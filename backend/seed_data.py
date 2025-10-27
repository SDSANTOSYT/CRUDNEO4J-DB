from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
)

with driver.session() as session:
    # Limpiar base de datos completamente
    print("---Limpiando base de datos...")
    session.run("MATCH (n) DETACH DELETE n")
    
    # ==========================================
    # USUARIOS - Atributos: idu, nombre
    # ==========================================
    print("---Creando Usuarios...")
    session.run("CREATE (:User {idu:'u1', nombre:'Sergio'})")
    session.run("CREATE (:User {idu:'u2', nombre:'Ana'})")
    session.run("CREATE (:User {idu:'u3', nombre:'Carlos'})")
    
    # ==========================================
    # POSTS - Atributos: idp, contenido
    # ==========================================
    print("---Creando Posts...")
    session.run("CREATE (:Post {idp:'p1', contenido:'Mi primer post sobre Neo4j'})")
    session.run("CREATE (:Post {idp:'p2', contenido:'Aprendiendo bases de datos grafos'})")
    
    # ==========================================
    # COMENTARIOS - Atributos: consec, fechorCom, likeNotLike, fechorAut, contenido
    # ==========================================
    print("---Creando Comentarios...")
    session.run("""
        CREATE (:Comment {
            consec:'c1', 
            fechorCom:'26/10/2025', 
            likeNotLike:'megusta', 
            fechorAut:'20/02/2023', 
            contenido:'Excelente explicación!'
        })
    """)
    session.run("""
        CREATE (:Comment {
            consec:'c2', 
            fechorCom:'04/01/2023', 
            likeNotLike:'nomegusta', 
            fechorAut:'24/12/2023', 
            contenido:'No me convenció del todo'
        })
    """)
    session.run("""
        CREATE (:Comment {
            consec:'c3', 
            fechorCom:'15/03/2024', 
            likeNotLike:'megusta', 
            fechorAut:'10/03/2024', 
            contenido:'Muy útil, gracias!'
        })
    """)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    print("---Creando Relaciones...")
    
    # Relación PUBLICA: Usuario -> Post
    session.run("MATCH (u:User {idu:'u1'}), (p:Post {idp:'p1'}) CREATE (u)-[:PUBLICA]->(p)")
    session.run("MATCH (u:User {idu:'u2'}), (p:Post {idp:'p2'}) CREATE (u)-[:PUBLICA]->(p)")
    
    # Relación HACE: Usuario -> Comentario
    session.run("MATCH (u:User {idu:'u2'}), (c:Comment {consec:'c1'}) CREATE (u)-[:HACE]->(c)")
    session.run("MATCH (u:User {idu:'u3'}), (c:Comment {consec:'c2'}) CREATE (u)-[:HACE]->(c)")
    session.run("MATCH (u:User {idu:'u1'}), (c:Comment {consec:'c3'}) CREATE (u)-[:HACE]->(c)")
    
    # Relación TIENE: Post -> Comentario
    session.run("MATCH (p:Post {idp:'p1'}), (c:Comment {consec:'c1'}) CREATE (p)-[:TIENE]->(c)")
    session.run("MATCH (p:Post {idp:'p1'}), (c:Comment {consec:'c2'}) CREATE (p)-[:TIENE]->(c)")
    session.run("MATCH (p:Post {idp:'p2'}), (c:Comment {consec:'c3'}) CREATE (p)-[:TIENE]->(c)")
    
    # Relación AUTORIZA: Usuario -> Comentario
    session.run("MATCH (u:User {idu:'u1'}), (c:Comment {consec:'c1'}) CREATE (u)-[:AUTORIZA]->(c)")
    session.run("MATCH (u:User {idu:'u1'}), (c:Comment {consec:'c2'}) CREATE (u)-[:AUTORIZA]->(c)")
    session.run("MATCH (u:User {idu:'u2'}), (c:Comment {consec:'c3'}) CREATE (u)-[:AUTORIZA]->(c)")

print("\n---Seed completado exitosamente!")
print("=" * 50)
print("---DATOS CREADOS:")
print("  - 3 Usuarios (idu, nombre)")
print("  - 2 Posts (idp, contenido)")
print("  - 3 Comentarios (consec, fechorCom, likeNotLike, fechorAut, contenido)")
print("  - Relaciones: PUBLICA, HACE, TIENE, AUTORIZA")
print("=" * 50)