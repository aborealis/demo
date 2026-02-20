from typing import AsyncGenerator, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logging_setup import setup_logging
from dependencies.chat_websocket import MultipleConnectionManager
from db.session import engine
from db.init_db import init_database
from routes import user_auth, user_docs_mgmt, user_self_mgmt, chat
from haystack_pipelines import initializator as __  # noqa: F401

DESCRIPTION = """
Demo backend service for the RAG portfolio project.
"""

tags_metadata = [
    {
        "name": "Manage Documents",
        "description": "Upload, update, search, and delete indexed documents.",
    },
]

origins = [
    "http://localhost:8001",
    "http://10.0.0.1:8001",
    "https://myfrontend.com",
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    init_database()
    app.state.connection_manager = MultipleConnectionManager()
    yield
    engine.dispose()


app = FastAPI(
    title="RAG Backend",
    description=DESCRIPTION,
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_auth.router, prefix="/api/v1")
app.include_router(user_self_mgmt.router, prefix="/api/v1")
app.include_router(user_docs_mgmt.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
setup_logging()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
