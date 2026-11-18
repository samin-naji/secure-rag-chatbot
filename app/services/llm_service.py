from openai import OpenAI, OpenAIError

from app.core.config import settings


class LLMServiceError(Exception):
    """Raised when the LLM provider request fails."""
    pass


def generate_answer(
    messages: list[dict],
) -> str:
    """
    Send messages to GapGPT and return the assistant response.
    """

    try:
        client = OpenAI(
            api_key=settings.gapgpt_api_key,
            base_url=settings.gapgpt_base_url,
            timeout=60.0,
            max_retries=1
        )

        response = client.chat.completions.create(
            model=settings.gapgpt_model,
            messages=messages,
            temperature=0.2,
            max_tokens=200
        )

        answer = response.choices[0].message.content

        if not answer:
            raise LLMServiceError(
                "The LLM returned an empty response."
            )

        return answer

    except LLMServiceError:
        raise

    except OpenAIError as exc:
        raise LLMServiceError(
            "Failed to communicate with GapGPT."
        ) from exc
