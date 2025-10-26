from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import datetime

load_dotenv()  # Lee variables del archivo .env

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASS")

app = Flask(__name__)
CORS(app)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def node_label_for_type(type_name: str):
    mapping = {"user": "User", "post": "Post", "comment": "Comment"}
    return mapping.get(type_name.lower())

@app.route("/users", methods=["GET"])
def get_users():
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u { .* } AS user")
        return jsonify([r["user"] for r in result]), 200

@app.route("/posts", methods=["GET"])
def get_posts():
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Post)
            OPTIONAL MATCH (a:User)-[:CREATED]->(p)
            RETURN p { .*, authorId: coalesce(a.id, null) } AS post
        """)
        return jsonify([r["post"] for r in result]), 200

@app.route("/comments", methods=["GET"])
def get_comments():
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Comment)
            OPTIONAL MATCH (a:User)-[:WROTE]->(c)
            OPTIONAL MATCH (p:Post)-[:HAS_COMMENT]->(c)
            RETURN c { .*, authorId: coalesce(a.id, null), postId: coalesce(p.id, null) } AS comment
        """)
        return jsonify([r["comment"] for r in result]), 200

@app.route("/node/<type_name>", methods=["POST"])
def create_node(type_name):
    body = request.get_json()
    label = node_label_for_type(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400

    node_id = body.get("id")
    if not node_id:
        return jsonify({"error": "Falta 'id'"}), 400

    with driver.session() as session:
        cypher = f"MERGE (n:{label} {{ id: $id }}) SET n += $props RETURN n {{ .* }} as node"
        result = session.run(cypher, id=node_id, props=body)
        node = result.single()["node"]
    return jsonify(node), 201

@app.route("/node/<type_name>/<node_id>", methods=["PUT"])
def update_node(type_name, node_id):
    body = request.get_json()
    label = node_label_for_type(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400

    with driver.session() as session:
        cypher = f"MATCH (n:{label} {{ id: $id }}) SET n += $props RETURN n {{ .* }} as node"
        result = session.run(cypher, id=node_id, props=body)
        record = result.single()
        if not record:
            return jsonify({"error": "Nodo no encontrado"}), 404
    return jsonify(record["node"]), 200

@app.route("/node/<type_name>/<node_id>", methods=["DELETE"])
def delete_node(type_name, node_id):
    label = node_label_for_type(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400

    with driver.session() as session:
        res = session.run(f"MATCH (n:{label} {{ id: $id }}) DETACH DELETE n RETURN 1", id=node_id)
        if not res.single():
            return jsonify({"error": "Nodo no encontrado"}), 404
    return jsonify({"deleted": True}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.datetime.utcnow().isoformat() + "Z"}), 200

if __name__ == "__main__":
    app.run(debug=True)
