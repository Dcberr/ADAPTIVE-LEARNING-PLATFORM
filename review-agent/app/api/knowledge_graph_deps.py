from fastapi import Request
from neo4j import Driver

from app.services.knowledge_graph_repository import KnowledgeGraphRepository


def get_neo4j_driver(request: Request) -> Driver:
    driver = getattr(request.app.state, "neo4j_driver", None)
    if driver is None:
        raise RuntimeError("Neo4j driver is not initialized on application startup.")
    return driver


def get_knowledge_graph_repository(request: Request) -> KnowledgeGraphRepository:
    return KnowledgeGraphRepository(driver=get_neo4j_driver(request))
