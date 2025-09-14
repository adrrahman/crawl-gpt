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
python -m scrape_gpt.chat --session_id "medrecruit" --link "https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1" --prompt "visit first 3 job details page from page 1-3 (total 9 jobs); extract job title, company name, location, salary, job type, experience level, date posted and job description."

python -m scrape_gpt.chat --session_id "medrecruit" --prompt "Filter data that have pay higher than $2,500 per day only."
```

# Contributing

Update code and run

```
pytest tests
```
