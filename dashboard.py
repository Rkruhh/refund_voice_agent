import os
import json
import glob
from datetime import datetime

import streamlit as st

from backend.conversation_state import ConversationState
from backend.refund_engine import process_refund
from backend.artifact_logger import (
    save_decision_log,
    save_receipt,
    save_transcript,
)

# ---------- Helpers for artifacts ----------

ARTIFACTS_DIR = "artifacts"
LOGS_DIR = "logs"


def get_latest_file(pattern: str):
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def load_json_file(path: str):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def load_text_file(path: str):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return f.read()


# ---------- Streamlit app setup ----------

st.set_page_config(
    page_title="Refund Voice Agent Dashboard",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 Refund Voice Agent – Chat & Dashboard")

st.markdown(
    """
This UI sits **on top of your existing backend**:

- Uses the same `ConversationState` and `process_refund` logic  
- Writes decision logs, receipts, and transcripts via `artifact_logger`  
- Lets you test the refund flow without voice, using a simple chat-style bot  
"""
)

# ---------- Session state init ----------

if "conv_state" not in st.session_state:
    st.session_state.conv_state = ConversationState()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user"/"bot", "text": str}

if "conversation_start" not in st.session_state:
    st.session_state.conversation_start = None


def reset_conversation():
    st.session_state.conv_state = ConversationState()
    st.session_state.chat_history = []
    st.session_state.conversation_start = None


# ---------- Layout: left = chat, right = dashboard ----------

left_col, right_col = st.columns([2, 1])

# ========== LEFT: Chatbot ==========

with left_col:
    st.subheader("💬 Refund Bot (Text Mode)")

    # Show chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["text"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["text"])

    # Chat input
    user_input = st.chat_input("Type your message (e.g., 'I want a refund')")

    if user_input:
        # start time for this conversation
        if st.session_state.conversation_start is None:
            st.session_state.conversation_start = datetime.now()

        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "text": user_input})

        state: ConversationState = st.session_state.conv_state
        event = state.process(user_input)

        # Decide bot response based on state
        bot_reply = None

        if state.is_ready():
            # Run refund logic
            result = process_refund(state.email, state.last4, state.order_number)

            # Build final message
            if result["status"] == "approved":
                bot_reply = (
                    f"Your refund is **approved** for **${result['amount']:.2f}**.\n\n"
                    f"Refund ID: `{result['refund_id']}`.\n"
                    "You’ll receive an email confirmation shortly."
                )
            elif result["status"] == "denied":
                bot_reply = (
                    "This order is **not eligible** for a refund.\n\n"
                    "You may request an exchange or store credit instead."
                )
            else:
                bot_reply = (
                    "I couldn't find a matching customer or order. "
                    "Please double-check your email, last four digits, and order number."
                )

            # Log artifacts for this chat session
            transcript_lines = [
                f"{m['role'].capitalize()}: {m['text']}" for m in st.session_state.chat_history
            ]
            save_decision_log(result)
            save_receipt(result)
            save_transcript(transcript_lines)

            # Append bot reply
            st.session_state.chat_history.append({"role": "bot", "text": bot_reply})

            # Show bot reply immediately
            with st.chat_message("assistant"):
                st.markdown(bot_reply)

            # Show a small note and reset state for next interaction
            st.success("Refund flow completed. You can start a new request below.")
            st.button("Start New Conversation", on_click=reset_conversation)

        else:
            # Not ready yet – guide user through steps
            if state.email is None:
                if event == "email_captured":
                    bot_reply = "Thanks! Now, what are the **last four digits** of the card on your account?"
                else:
                    bot_reply = "Sure! Let's start. What's the **email** on your account?"
            elif state.last4 is None:
                if event == "last4_captured":
                    bot_reply = "Got it. **Which order** would you like to refund? (For example: 'order number one')"
                else:
                    bot_reply = "Please tell me the **last four digits** of the card on your account."
            elif state.order_number is None:
                if event == "order_captured":
                    # The next iteration will run refund logic
                    bot_reply = "Thanks. Let me process that refund for you..."
                else:
                    bot_reply = "Which **order number** is this about? (Try 'order number one' or 'order number two')"

            # Append bot reply and display
            st.session_state.chat_history.append({"role": "bot", "text": bot_reply})
            with st.chat_message("assistant"):
                st.markdown(bot_reply)

# ========== RIGHT: Dashboard / Artifacts ==========

with right_col:
    st.subheader("📊 Latest Decision & Metrics")

    # Latest decision
    latest_decision_path = get_latest_file(os.path.join(ARTIFACTS_DIR, "decision_*.json"))
    latest_receipt_path = get_latest_file(os.path.join(ARTIFACTS_DIR, "receipt_*.json"))
    latest_transcript_path = get_latest_file(os.path.join(ARTIFACTS_DIR, "transcript_*.txt"))
    latest_metrics_path = get_latest_file(os.path.join(ARTIFACTS_DIR, "metrics_*.json"))

    if latest_decision_path:
        st.caption(f"Latest decision file: `{os.path.basename(latest_decision_path)}`")
        decision_data = load_json_file(latest_decision_path)
        if decision_data:
            st.json(decision_data)
    else:
        st.info("No decision logs found yet. Run a refund flow to generate one.")

    st.markdown("---")
    st.subheader("🧾 Artifacts Explorer")

    with st.expander("Decision Logs (JSON)", expanded=False):
        for path in sorted(glob.glob(os.path.join(ARTIFACTS_DIR, "decision_*.json"))):
            st.code(os.path.basename(path))
            if st.button(f"View {os.path.basename(path)}", key=f"dec_{path}"):
                st.json(load_json_file(path))

    with st.expander("Receipts (JSON)", expanded=False):
        for path in sorted(glob.glob(os.path.join(ARTIFACTS_DIR, "receipt_*.json"))):
            st.code(os.path.basename(path))
            if st.button(f"View {os.path.basename(path)}", key=f"rec_{path}"):
                st.json(load_json_file(path))

    with st.expander("Transcripts (TXT)", expanded=False):
        for path in sorted(glob.glob(os.path.join(ARTIFACTS_DIR, "transcript_*.txt"))):
            st.code(os.path.basename(path))
            if st.button(f"View {os.path.basename(path)}", key=f"tr_{path}"):
                st.text(load_text_file(path))

    with st.expander("Metrics (if available)", expanded=False):
        metrics_files = sorted(glob.glob(os.path.join(ARTIFACTS_DIR, "metrics_*.json")))
        if not metrics_files:
            st.write("No metrics recorded yet (metrics are created from the voice flow).")
        else:
            for path in metrics_files:
                st.code(os.path.basename(path))
                if st.button(f"View {os.path.basename(path)}", key=f"met_{path}"):
                    st.json(load_json_file(path))
