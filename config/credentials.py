import os
from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_API_BASE")
model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print("Initializing model client")
model_client = AzureOpenAIChatCompletionClient(
    azure_endpoint=azure_endpoint,
    model=model,
    azure_deployment=model,
    api_version=api_version,
    api_key=api_key,
)