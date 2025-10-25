from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
)

with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")  # limpiar
    session.run("CREATE (:User {id:'u1', name:'Sergio', email:'sergio@example.com'})")
    session.run("CREATE (:User {id:'u2', name:'Ana', email:'ana@example.com'})")
    session.run("CREATE (:Post {id:'p1', title:'Primer post', body:'Hola mundo'})")
    session.run("""
        MATCH (u:User {id:'u1'}), (p:Post {id:'p1'})
        CREATE (u)-[:CREATED]->(p)
    """)
    session.run("CREATE (:Comment {id:'c1', body:'Excelente post!'})")
    session.run("""
        MATCH (u:User {id:'u2'}), (p:Post {id:'p1'}), (c:Comment {id:'c1'})
        CREATE (u)-[:WROTE]->(c)
        CREATE (p)-[:HAS_COMMENT]->(c)
    """)
print("Seed completo.")
