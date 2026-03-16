"""
🧠 Prompt Engineer — Streamlit App
-----------------------------------
Local web UI for the prompt engineer tool.

Run with:
    streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ── Setup ──────────────────────────────────────────────────────────────────────

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4.1-nano"

# ── System Prompt ──────────────────────────────────────────────────────────────

PROMPT_ENGINEER_SYSTEM = """
You are an expert prompt engineer. Your job is to transform a raw, vague, or poorly structured
user input into a world-class prompt that will produce the best possible output from a large
language model.

When rewriting, always apply these techniques:

1. **Role Assignment** — Give the LLM a clear expert persona relevant to the task.
2. **Task Clarity** — Restate the goal precisely. Remove ambiguity.
3. **Chain-of-Thought (CoT)** — Instruct the model to reason step by step before giving a final answer.
   Use phrases like:
   - "Think through this step by step."
   - "First, analyze X. Then consider Y. Finally, synthesize your answer."
   - "Show your reasoning before providing the final answer."
4. **Constraints & Format** — Specify output format, length, tone, or structure if helpful.
5. **Context Injection** — Add any missing context that would help the model respond better.

Output format:
Return ONLY the engineered prompt, ready to be pasted directly into a chat or API call.
Do not add explanations or meta-commentary — just the improved prompt itself.
""".strip()

# ── Core Functions ─────────────────────────────────────────────────────────────

def engineer_prompt(raw_input: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT_ENGINEER_SYSTEM},
            {"role": "user", "content": f"Raw input to engineer:\n\n{raw_input}"}
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()

# ── Page Config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Prompt Engineer",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Prompt Engineer")
st.caption(f"Powered by `{MODEL}` · Transforms raw input into high-quality, chain-of-thought prompts")
st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["✏️ Single Prompt", "🧪 Batch Mode"])

# ── Tab 1: Single Prompt ───────────────────────────────────────────────────────

with tab1:
    st.subheader("Single Prompt")
    st.write("Type a raw prompt and get an engineered version back.")

    raw_input = st.text_area(
        "Raw Input",
        placeholder="e.g. explain how neural networks work",
        height=120,
        key="single_input"
    )

    if st.button("⚡ Engineer Prompt", key="single_btn", use_container_width=True):
        if not raw_input.strip():
            st.warning("Please enter a prompt first.")
        else:
            with st.spinner("Engineering your prompt..."):
                result = engineer_prompt(raw_input.strip())
                st.session_state["single_result"] = result

    if "single_result" in st.session_state:
        st.subheader("✨ Engineered Prompt")
        st.text_area(
            "Copy this prompt:",
            value=st.session_state["single_result"],
            height=220,
            key="single_output"
        )
        st.caption("💡 Tip: Click inside the box, press Ctrl+A then Ctrl+C to copy.")

# ── Tab 2: Batch Mode ──────────────────────────────────────────────────────────

with tab2:
    st.subheader("Batch Mode")
    st.write("Enter multiple raw prompts, one per line. All will be engineered at once.")

    batch_input = st.text_area(
        "Raw Prompts (one per line)",
        placeholder="write a cover letter\nexplain transformers in ML\nhelp me debug my python code",
        height=160,
        key="batch_input"
    )

    if st.button("⚡ Engineer All Prompts", key="batch_btn", use_container_width=True):
        lines = [l.strip() for l in batch_input.strip().split("\n") if l.strip()]
        if not lines:
            st.warning("Please enter at least one prompt.")
        else:
            st.session_state["batch_results"] = []
            progress = st.progress(0, text="Starting...")

            for i, raw in enumerate(lines):
                progress.progress((i) / len(lines), text=f"Engineering prompt {i+1} of {len(lines)}...")
                engineered = engineer_prompt(raw)
                st.session_state["batch_results"].append((raw, engineered))

            progress.progress(1.0, text="Done!")

    if "batch_results" in st.session_state and st.session_state["batch_results"]:
        st.divider()
        st.subheader(f"✨ Results ({len(st.session_state['batch_results'])} prompts)")

        for i, (raw, engineered) in enumerate(st.session_state["batch_results"], 1):
            with st.expander(f"[{i}] {raw}", expanded=True):
                st.text_area(
                    "Engineered Prompt",
                    value=engineered,
                    height=180,
                    key=f"batch_result_{i}"
                )
