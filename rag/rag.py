import os
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "retrieval",
        "vector_db": "mongodb",
        "db_config": {
            "connection_string": os.getenv("MONGODB_URI"),
            "database_name": "autogen",
            "collection_name": "ag2-docs",
        },

        "embedding_model": "text-embedding-3-small",
        "n_results": 5,
        "distance_threshold": 0.7,
    },

    code_execution_config=False,
)

print("RAG proxy agent initialized")