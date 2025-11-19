import os
import signal

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

from backend.conversation_state import ConversationState
from backend.refund_engine import process_refund
from backend.artifact_logger import save_decision_log, save_receipt, save_transcript

# Globals
state = ConversationState()
session_transcript = []
decision_done = False
conversation = None


def main():
    global conversation, decision_done, session_transcript, state

    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("AGENT_ID")

    eleven = ElevenLabs(api_key=api_key)
    audio = DefaultAudioInterface()

    # -----------------------------
    # CALLBACKS
    # -----------------------------

    def agent_cb(text):
        session_transcript.append("Agent: " + text)
        print(f"AGENT: {text}")

    def user_cb(text):
        global decision_done
        global state

        print(f"USER: {text}")
        session_transcript.append("User: " + text)

        event = state.process(text)

        if event == "email_captured":
            print(f"[BACKEND] Captured email: {state.email}")
        if event == "last4_captured":
            print(f"[BACKEND] Captured last4: {state.last4}")
        if event == "order_captured":
            print(f"[BACKEND] Captured order number: {state.order_number}")

        # Run refund logic ONCE
        if state.is_ready() and not decision_done:
            decision_done = True

            print("[BACKEND] Running refund logic...")
            result = process_refund(state.email, state.last4, state.order_number)

            # Save artifacts
            save_decision_log(result)
            save_receipt(result)
            save_transcript(session_transcript)

            # Print backend result
            print("[BACKEND] RESULT:", result)

            conversation.end_session()

    # -----------------------------
    # CREATE CONVERSATION
    # -----------------------------
    conversation = Conversation(
        eleven,
        agent_id,
        requires_auth=bool(api_key),
        audio_interface=audio,
        callback_agent_response=agent_cb,
        callback_user_transcript=user_cb
    )

    def stop(sig, frame):
        print("\n[BACKEND] Forced stop. Ending session.")
        conversation.end_session()

    signal.signal(signal.SIGINT, stop)

    print("Voice agent running... Speak when you hear the greeting.")
    conversation.start_session()
    conversation.wait_for_session_end()
    print("[BACKEND] Session finished.")


if __name__ == "__main__":
    main()
