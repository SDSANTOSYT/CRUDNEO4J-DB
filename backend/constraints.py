from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
)

with driver.session() as session:
    session.run("""
                CREATE CONSTRAINT user_id_unique IF NOT EXISTS
                FOR (u:User)
                REQUIRE u.idu IS UNIQUE;
                """)
    session.run("""
                CREATE CONSTRAINT post_id_unique IF NOT EXISTS
                FOR (p:Post)
                REQUIRE p.idp IS UNIQUE;
                """)