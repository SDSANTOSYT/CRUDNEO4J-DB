from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASS")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

constraints = [
    # Usuario
    "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:Usuario) REQUIRE u.id IS UNIQUE",
    "CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:Usuario) REQUIRE u.email IS UNIQUE",
    
    # Post
    "CREATE CONSTRAINT post_id_unique IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE",
    
    # Comentario
    "CREATE CONSTRAINT comment_id_unique IF NOT EXISTS FOR (c:Comentario) REQUIRE c.id IS UNIQUE"
]

with driver.session() as session:
    for query in constraints:
        session.run(query)
        print(f"✅ Constraint ejecutado: {query}")

print("🎯 Todas las constraints fueron aplicadas correctamente.")
driver.close()

