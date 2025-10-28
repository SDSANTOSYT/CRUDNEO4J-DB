from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import uuid
import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASS")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# -----------------------------------------
# MANEJO GLOBAL DE ERRORES JSON
# -----------------------------------------
@app.errorhandler(Exception)
def error_handler(e):
    return jsonify({"error": str(e)}), 500


# -----------------------------------------
# UTILIDADES
# -----------------------------------------
def generate_id():
    return str(uuid.uuid4())


def valid_label(type_name):
    mapping = {"user": "User", "post": "Post", "comment": "Comment"}
    return mapping.get(type_name.lower())


# -----------------------------------------
# GET PRINCIPALES
# -----------------------------------------
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
        OPTIONAL MATCH (a:User)-[:PUBLICA]->(p)
        RETURN p { .*, authorId: a.id } AS post
        """)
        return jsonify([r["post"] for r in result]), 200


@app.route("/comments", methods=["GET"])
def get_comments():
    with driver.session() as session:
        result = session.run("""
        MATCH (c:Comment)
        OPTIONAL MATCH (u:User)-[:HACE]->(c)
        OPTIONAL MATCH (p:Post)-[:TIENE]->(c)
        RETURN c { .*, authorId: u.id, postId: p.id } AS comment
        """)
        return jsonify([r["comment"] for r in result]), 200


# -----------------------------------------
# CREAR NODOS + RELACIONES
# -----------------------------------------
@app.route("/node/<type_name>", methods=["POST"])
def create_node(type_name):
    label = valid_label(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400

    body = request.get_json()
    node_id = body.get("id") or generate_id()  # ID automático si no lo envían
    body["id"] = node_id

    with driver.session() as session:
        # Crear nodo
        cypher = f"CREATE (n:{label} $props) RETURN n {{ .* }} as node"
        result = session.run(cypher, props=body)
        node = result.single()["node"]

        # Crear relaciones si aplica
        if label == "Post":
            if "authorId" in body:
                session.run("""
                MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                MERGE (u)-[:PUBLICA]->(p)
                """, uid=body["authorId"], pid=node_id)

        if label == "Comment":
            if "authorId" in body and "postId" in body:
                session.run("""
                MATCH (u:User {id: $uid}), (c:Comment {id: $cid}), (p:Post {id: $pid})
                MERGE (u)-[:HACE]->(c)
                MERGE (p)-[:TIENE]->(c)
                """, uid=body["authorId"], cid=node_id, pid=body["postId"])

    return jsonify(node), 201


# -----------------------------------------
# ACTUALIZAR NODOS
# -----------------------------------------
@app.route("/node/<type_name>/<node_id>", methods=["PUT"])
def update_node(type_name, node_id):
    label = valid_label(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400

    body = request.get_json()

    with driver.session() as session:
        q = f"MATCH (n:{label} {{ id: $id }}) SET n += $props RETURN n {{ .* }} as node"
        res = session.run(q, id=node_id, props=body).single()
        if not res:
            return jsonify({"error": "Nodo no encontrado"}), 404

        return jsonify(res["node"]), 200


# -----------------------------------------
# ELIMINAR NODOS
# -----------------------------------------
@app.route("/node/<type_name>/<node_id>", methods=["DELETE"])
def delete_node(type_name, node_id):
    label = valid_label(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400

    with driver.session() as session:
        res = session.run(f"MATCH (n:{label} {{ id: $id }}) DETACH DELETE n RETURN 1", id=node_id).single()
        if not res:
            return jsonify({"error": "Nodo no encontrado"}), 404

    return jsonify({"deleted": True}), 200


# -----------------------------------------
# HEALTH CHECK
# -----------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.datetime.utcnow().isoformat()}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
