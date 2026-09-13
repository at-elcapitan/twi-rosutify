from functools import wraps
import inspect

from google import genai

from ..configuration import configuration

def get_gemini_async_client(handler):
    sig = inspect.signature(handler)

    @wraps(handler)
    async def wrapper(*args, **kwargs):
        async with genai.Client(api_key=configuration["GOOGLEAI_API_KEY"]).aio as client:
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.arguments['gemini_client'] = client
            
            return await handler(*bound_args.args, **bound_args.kwargs)

    return wrapper