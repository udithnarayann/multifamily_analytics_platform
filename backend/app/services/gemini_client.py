from collections.abc import Iterable
from dataclasses import dataclass

from app.core.errors import AIServiceError, ConfigurationError


@dataclass(frozen=True)
class GeminiTextResponse:
    text: str
    model_name: str
    model_version: str | None = None


class GeminiClient:
    def __init__(self, *, api_key: str, primary_model: str, fallback_model: str) -> None:
        self.api_key = api_key.strip()
        self.primary_model = primary_model
        self.fallback_model = fallback_model

    def _models_to_try(self) -> Iterable[str]:
        yield self.primary_model
        if self.fallback_model != self.primary_model:
            yield self.fallback_model

    def generate_json(self, prompt: str) -> GeminiTextResponse:
        if not self.api_key:
            raise ConfigurationError("GEMINI_API_KEY is required to generate AI risk reports")

        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:  # pragma: no cover - dependency issue in deployed env
            raise ConfigurationError("google-genai is not installed") from exc

        client = genai.Client(api_key=self.api_key)
        failures: list[str] = []
        for model_name in self._models_to_try():
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                text = getattr(response, "text", None)
                if not text:
                    raise AIServiceError("Gemini response did not include text")
                model_version = getattr(response, "model_version", None)
                return GeminiTextResponse(
                    text=text, model_name=model_name, model_version=model_version
                )
            except Exception as exc:  # noqa: BLE001 - fallback should catch SDK/API failures
                failures.append(f"{model_name}: {exc}")
                continue

        raise AIServiceError(
            "Gemini request failed for all configured models: " + "; ".join(failures)
        )
