from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

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
        print(f"Users found: {users}")
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
        print(f"Posts found: {posts}")
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
        print(f"Comments found: {comments}")
        return jsonify(comments), 200

@app.route("/node/<type_name>", methods=["POST"])
def create_node(type_name):
    body = request.get_json()
    label = node_label_for_type(type_name)
    node_id_label = node_id_label_for_type(type_name)

    if not label or not node_id_label:
        return jsonify({"error": "Tipo no válido"}), 400

    if body.get(node_id_label) is None:
        return jsonify({"error": "Falta el ID del nodo"}), 400

    node_id = body[node_id_label]

    with driver.session() as session:
        # Verificar si el ID ya existe
        exists = session.run(
            f"MATCH (n:{label} {{ {node_id_label}: $id }}) RETURN n LIMIT 1",
            id=node_id
        ).single()

        if exists:
            return jsonify({"error": f"El ID '{node_id}' ya está en uso"}), 409

        # Construir query según el tipo
        try:
            if label == "User":
                # Usuario simple, sin dependencias
                cypher = "CREATE (n:User) SET n += $props RETURN n { .* } AS node"
                result = session.run(cypher, props=body)
                
            elif label == "Post":
                # Post requiere que exista el usuario
                idu = body.get("idu")
                if not idu:
                    return jsonify({"error": "Falta 'idu' (usuario que publica)"}), 400
                
                cypher = """
                MATCH (u:User {idu: $idu})
                CREATE (n:Post)
                SET n += $props
                CREATE (u)-[:PUBLICA]->(n)
                RETURN n { .* } AS node
                """
                result = session.run(cypher, props=body, idu=idu)
                
            elif label == "Comment":
                # Comentario requiere usuario, autorizador y post
                idu = body.get("idu")
                idau = body.get("idau")
                idp = body.get("idp")
                
                if not all([idu, idau, idp]):
                    return jsonify({"error": "Faltan 'idu', 'idau' o 'idp'"}), 400
                
                like = body.get("likeNotLike")
                if like not in ["megusta", "nomegusta"]:
                    return jsonify({"error": "likeNotLike debe ser 'megusta' o 'nomegusta'"}), 400
                
                cypher = """
                MATCH (u:User {idu: $idu})
                MATCH (aut:User {idu: $idau})
                MATCH (p:Post {idp: $idp})
                CREATE (n:Comment)
                SET n += $props
                CREATE (p)-[:TIENE]->(n)
                CREATE (u)-[:HACE]->(n)
                CREATE (aut)-[:AUTORIZA]->(n)
                RETURN n { .* } AS node
                """
                result = session.run(cypher, props=body, idu=idu, idau=idau, idp=idp)

            record = result.single()
            if not record:
                return jsonify({"error": "No se pudo crear el nodo"}), 400

            return jsonify(record["node"]), 201

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error al crear {label}: {error_msg}")
            
            # Mensajes de error más amigables
            if "User" in error_msg and "idu" in error_msg:
                return jsonify({"error": f"El usuario con idu '{idu}' no existe"}), 404
            elif "Post" in error_msg and "idp" in error_msg:
                return jsonify({"error": f"El post con idp '{idp}' no existe"}), 404
            else:
                return jsonify({"error": f"Error al crear: {error_msg}"}), 400

@app.route("/node/<type_name>/<node_id>", methods=["PUT"])
def update_node(type_name, node_id):
    body = request.get_json()
    label = node_label_for_type(type_name)
    node_id_label = node_id_label_for_type(type_name)
    
    if not label or not node_id_label:
        return jsonify({"error": "Tipo no válido"}), 400

    with driver.session() as session:
        try:
            # Actualizar relaciones si cambiaron
            if label == "Post":
                idu = body.get("idu")
                if idu:
                    # Verificar que el nuevo usuario existe
                    user_exists = session.run(
                        "MATCH (u:User {idu: $idu}) RETURN u", idu=idu
                    ).single()
                    
                    if not user_exists:
                        return jsonify({"error": f"Usuario con idu '{idu}' no existe"}), 404
                    
                    # Reemplazar relación
                    session.run(f"""
                        MATCH (p:{label} {{{node_id_label}: $id}})
                        OPTIONAL MATCH (oldU:User)-[r:PUBLICA]->(p)
                        DELETE r
                        WITH p
                        MATCH (newU:User {{idu: $idu}})
                        CREATE (newU)-[:PUBLICA]->(p)
                    """, id=node_id, idu=idu)

            elif label == "Comment":
                idu = body.get("idu")
                idau = body.get("idau")
                idp = body.get("idp")
                
                if all([idu, idau, idp]):
                    # Verificar que existen
                    check = session.run("""
                        MATCH (u:User {idu: $idu})
                        MATCH (a:User {idu: $idau})
                        MATCH (p:Post {idp: $idp})
                        RETURN u, a, p
                    """, idu=idu, idau=idau, idp=idp).single()
                    
                    if not check:
                        return jsonify({"error": "Usuario o post no existen"}), 404
                    
                    # Reemplazar relaciones
                    session.run(f"""
                        MATCH (c:{label} {{{node_id_label}: $id}})
                        OPTIONAL MATCH (u1)-[r1:HACE]->(c)
                        OPTIONAL MATCH (u2)-[r2:AUTORIZA]->(c)
                        OPTIONAL MATCH (p)-[r3:TIENE]->(c)
                        DELETE r1, r2, r3
                        WITH c
                        MATCH (u:User {{idu: $idu}})
                        MATCH (a:User {{idu: $idau}})
                        MATCH (p:Post {{idp: $idp}})
                        CREATE (u)-[:HACE]->(c)
                        CREATE (a)-[:AUTORIZA]->(c)
                        CREATE (p)-[:TIENE]->(c)
                    """, id=node_id, idu=idu, idau=idau, idp=idp)

            # Actualizar propiedades del nodo
            update_query = f"""
            MATCH (n:{label} {{{node_id_label}: $id}})
            SET n += $props
            RETURN n {{ .* }} AS node
            """
            record = session.run(update_query, id=node_id, props=body).single()

            if not record:
                return jsonify({"error": "Nodo no encontrado"}), 404

            return jsonify(record["node"]), 200

        except Exception as e:
            print(f"❌ Error al actualizar: {str(e)}")
            return jsonify({"error": f"Error al actualizar: {str(e)}"}), 400

@app.route("/node/<type_name>/<node_id>", methods=["DELETE"])
def delete_node(type_name, node_id):
    label = node_label_for_type(type_name)
    node_id_label = node_id_label_for_type(type_name)
    
    if not label or not node_id_label:
        return jsonify({"error": "Tipo no válido"}), 400

    with driver.session() as session:
        res = session.run(
            f"MATCH (n:{label} {{ {node_id_label}: $id }}) DETACH DELETE n RETURN 1",
            id=node_id
        )
        if not res.single():
            return jsonify({"error": "Nodo no encontrado"}), 404
            
    return jsonify({"deleted": True}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}), 200

@app.route("/debug/all", methods=["GET"])
def debug_all():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN labels(n) as labels, n { .* } as node LIMIT 20")
        nodes = [{"labels": r["labels"], "node": r["node"]} for r in result]
        return jsonify(nodes), 200

@app.route("/consulta/posts-usuario/<user_id>", methods=["GET"])
def get_posts_usuario(user_id):
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

@app.route("/consulta/comentarios-post/<post_id>", methods=["GET"])
def get_comentarios_post(post_id):
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
    app.run(host="0.0.0.0", port=5000, debug=True)