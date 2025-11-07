import asyncio
from autogen_core import SingleThreadedAgentRuntime, TopicId
from config.credentials import model_client
from rag.rag import ragproxyagent
from messages.shared import Message
from agents.query_rewriter import QueryRewriterAgent, query_rewriter
from agents.document_retriever import DocumentRetrieverAgent, document_retriever
from agents.response_agent import ResponseAgent, response_generator


async def process_query(runtime, query: str):
    """Process a single query through the agent pipeline."""
    print(f"Processing query: {query}")
    
    await runtime.publish_message(
        Message(content=query),
        topic_id=TopicId(query_rewriter, source="user")
    )
    
    # Agent pipeline complete
    await runtime.stop_when_idle()


async def main():
    """Main application entry point."""
    print("\nInitializing runtime")
    runtime = SingleThreadedAgentRuntime()

    print("Registering agents")
    
    await QueryRewriterAgent.register(
        runtime,
        type=query_rewriter,
        factory=lambda: QueryRewriterAgent(model_client)
    )
    print(f"Registered: {query_rewriter}")
    
    await DocumentRetrieverAgent.register(
        runtime,
        type=document_retriever,
        factory=lambda: DocumentRetrieverAgent(model_client, ragproxyagent)
    )
    print(f"Registered: {document_retriever}")
    
    await ResponseAgent.register(
        runtime,
        type=response_generator,
        factory=lambda: ResponseAgent(model_client)
    )
    print(f"Registered: {response_generator}")

    print("\nStarting runtime")

    runtime.start()
    
    print("Type your question or 'exit' to quit.\n")

    while True:
        try:
            query = input("Your question:").strip()
            
            if query.lower() in ["exit", "quit"]:
                print("\nThankyou")
                break
                
            if not query:
                continue
            
            await process_query(runtime, query)
            
            # Restart runtime for next query
            runtime.start()
            
        except KeyboardInterrupt:
            print("\n\nKeyboard Interrupted")
            break

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    await runtime.stop()    
    await model_client.close()    


if __name__ == "__main__":
    asyncio.run(main())