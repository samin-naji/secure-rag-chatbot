from openai import OpenAI, OpenAIError, APITimeoutError

from app.core.config import settings


class LLMServiceError(Exception):
    """Raised when the LLM provider request fails."""
    pass


class LLMTimeoutError(LLMServiceError):
    """Raised when the LLM provider times out."""
    pass


def generate_answer(messages: list[dict]) -> str:
    """
    Send messages to GapGPT and return the answer.
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

        if not response.choices:
            raise LLMServiceError(
                "The LLM returned an invalid response."
            )

        answer = response.choices[0].message.content

        if not isinstance(answer, str) or not answer.strip():
            raise LLMServiceError(
                "The LLM returned an empty response."
            )

        return answer.strip()

    except APITimeoutError as exc:
        raise LLMTimeoutError(
            "LLM request timed out."
        ) from exc

    except LLMServiceError:
        raise

    except OpenAIError as exc:
        raise LLMServiceError(
            "Failed to communicate with GapGPT."
        ) from exc

    except (AttributeError, IndexError, TypeError) as exc:
        raise LLMServiceError(
            "The LLM returned an invalid response."
        ) from exc
