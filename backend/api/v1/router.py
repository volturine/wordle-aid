"""
API v1 Router - Aggregates all module routes
"""

from fastapi import APIRouter

from modules.word_definition import routes as word_definition_routes
from modules.filter import routes as filter_routes

api_router = APIRouter(prefix="/api")

api_router.include_router(word_definition_routes.router, prefix="/word-definition")
api_router.include_router(filter_routes.router, prefix="/filter")
