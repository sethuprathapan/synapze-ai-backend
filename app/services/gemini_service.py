from google.genai import errors
from google import genai

from app.core.config import settings


class GeminiService:

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate_response(self, prompt: str):

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            return response.text

        except errors.ServerError as e:
            print(f"Gemini server error: {e}")
            return "AI service is temporarily unavailable. Please try again later."

        except Exception as e:
            print(f"Unexpected error: {e}")
            return "Something went wrong."
