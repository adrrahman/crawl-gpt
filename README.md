# Features

- Natural Language Command Processing: allow users to input commands in plain text

# Requirements

- python 3.12
- uv

# Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/adrrahman/crawl-gpt.git
   cd crawl-gpt
   ```

2. **Create and activate a virtual environment:**

   ```bash
   uv venv --python 3.12
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the Python dependencies:**

   ```bash
   uv pip install -r requirements.txt # alternative: uv pip install -r pyproject.toml
   ```

4. **Install the Playwright browsers:**

   ```bash
   playwright install
   ```

5. **Set the OpenAI API Key:**

   You can either set the environment variable manually:
   
   ```bash
   cp .env.example .env
   vim .env
   ```

# Quickstart

Run this command

```
python -m scrape_gpt.app --prompt "navigate https://shorthorn.digitalbeef.com/ do Ranch search with herd prefix 'prnl' member id '01-00927' name 'james' city 'stantons'"
```

# Contributing

Update code and run

```
pytest tests
```
