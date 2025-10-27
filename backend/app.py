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

def node_id_label_for_type(type_name: str):
    mapping = {"user": "idu", "post": "idp", "comment": "consec"}
    return mapping.get(type_name.lower())

@app.route("/users", methods=["GET"])
def get_users():
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u { .* } AS user")
        users = [r["user"] for r in result]
        print(f"Users found: {users}")  # Debug
        return jsonify(users), 200

@app.route("/posts", methods=["GET"])
def get_posts():
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Post)
            OPTIONAL MATCH (a:User)-[:PUBLICA]->(p)
            RETURN p { .*, idu: coalesce(a.idu, null) } AS post
        """)
        posts = [r["post"] for r in result]
        print(f"Posts found: {posts}")  # Debug
        return jsonify(posts), 200

@app.route("/comments", methods=["GET"])
def get_comments():
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Comment)
            OPTIONAL MATCH (a:User)-[:HACE]->(c)
            OPTIONAL MATCH (p:Post)-[:TIENE]->(c)
            OPTIONAL MATCH (au:User)-[:AUTORIZA]->(c)
            RETURN c { .*, idu: coalesce(a.idu, null), idp: coalesce(p.idp, null), idau: coalesce(au.idu, null) } AS comment
        """)
        comments = [r["comment"] for r in result]
        print(f"Comments found: {comments}")  # Debug
        return jsonify(comments), 200

@app.route("/node/<type_name>", methods=["POST"])
def create_node(type_name):
    body = request.get_json()
    label = node_label_for_type(type_name)
    node_id_label = node_id_label_for_type(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400
    if not node_id_label:
        return jsonify({"error": "Tipo no válido"}), 400

    node_id = body.get(f"{node_id_label}")
    if not node_id:
        return jsonify({"error": "Falta 'id'"}), 400
    
    with driver.session() as session:
        cypher = f"""
        MERGE (n:{label} {{ {node_id_label}: $id }})
        SET n += $props
        """
        if label == "Post":
           cypher += """
           WITH n
           MERGE (u:User {idu: $idu})
           MERGE (u)-[:PUBLICA]->(n)
           """
        elif label == "Comment":
            cypher += """
            WITH n
            MERGE (u:User {idu: $idu})
            MERGE (aut:User {idu: $idau})
            MERGE (p:Post {idp: $idp})
            MERGE (p)-[:TIENE]->(n)
            MERGE (u)-[:HACE]->(n)
            MERGE (aut)-[:AUTORIZA]->(n)
            """
        cypher += "RETURN n { .* } AS node"
        
        result = session.run(
            cypher,
            id=node_id,
            props=body,
            idu=body.get("idu"),
            idp=body.get("idp"),
            idau=body.get("idau")
    )

        record = result.single()
        if record is None:
            print("No se devolvió ningún resultado del query:")
            print(cypher)
            return jsonify({"error": "No se pudo crear el nodo o no se encontró el usuario/post"}), 400

        node = record["node"]
        return jsonify(node), 201


@app.route("/node/<type_name>/<node_id>", methods=["PUT"])
def update_node(type_name, node_id):
    body = request.get_json()
    label = node_label_for_type(type_name)
    node_id_label = node_id_label_for_type(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400
    if not node_id_label:
        return jsonify({"error": "Tipo no válido"}), 400

    with driver.session() as session:
        cypher = f"MATCH (n:{label} {{ {node_id_label}: $id }}) SET n += $props RETURN n {{ .* }} as node"
        result = session.run(cypher, id=node_id, props=body)
        record = result.single()
        if not record:
            return jsonify({"error": "Nodo no encontrado"}), 404
    return jsonify(record["node"]), 200

@app.route("/node/<type_name>/<node_id>", methods=["DELETE"])
def delete_node(type_name, node_id):
    label = node_label_for_type(type_name)
    node_id_label = node_id_label_for_type(type_name)
    if not label:
        return jsonify({"error": "Tipo no válido"}), 400
    if not node_id_label:
        return jsonify({"error": "Tipo no válido"}), 400

    with driver.session() as session:
        res = session.run(f"MATCH (n:{label} {{ {node_id_label}: $id }}) DETACH DELETE n RETURN 1", id=node_id)
        if not res.single():
            return jsonify({"error": "Nodo no encontrado"}), 404
    return jsonify({"deleted": True}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.datetime.utcnow().isoformat() + "Z"}), 200

# Endpoint de debug para verificar la base de datos
@app.route("/debug/all", methods=["GET"])
def debug_all():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN labels(n) as labels, n { .* } as node LIMIT 20")
        nodes = [{"labels": r["labels"], "node": r["node"]} for r in result]
        return jsonify(nodes), 200

# INCISO C: Consulta 1 - Usuario que ha hecho un USUARIO mostrando como submenú
@app.route("/consulta/posts-usuario/<user_id>", methods=["GET"])
def get_posts_usuario(user_id):
    """
    Consulta 1: Muestra que USUARIO ha hecho un POST como submenú
    Retorna los posts de un usuario específico
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User {idu: $user_id})-[:PUBLICA]->(p:Post)
            RETURN u.idu AS idu,
                   u.nombre AS nombreUsuario,
                   p.idp AS idp,
                   p.contenido AS contenido
            ORDER BY p.idp
        """, user_id=user_id)
        
        posts = [{
            "idu": r["idu"],
            "nombreUsuario": r["nombreUsuario"],
            "idp": r["idp"],
            "contenido": r["contenido"]
        } for r in result]
        
        print(f"✅ Posts del usuario {user_id}: {posts}")
        return jsonify(posts), 200

# INCISO C: Consulta 2 - Comentarios de un POST con info del usuario
@app.route("/consulta/comentarios-post/<post_id>", methods=["GET"])
def get_comentarios_post(post_id):
    """
    Retorna los comentarios de un POST específico mostrando:
    - Fecha-hora de creación del comentario (fechorCom)
    - Fecha-hora de autorización (fechorAut)
    - Usuario que hizo el comentario
    - Si fue megusta o nomegusta
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Post {idp: $post_id})-[:TIENE]->(c:Comment)
            MATCH (u:User)-[:HACE]->(c)
            RETURN c.fechorCom AS fechorCom,
                   c.fechorAut AS fechorAut,
                   u.nombre AS usuario,
                   c.likeNotLike AS likeNotLike,
                   c.contenido AS contenido,
                   c.consec AS consec
            ORDER BY c.fechorCom DESC
        """, post_id=post_id)
        
        comentarios = [{
            "consec": r["consec"],
            "fechorCom": r["fechorCom"],
            "fechorAut": r["fechorAut"],
            "usuario": r["usuario"],
            "likeNotLike": r["likeNotLike"],
            "contenido": r["contenido"]
        } for r in result]
        
        print(f"✅ Comentarios del post {post_id}: {comentarios}")
        return jsonify(comentarios), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)