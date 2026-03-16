# 🧠 Prompt Engineer

A CLI + web tool that transforms raw, vague user input into high-quality, chain-of-thought engineered prompts using the OpenAI `gpt-4.1-nano` model.

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

### 🖥️ Web UI (Streamlit)

Run the local web app in your browser:

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` with two tabs:
- **Single Prompt** — type a raw prompt, get the engineered version in a copyable text box
- **Batch Mode** — paste multiple prompts (one per line), engineer all at once with a live progress bar

### ⌨️ CLI

**Interactive mode** — type prompts one by one:
```bash
python prompt_engineer.py
```

**Interactive + run** — engineer the prompt AND see the model's response:
```bash
python prompt_engineer.py --run
```

**Batch mode** — engineer multiple prompts at once (edit the `test_inputs` list in the file):
```bash
python prompt_engineer.py --batch
```

**Exit interactive mode** by typing `quit`, `exit`, or `q`.

## Project Structure

```
prompt-engineer/
├── app.py                 # Streamlit web UI
├── prompt_engineer.py     # CLI tool
├── requirements.txt       # Dependencies
└── .env                   # Your API key (not committed)
```

## Requirements

- Python 3.9+
- OpenAI API key

## Tech Stack

- [Streamlit](https://streamlit.io/) — local web UI
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- Model: `gpt-4.1-nano`
