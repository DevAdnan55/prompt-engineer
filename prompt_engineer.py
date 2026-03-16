"""
🧠 Prompt Engineer
------------------
Transforms raw user input into a high-quality, chain-of-thought
engineered prompt using gpt-4.1-nano.

Usage:
    python prompt_engineer.py                  # interactive mode
    python prompt_engineer.py --batch          # run built-in batch test
    python prompt_engineer.py --run            # engineer + execute the prompt
"""

import os
import argparse
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
    """
    Takes a raw user input and returns a fully engineered prompt.

    Args:
        raw_input: The user's original, unrefined prompt or question.

    Returns:
        A rewritten, chain-of-thought enhanced prompt string.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT_ENGINEER_SYSTEM},
            {"role": "user", "content": f"Raw input to engineer:\n\n{raw_input}"}
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def run_engineered_prompt(engineered_prompt: str) -> str:
    """
    Runs the engineered prompt through the model and returns the response.

    Args:
        engineered_prompt: The prompt to execute.

    Returns:
        The model's response string.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": engineered_prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


# ── Display Helpers ────────────────────────────────────────────────────────────

def divider(char="─", width=60):
    print(char * width)

def print_section(title: str, content: str):
    print(f"\n{title}")
    divider()
    print(content)
    divider()


# ── Modes ──────────────────────────────────────────────────────────────────────

def interactive_mode(also_run: bool = False):
    """Loop: user types a raw prompt, gets the engineered version back."""
    print("\n🧠 Prompt Engineer — Interactive Mode")
    print("Type your raw prompt and press Enter. Type 'quit' to exit.\n")
    divider("=")

    while True:
        raw = input("\n✏️  Raw input: ").strip()
        if raw.lower() in ("quit", "exit", "q"):
            print("👋 Bye!")
            break
        if not raw:
            print("⚠️  Please enter something.")
            continue

        print("\n⏳ Engineering your prompt...")
        engineered = engineer_prompt(raw)
        print_section("✨ Engineered Prompt", engineered)

        if also_run:
            print("\n⏳ Running engineered prompt...")
            output = run_engineered_prompt(engineered)
            print_section("🤖 Model Response", output)


def batch_mode():
    """Run a set of test inputs and print engineered versions."""
    test_inputs = [
        "write a cover letter",
        "summarize this article for me",
        "help me debug my python code",
        "what's the best diet for muscle gain",
    ]

    print("\n🧪 Batch Mode — Engineering multiple prompts\n")
    divider("=")

    for i, raw in enumerate(test_inputs, 1):
        print(f"\n[{i}] Raw: {raw}")
        divider()
        result = engineer_prompt(raw)
        print(f"Engineered:\n{result}")
        divider()


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="🧠 Prompt Engineer CLI")
    parser.add_argument(
        "--batch", action="store_true",
        help="Run built-in batch test instead of interactive mode"
    )
    parser.add_argument(
        "--run", action="store_true",
        help="Also execute the engineered prompt and show the model response"
    )
    args = parser.parse_args()

    print(f"✅ Client ready — model: {MODEL}")

    if args.batch:
        batch_mode()
    else:
        interactive_mode(also_run=args.run)


if __name__ == "__main__":
    main()