from autogen_core import (MessageContext,RoutedAgent,TopicId,message_handler,type_subscription,)
from autogen_core.models import SystemMessage, UserMessage
from autogen_core.memory import MemoryContent, MemoryMimeType
from messages.shared import Message
from utils.retry import safe_llm_create
from utils.memory import global_memory

# Agent type identifier
response_generator = "ResponseAgent"


@type_subscription(topic_type=response_generator)
class ResponseAgent(RoutedAgent):
    def __init__(self, model_client):
        super().__init__("Response Agent")
        self.system_message = SystemMessage(
            content="""You are a **Response Agent** for the HR Knowledge Assistant with STRICT retrieval-only constraints.

**CRITICAL RULES:**
- You must **only** respond with information retrieved from the HR Knowledge Base.  
- You must **never** generate, infer or assume answers based on your own reasoning or external knowledge.  
- If the KB does not provide sufficient information to fully answer the query, you are required to provide the fallback response, "Sorry, I don’t have information about that HR policy."  
- Always cite which document number you're referencing (e.g., "According to Document 1...").
- **Summarize** the final response clearly and professionally.

**RESPONSE FORMAT:**
- Use a concise and professional tone suitable for internal HR communication. 
- Organize the answer with short paragraphs or bullet points if needed.  
- Only include information that can be directly traced to the CONTEXT.
- If uncertain, acknowledge the limitation rather than guessing"""
)
        self.model_client = model_client

    @message_handler
    async def handle_response(self, message: Message, ctx: MessageContext) -> None:
        print(f"\nResponseAgent: Generating final answer...")
        
        llm_result = await safe_llm_create(
            self.model_client,
            [self.system_message, UserMessage(source='assistant', content=message.content)],
            ctx
        )
        
        response = llm_result.content.strip()
        
        await global_memory.add(
            MemoryContent(content=f"Response: {response}", mime_type=MemoryMimeType.TEXT)
        )
        
        print(f"FINAL RESPONSE:")
        print(f"{response}")
