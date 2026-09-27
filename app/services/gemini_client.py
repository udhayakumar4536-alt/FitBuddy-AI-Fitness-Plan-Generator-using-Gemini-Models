from google import genai

from google.genai import types

from ..config import settings


class GeminiService:

    def __init__(self):

        self.client = None

        if settings.gemini_api_key:

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )


    @property
    def available(self):

        return self.client is not None


    def generate(
        self,
        model,
        prompt,
        max_output_tokens=3000
    ):

        if not self.client:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )


        response = self.client.models.generate_content(

            model=model,

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.7,

                max_output_tokens=max_output_tokens
            )
        )


        text = (
            response.text or ""
        ).strip()


        if not text:

            raise RuntimeError(
                "Gemini returned empty response."
            )


        return text


gemini_service = GeminiService()