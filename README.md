# 🎧 Request Resolution Voice Agent (RRVA) – Refund PoC

This project is a Proof-of-Concept implementation of **SPK-005 – Request Resolution Voice Agent** for TheoremLabs. It demonstrates a voice-driven refund workflow using **ElevenLabs Conversational AI** plus a lightweight Python backend.

The agent:

- Authenticates the caller (email + last-4 digits)
- Fetches mock order history
- Evaluates refund eligibility
- Executes a simulated refund decision
- Emits auditable artifacts:
  - Decision log (JSON)
  - Refund receipt (JSON)
  - Transcript (text)
  - Metrics & cost snapshot (JSON)
  - Trial summaries for Trial A / Trial B (JSON)

---

## 1. Tech Stack

- **Runtime:** Python 3.x
- **Voice Agent:** ElevenLabs Conversational AI
- **Audio I/O:** `DefaultAudioInterface` (mic + speakers)
- **Backend:**
  - `backend/conversation_state.py` – simple state machine (email → last4 → order#)
  - `backend/refund_engine.py` – mock data + refund eligibility logic
  - `backend/artifact_logger.py` – artifacts, metrics, trial summaries
- **Storage:**
  - `artifacts/` – decision logs, receipts, transcripts, metrics
  - `logs/` – trial summaries (Trial A / Trial B)

---

## 2. Setup

```bash
git clone https://github.com/Rkruhh/refund_voice_agent.git
cd refund_voice_agent

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt   # if present, or: pip install elevenlabs python-dotenv
