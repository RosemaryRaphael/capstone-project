import os
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "retrieval",
        "vector_db": "chroma",
        "db_config": {"path": "./chroma_db"},
        "collection_name": "ag2-docs",
        "n_results": 5,
        "distance_threshold": 0.7,
        "docs_path": None,
    },
    code_execution_config=False,
)

print("ChromaDB-based RAG proxy agent initialized successfully.")
