# 🧠 Prompt Engineer

A CLI + web tool that transforms raw, vague user input into high-quality, chain-of-thought engineered prompts using the OpenAI `gpt-4.1-nano` model. Includes a built-in evaluation system that measures how much prompt engineering improves output quality.

## How It Works

You type a rough prompt. The tool rewrites it using proven prompt engineering techniques and returns a version that gets significantly better results from any LLM.

**Techniques applied automatically:**
- **Role Assignment** — gives the model a relevant expert persona
- **Task Clarity** — removes ambiguity and sharpens the goal
- **Chain-of-Thought (CoT)** — instructs the model to reason step by step
- **Output Constraints** — specifies format, tone, and structure
- **Context Injection** — adds missing context that improves responses

## Example

**Raw input:**
```
explain how neural networks work
```

**Engineered output:**
```
You are an expert machine learning educator with years of experience 
explaining complex concepts to beginners and professionals alike. 
Explain how neural networks work. Think through this step by step: 
first describe the biological inspiration, then explain the structure 
(layers, neurons, weights), then walk through the forward pass and 
backpropagation. Finally, give a concrete real-world example. 
Use clear language and include an analogy to aid understanding.
```

## Project Structure

```
Prompt_Engineering/
├── app.py                  # Streamlit prompt engineer UI
├── eval_app.py             # Streamlit eval UI
├── prompt_engineer.py      # CLI prompt engineering tool
├── prompt_eval.py          # CLI eval tool
└── requirements.txt        # Dependencies
```

## Setup

**1. Clone the repo:**
```bash
git clone https://github.com/DevAdnan55/prompt-engineer.git
cd prompt-engineer
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Add your OpenAI API key:**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

Get your API key at: https://platform.openai.com/api-keys

## Usage

### 🧠 Prompt Engineer

**Web UI:**
```bash
streamlit run app.py
```
Opens at `http://localhost:8501` with two tabs:
- **Single Prompt** — type a raw prompt, get the engineered version in a copyable text box
- **Batch Mode** — paste multiple prompts (one per line), engineer all at once with a live progress bar

**CLI:**
```bash
python prompt_engineer.py          # interactive mode
python prompt_engineer.py --run    # engineer + see model response
python prompt_engineer.py --batch  # batch mode
```

### 🧪 Prompt Eval

Measures how much prompt engineering improves output quality using LLM-as-a-judge scoring.

**Web UI:**
```bash
streamlit run eval_app.py
```
- Runs the same input twice — once raw, once engineered
- GPT judges both on Clarity, Completeness, Specificity, and Structure (1–10 each)
- Displays scores side by side with a winner declaration

**CLI:**
```bash
python prompt_eval.py          # interactive mode
python prompt_eval.py --batch  # batch mode
```

**Exit interactive mode** by typing `quit`, `exit`, or `q`.

## Requirements

- Python 3.9+
- OpenAI API key

## Tech Stack

- [Streamlit](https://streamlit.io/) — local web UI
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- Model: `gpt-4.1-nano`
