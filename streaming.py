import asyncio
from typing import AsyncGenerator, Any
from openai.types.beta import AssistantStreamEvent


class StreamProcessor:
    @staticmethod
    async def process_stream(stream) -> AsyncGenerator[str, None]:
        async for event in stream:
            if event.event == 'thread.message.delta':
                for content in event.data.delta.content or []:
                    if content.type == 'text':
                        if hasattr(content.text, 'value'):
                            yield content.text.value