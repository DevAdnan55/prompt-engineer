"""
🧪 Prompt Eval
--------------
Evaluates whether prompt engineering improves LLM output quality.

Runs the same input twice:
  - Once raw (no engineering)
  - Once engineered (with your system prompt)

GPT judges both on Clarity, Completeness, Specificity, and Structure.
Declares a winner with total score.

Usage:
    python prompt_eval.py                  # interactive mode
    python prompt_eval.py --batch          # batch mode
"""

import os
import json
import argparse
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
    "structure": <sum of 4 scores>,
    "total": <sum of 4 scores>
  },
  "winner": "<A or B>",
  "reason": "<one sentence explaining why the winner is better>"
}
""".strip()

# ── Core Functions ─────────────────────────────────────────────────────────────

def engineer_prompt(raw_input: str) -> str:
    """Transforms raw input into an engineered prompt."""
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
    """Gets a model response for a given prompt."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def evaluate(raw_input: str, response_a: str, response_b: str) -> dict:
    """Asks GPT to judge both responses and return scores as JSON."""
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
                return {
                    "response_a": {"clarity": 5, "completeness": 5, "specificity": 5, "structure": 5, "total": 20},
                    "response_b": {"clarity": 5, "completeness": 5, "specificity": 5, "structure": 5, "total": 20},
                    "winner": "B",
                    "reason": "Could not parse judge response — please try again."
                }
            continue


# ── Display ────────────────────────────────────────────────────────────────────

def divider(char="─", width=60):
    print(char * width)

def print_eval_results(raw_input: str, engineered: str, response_a: str, response_b: str, scores: dict):
    """Prints a clean eval report to the terminal."""
    a = scores["response_a"]
    b = scores["response_b"]
    winner = scores["winner"]
    reason = scores["reason"]

    print("\n" + "="*60)
    print("🧪 PROMPT EVAL REPORT")
    print("="*60)

    print(f"\n📝 Raw Input:\n  {raw_input}")
    print(f"\n✨ Engineered Prompt:\n  {engineered[:200]}{'...' if len(engineered) > 200 else ''}")

    divider()
    print("\n📊 SCORES (out of 10 per category, 40 total)\n")
    print(f"{'Criteria':<20} {'Response A (Raw)':>16} {'Response B (Engineered)':>24}")
    divider()
    print(f"{'Clarity':<20} {a['clarity']:>16} {b['clarity']:>24}")
    print(f"{'Completeness':<20} {a['completeness']:>16} {b['completeness']:>24}")
    print(f"{'Specificity':<20} {a['specificity']:>16} {b['specificity']:>24}")
    print(f"{'Structure & Format':<20} {a['structure']:>16} {b['structure']:>24}")
    divider()
    print(f"{'TOTAL':<20} {a['total']:>16} {b['total']:>24}")

    print(f"\n🏆 WINNER: Response {'A (Raw)' if winner == 'A' else 'B (Engineered)'}")
    print(f"💬 Reason: {reason}")
    print("\n" + "="*60)


# ── Modes ──────────────────────────────────────────────────────────────────────

def run_eval(raw_input: str):
    """Full eval pipeline for a single input."""
    print("\n⏳ Step 1/4 — Engineering the prompt...")
    engineered = engineer_prompt(raw_input)

    print("⏳ Step 2/4 — Getting response from raw prompt...")
    response_a = get_response(raw_input)

    print("⏳ Step 3/4 — Getting response from engineered prompt...")
    response_b = get_response(engineered)

    print("⏳ Step 4/4 — Judging both responses...")
    scores = evaluate(raw_input, response_a, response_b)

    print_eval_results(raw_input, engineered, response_a, response_b, scores)


def interactive_mode():
    print("\n🧪 Prompt Eval — Interactive Mode")
    print("Type a raw prompt to evaluate. Type 'quit' to exit.\n")
    divider("=")

    while True:
        raw = input("\n✏️  Raw input: ").strip()
        if raw.lower() in ("quit", "exit", "q"):
            print("👋 Bye!")
            break
        if not raw:
            print("⚠️  Please enter something.")
            continue
        run_eval(raw)


def batch_mode():
    test_inputs = [
        "explain transformers in ML",
        "write a python function to read a csv",
        "what is RAG",
        "how do I improve my resume",
    ]

    print("\n🧪 Batch Eval Mode\n")
    divider("=")

    for i, raw in enumerate(test_inputs, 1):
        print(f"\n[{i}/{len(test_inputs)}] Evaluating: {raw}")
        run_eval(raw)


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="🧪 Prompt Eval CLI")
    parser.add_argument(
        "--batch", action="store_true",
        help="Run batch eval on built-in test inputs"
    )
    args = parser.parse_args()

    print(f"✅ Eval ready — model: {MODEL}")

    if args.batch:
        batch_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
