from app.services.gemini_service import GeminiService


class ChatService:

    def __init__(self):
        self.gemini_service = GeminiService()

    def get_response(self, message: str):

        return self.gemini_service.generate_response(message)
