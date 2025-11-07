from autogen_core import (MessageContext,RoutedAgent,TopicId,message_handler,type_subscription,)
from autogen_core.models import SystemMessage
from autogen_core.memory import MemoryContent, MemoryMimeType
from messages.shared import Message
from utils.memory import global_memory

# Agent type identifiers
document_retriever = "DocumentRetrieverAgent"
response_generator = "ResponseAgent"


@type_subscription(topic_type=document_retriever)
class DocumentRetrieverAgent(RoutedAgent):
    def __init__(self, model_client, rag_agent):
        super().__init__("Document Retriever Agent")
        self.system_message = SystemMessage(
            content="You are an **HR Policy Retrieval Agent**."
                    "Fetch information strictly and only from the HR KB. "
                    "If no relevant content exists, respond exactly with 'No info found'. "
                    "Do not generate, assume or include any information outside the data source."
        )
        self.model_client = model_client
        self.rag_agent = rag_agent

    @message_handler
    async def handle_retrieval(self, message: Message, ctx: MessageContext) -> None:
        query = message.content.strip()
        print(f"\nDocumentRetriever: Retrieving docs for: {query}")
        
        self.rag_agent.retrieve_docs(problem=query)
        retrieved_docs = self.rag_agent._results

        filtered_docs = []
        for doc in retrieved_docs:
            if isinstance(doc, dict):
                content = doc.get("content", "")
                score = doc.get("score", None)
            else:
                content = str(doc)
                score = None
            
            if content.strip():
                filtered_docs.append(content)
                if score is not None:
                    print(f"Document with score: {score:.3f}")

        if not filtered_docs:
            print("No relevant documents found.")
            await self.publish_message(
                Message(content="No relevant context found."),
                topic_id=TopicId(response_generator, source=self.id.key)
            )
            return

        context = "\n\n".join([f"Document {i+1}:\n{d}" for i, d in enumerate(filtered_docs[:5])])
        print(f"Retrieved {len(filtered_docs)} relevant docs.")
        
        await global_memory.add(
            MemoryContent(content=f"Context: {context}", mime_type=MemoryMimeType.TEXT)
        )
        
        await self.publish_message(
            Message(content=f"{query}\n\nCONTEXT:\n{context}"),
            topic_id=TopicId(response_generator, source=self.id.key)
        )
        print(f"Published to {response_generator}")