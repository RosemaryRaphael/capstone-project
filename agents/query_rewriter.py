from autogen_core import (MessageContext,RoutedAgent,TopicId,message_handler,type_subscription,)
from autogen_core.models import SystemMessage, UserMessage
from autogen_core.memory import MemoryContent, MemoryMimeType
from messages.shared import Message
from utils.retry import safe_llm_create
from utils.memory import global_memory

# Agent type identifiers
query_rewriter = "QueryRewriterAgent"
document_retriever = "DocumentRetrieverAgent"


@type_subscription(topic_type=query_rewriter)
class QueryRewriterAgent(RoutedAgent):
    def __init__(self, model_client):
        super().__init__("Query Rewriter Agent")
        self.system_message = SystemMessage(
            content="You are a **Query Rewriter Agent** specialized in HR-related queries."
                    "Rephrase the user's query clearly to improve document retrieval accuracy from HR policy documents."
                    "Preserve the original intent without adding extra information."
        )
        self.model_client = model_client

    @message_handler
    async def handle_query(self, message: Message, ctx: MessageContext) -> None:
        print(f"\nQueryRewriter: Processing query")
        prompt = f"User Query: {message.content}\nRewrite this for better retrieval clarity."
        
        llm_result = await safe_llm_create(
            self.model_client,
            [self.system_message, UserMessage(source='assistant', content=prompt)],
            ctx
        )
        
        rewritten = llm_result.content.strip()
        print(f"Rewritten Query: {rewritten}")
        
        await global_memory.add(
            MemoryContent(content=f"Rewritten: {rewritten}", mime_type=MemoryMimeType.TEXT)
        )
        
        await self.publish_message(
            Message(content=rewritten),
            topic_id=TopicId(document_retriever, source=self.id.key)
        )
        print(f"Published to {document_retriever}")