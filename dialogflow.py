from google.cloud import dialogflow
import uuid
from dotenv import load_dotenv

load_dotenv()

def detect_intent(text):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path("lifeline-clone", str(uuid.uuid4()))

    text_input = dialogflow.TextInput(text=text, language_code="en-GB")

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.intent.display_name