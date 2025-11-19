# 🎧 Request Resolution Voice Agent (Refund PoC)

A working Proof-of-Concept for **Spike SPK-005**:  
a voice-driven customer refund flow powered by **ElevenLabs Conversational AI** plus a lightweight Python backend.

This PoC demonstrates:

- Voice-driven identity collection (email + last-4 digits)
- Order lookup and refund eligibility checks
- Backend business logic with clean audit outputs
- End-to-end conversational loop using ElevenLabs callbacks
- Artifact generation for compliance and observability
- Cost + metrics tracking per call
- Two required trials:
  - **Trial A — Eligible Refund**
  - **Trial B — Ineligible Refund**

---

## 📁 Project Structure
refund_voice_agent/
│
├── backend/
│ ├── conversation_state.py # State machine for email → last4 → order
│ ├── refund_engine.py # Mock data + refund rules
│ ├── artifact_logger.py # Artifacts, metrics, trial summaries
│ └── order_data.json # Sample customers/orders
│
├── artifacts/ # transcripts, receipts, metrics (auto-generated)
├── logs/ # trial summaries (auto-generated)
│
├── run_agent.py # Main entry point (voice agent session)
├── .env # API keys (not committed)
├── .gitignore
└── .venv/ # Virtual environment (ignored)

## 🧠 How It Works — High-Level Architecture

```mermaid
flowchart LR
    User((User))
    Agent[ElevenLabs Voice Agent]
    Callback[Python Callback Layer]
    State[Conversation State Machine]
    Refund["Refund Engine (Eligibility Logic)"]
    Artifacts[(Artifacts\nDecision Log, Receipt,\nMetrics, Transcript)]

    User --> Agent
    Agent --> Callback
    Callback --> State
    State --> Refund
    Refund --> Callback
    Callback --> Agent
    Callback --> Artifacts
    Agent --> User


🚀 **Setup & Installation**

1. Clone the Repository
git clone https://github.com/Rkruhh/refund_voice_agent.git
cd refund_voice_agent

2. Create Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies
pip install elevenlabs python-dotenv

4. Create .env
ELEVENLABS_API_KEY=your_api_key
AGENT_ID=your_elevenlabs_agent_id

5. Configure Your ElevenLabs Agent
Set the "System Instructions" to your custom persona:
Short, friendly responses
Ask email → last4 → order number
Never mention AI, ElevenLabs, or technology
Final message:
“Hi there! I can help with your refund. What’s the email on your account?”


🎤 Running the Voice Agent
python run_agent.py

