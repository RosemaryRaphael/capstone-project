import asyncio
from openai import RateLimitError


async def safe_llm_create(model_client, messages, ctx, max_retries=3):
    """Safely call LLM with retry logic for rate limits."""
    for attempt in range(max_retries):
        try:
            return await model_client.create(
                messages=messages,
                cancellation_token=ctx.cancellation_token,
            )
        except RateLimitError:
            print(f"Rate limit hit, retrying in 60s... (Attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(60)
        except Exception as e:
            print(f"LLM Error: {e}")
            raise
    
    raise Exception("Max retries exceeded for LLM call")