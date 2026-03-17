"""
🧪 Prompt Eval — Streamlit App
--------------------------------
Local web UI for evaluating prompt engineering quality.

Run with:
    streamlit run eval_app.py
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ── Setup ──────────────────────────────────────────────────────────────────────

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4.1-nano"

# ── System Prompts ─────────────────────────────────────────────────────────────

PROMPT_ENGINEER_SYSTEM = """
You are an expert prompt engineer. Your job is to transform a raw, vague, or poorly structured
user input into a world-class prompt that will produce the best possible output from a large
language model.

When rewriting, always apply these techniques:

1. Role Assignment — Give the LLM a clear expert persona relevant to the task.
2. Task Clarity — Restate the goal precisely. Remove ambiguity.
3. Chain-of-Thought (CoT) — Instruct the model to reason step by step before giving a final answer.
4. Constraints & Format — Specify output format, length, tone, or structure if helpful.
5. Context Injection — Add any missing context that would help the model respond better.

Return ONLY the engineered prompt. No explanations or meta-commentary.
""".strip()

JUDGE_SYSTEM = """
You are an expert LLM output evaluator. You will be given two responses to the same question:
- Response A: generated from a raw, unengineered prompt
- Response B: generated from a professionally engineered prompt

Score each response from 1 to 10 on these 4 criteria:
1. Clarity — Is the response easy to understand?
2. Completeness — Does it fully address the question?
3. Specificity — Does it give concrete details or stay vague?
4. Structure & Format — Is it well organized and easy to read?

You MUST respond in this exact JSON format and nothing else:
{
  "response_a": {
    "clarity": <score>,
    "completeness": <score>,
    "specificity": <score>,
    "structure": <score>,
    "total": <sum of 4 scores>
  },
  "response_b": {
    "clarity": <score>,
    "completeness": <score>,
    "specificity": <score>,
    "structure": <score>,
    "total": <sum of 4 scores>
  },
  "winner": "<A or B>",
  "reason": "<one sentence explaining why the winner is better>"
}
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


def get_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def evaluate(raw_input: str, response_a: str, response_b: str) -> dict:
    judge_prompt = f"""
Original question: {raw_input}

Response A (from raw prompt):
{response_a}

Response B (from engineered prompt):
{response_b}

Score both responses as instructed.
""".strip()

    for attempt in range(3):  # Retry up to 3 times if JSON is malformed
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": judge_prompt}
            ],
            temperature=0.0,
        )
        raw_json = response.choices[0].message.content.strip()
        raw_json = raw_json.replace("```json", "").replace("```", "").strip()

        # Extract only the JSON object in case there's extra text around it
        start = raw_json.find("{")
        end = raw_json.rfind("}") + 1
        if start != -1 and end != 0:
            raw_json = raw_json[start:end]

        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            if attempt == 2:
                # Return safe fallback scores on final failure
                return {
                    "response_a": {"clarity": 5, "completeness": 5, "specificity": 5, "structure": 5, "total": 20},
                    "response_b": {"clarity": 5, "completeness": 5, "specificity": 5, "structure": 5, "total": 20},
                    "winner": "B",
                    "reason": "Could not parse judge response — please try again."
                }
            continue

# ── Page Config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Prompt Eval",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Prompt Eval")
st.caption(f"Powered by `{MODEL}` · Measures how much prompt engineering improves output quality")
st.divider()

# ── Input ──────────────────────────────────────────────────────────────────────

raw_input = st.text_area(
    "Raw Input",
    placeholder="e.g. explain how transformers work",
    height=120,
)

if st.button("⚡ Run Eval", use_container_width=True):
    if not raw_input.strip():
        st.warning("Please enter a prompt first.")
    else:
        with st.spinner("Step 1/4 — Engineering the prompt..."):
            engineered = engineer_prompt(raw_input.strip())

        with st.spinner("Step 2/4 — Getting response from raw prompt..."):
            response_a = get_response(raw_input.strip())

        with st.spinner("Step 3/4 — Getting response from engineered prompt..."):
            response_b = get_response(engineered)

        with st.spinner("Step 4/4 — Judging both responses..."):
            scores = evaluate(raw_input.strip(), response_a, response_b)

        st.session_state["eval_result"] = {
            "engineered": engineered,
            "response_a": response_a,
            "response_b": response_b,
            "scores": scores,
        }

# ── Results ────────────────────────────────────────────────────────────────────

if "eval_result" in st.session_state:
    r = st.session_state["eval_result"]
    a = r["scores"]["response_a"]
    b = r["scores"]["response_b"]
    winner = r["scores"]["winner"]
    reason = r["scores"]["reason"]

    st.divider()

    # Winner banner
    if winner == "B":
        st.success(f"🏆 Winner: **Engineered Prompt** — {reason}")
    else:
        st.warning(f"🏆 Winner: **Raw Prompt** — {reason}")

    # Scores table
    st.subheader("📊 Scores (out of 10 per category)")

    col1, col2, col3 = st.columns([2, 1, 1])
    col1.markdown("**Criteria**")
    col2.markdown("**A — Raw**")
    col3.markdown("**B — Engineered**")

    for label, key in [("Clarity", "clarity"), ("Completeness", "completeness"),
                        ("Specificity", "specificity"), ("Structure & Format", "structure")]:
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(label)
        c2.write(f"{a[key]} / 10")
        c3.write(f"{b[key]} / 10")

    st.divider()
    col_a, col_b = st.columns(2)
    col_a.metric("Total — Raw", f"{a['total']} / 40")
    col_b.metric("Total — Engineered", f"{b['total']} / 40", delta=b['total'] - a['total'])

    # Responses side by side
    st.divider()
    st.subheader("💬 Responses")
    col_ra, col_rb = st.columns(2)

    with col_ra:
        st.markdown("**A — Raw Prompt Response**")
        st.text_area("", value=r["response_a"], height=500, key="resp_a")

    with col_rb:
        st.markdown("**B — Engineered Prompt Response**")
        st.text_area("", value=r["response_b"], height=500, key="resp_b")

    # Engineered prompt
    st.divider()
    st.subheader("✨ Engineered Prompt Used")
    st.text_area("", value=r["engineered"], height=150, key="eng_prompt")
