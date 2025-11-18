import os
import signal

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface


def main():
    # Load .env variables
    load_dotenv()
    agent_id = os.getenv("AGENT_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not agent_id:
        raise RuntimeError("AGENT_ID is not set in .env")
    if not api_key:
        print("Warning: ELEVENLABS_API_KEY not set – will only work if agent is public.")

    # Create ElevenLabs client
    client = ElevenLabs(api_key=api_key)

    # Create audio interface (uses your default mic & speakers)
    audio_interface = DefaultAudioInterface()

    # Create conversation object
    conversation = Conversation(
        client=client,
        agent_id=agent_id,
        requires_auth=bool(api_key),
        audio_interface=audio_interface,
        # Print what the agent says (debug)
        callback_agent_response=lambda text: print(f"\nAgent: {text}"),
        # Print what you said (debug)
        callback_user_transcript=lambda text: print(f"User: {text}"),
    )

    # Allow Ctrl+C to stop cleanly
    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

    print("Starting voice session. Speak when you hear the agent.")
    print("Press Ctrl+C in the terminal to end.\n")

    # Start the session (non-blocking)
    conversation.start_session()

    # Wait until conversation ends
    conversation_id = conversation.wait_for_session_end()
    print(f"\nConversation ended. ID: {conversation_id}")


if __name__ == "__main__":
    main()
