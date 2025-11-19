import os
import signal
import time
from datetime import datetime

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

from backend.conversation_state import ConversationState
from backend.refund_engine import process_refund
from backend.artifact_logger import (
    save_decision_log,
    save_receipt,
    save_transcript,
    save_metrics,
    save_trial_summary,
)

# Globals
state = ConversationState()
session_transcript = []
decision_done = False
conversation = None

# Simple cost model coefficients (tune these if needed)
C_VOICE_PER_MIN = 0.02   # $ per minute of agent runtime (example)
C_TEL_PER_MIN = 0.00     # if you add telephony later
C_TX = 0.00              # per-transaction fee (e.g. refund API fee)
C_STORE = 0.0001         # storage cost per interaction, rough


def main():
    global conversation, decision_done, session_transcript, state

    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("AGENT_ID")

    eleven = ElevenLabs(api_key=api_key)
    audio = DefaultAudioInterface()

    # --- timing markers ---
    call_start = time.time()    # Global for timing markers for the entire call
    auth_done_time = None       # Global for timing markers
    decision_time = None        # Global for timing markers

    # -----------------------------
    # CALLBACKS
    # -----------------------------

    def agent_cb(text: str):
        session_transcript.append("Agent: " + text)
        print(f"AGENT: {text}")

    def user_cb(text: str):
        nonlocal auth_done_time, decision_time
        global state, decision_done

        print(f"USER: {text}")
        session_transcript.append("User: " + text)

        event = state.process(text)

        if event == "email_captured":
            print(f"[BACKEND] Captured email: {state.email}")
        if event == "last4_captured":
            print(f"[BACKEND] Captured last4: {state.last4}")
        if event == "order_captured":
            print(f"[BACKEND] Captured order number: {state.order_number}")

        # mark auth completion when we have email + last4
        if state.email and state.last4 and auth_done_time is None:
            auth_done_time = time.time()

        # Run refund logic ONCE when we have all 3
        if state.is_ready() and not decision_done:
            decision_done = True
            decision_time = time.time()

            print("[BACKEND] Running refund logic...")
            result = process_refund(state.email, state.last4, state.order_number)
            print("[BACKEND] RESULT:", result)

            # --- metrics & cost model ---
            call_end = time.time()
            seconds_total = call_end - call_start
            seconds_to_auth = (
                auth_done_time - call_start if auth_done_time is not None else None
            )
            seconds_to_decision = (
                decision_time - call_start if decision_time is not None else None
            )

            minutes_total = seconds_total / 60.0
            voice_runtime_cost = minutes_total * (C_VOICE_PER_MIN + C_TEL_PER_MIN)
            total_cost = voice_runtime_cost + C_TX + C_STORE

            metrics = {
                "call_started_at": datetime.fromtimestamp(call_start).isoformat(),
                "call_ended_at": datetime.fromtimestamp(call_end).isoformat(),
                "seconds_total": seconds_total,
                "seconds_to_auth": seconds_to_auth,
                "seconds_to_decision": seconds_to_decision,
                "minutes_total": minutes_total,
                "cost": {
                    "voice_runtime": voice_runtime_cost,
                    "transaction": C_TX,
                    "storage": C_STORE,
                    "total": total_cost,
                },
                "inputs": {
                    "email": state.email,
                    "last4": state.last4,
                    "order_number": state.order_number,
                },
                "decision": result,
            }

            save_decision_log(result)
            save_receipt(result)
            save_transcript(session_transcript)
            save_metrics(metrics)

            # --- trial summary for spike docs ---
            # We can label by scenario: order 1 is "Trial A", order 2 is "Trial B"
            if state.order_number == 1:
                trial_label = "trial_A_eligible"
            elif state.order_number == 2:
                trial_label = "trial_B_ineligible_or_partial"
            else:
                trial_label = f"trial_order_{state.order_number}"

            summary = {
                "trial_label": trial_label,
                "email": state.email,
                "last4": state.last4,
                "order_number": state.order_number,
                "decision": result,
                "timing": {
                    "seconds_total": seconds_total,
                    "seconds_to_auth": seconds_to_auth,
                    "seconds_to_decision": seconds_to_decision,
                },
                "cost": {
                    "minutes_total": minutes_total,
                    "total_cost_estimate": total_cost,
                },
            }

            save_trial_summary(trial_label, summary)

            # End session after backend work is done
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
        callback_user_transcript=user_cb,
    )

    def stop(sig, frame):
        print("\n[BACKEND] Forced stop. Ending session.")
        try:
            conversation.end_session()
        except Exception:
            pass

    signal.signal(signal.SIGINT, stop)

    print("Voice agent running... Speak when you hear the greeting.")
    conversation.start_session()
    conversation.wait_for_session_end()
    print("[BACKEND] Session finished.")


if __name__ == "__main__":
    main()
