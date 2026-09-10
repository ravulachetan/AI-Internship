# Path A: FastAPI and Streamlit Setup Summary

This document records the complete Path A workflow: starting from a GitHub fork, setting up Python, running the FastAPI service, testing `/ask`, adding the Streamlit demo, protecting the OpenAI key, and publishing the changes.

## 1. Repository and Fork

The project is the `week1-fastapi-intro` folder inside the `AI-Internship` repository.

### Fork on GitHub

1. Open the source repository on GitHub.
2. Click **Fork**.
3. Choose your own GitHub account as the owner.
4. Keep the fork name as `AI-Internship` unless you have a reason to rename it.

### Clone the fork

Run these commands from a terminal, replacing the URL with your own fork URL:

```bash
git clone https://github.com/YOUR_USERNAME/AI-Internship.git
cd AI-Internship/ai-engineering-bootcamp/week1-fastapi-intro
```

What they do:

- `git clone` downloads the repository and creates a local Git working copy.
- `cd` moves into the FastAPI project folder, where all commands below should be run.

In this session, the existing remote was checked with:

```bash
git remote -v
```

It pointed to:

```text
https://github.com/ravulachetan/AI-Internship.git
```

If your remote is wrong, replace it with:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/AI-Internship.git
```

## 2. Protect the API Key First

The real API key belongs in `.env`, never in Git. The repository's `.gitignore` contains:

```gitignore
.env
```

Create the local environment file from the safe template:

```bash
cp .env.example .env
```

Then open `.env` and set your key:

```text
OPENAI_API_KEY=your_key_here
```

Do not paste the real key into a commit, issue, chat message, screenshot, or README.

Verify that Git ignores the file:

```bash
git check-ignore -v .env
git ls-files --error-unmatch .env
```

Expected result:

- `git check-ignore -v .env` prints the `.gitignore` rule.
- `git ls-files --error-unmatch .env` should fail because `.env` is not tracked.

Before every commit, also run:

```bash
git status --short
git diff --cached --name-only
```

Confirm that `.env` is absent from both lists.

## 3. Create and Activate the Virtual Environment

Create a project-local virtual environment:

```bash
python3 -m venv .venv
```

This creates an isolated Python installation in `.venv`, so project packages do not alter your system Python.

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

When activation works, the terminal prompt normally starts with `(.venv)`.

Verify the active tools:

```bash
python --version
python -m pip --version
```

The pip path should contain this project folder's `.venv` directory.

Whenever a new terminal is opened, activate the environment again:

```bash
cd AI-Internship/ai-engineering-bootcamp/week1-fastapi-intro
source .venv/bin/activate
```

## 4. Install the Dependencies

Install the packages declared by `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

The main dependencies are:

- `fastapi[standard]`: FastAPI and its standard command-line/server extras.
- `uvicorn`: the ASGI server that runs the FastAPI application.
- `openai`: the OpenAI Python client.
- `pydantic`: request and response validation.
- `python-dotenv`: loads `OPENAI_API_KEY` from `.env`.
- `streamlit`: the browser UI used in the final Path A demo.
- `certifi`: trusted CA certificates used by the Streamlit HTTPS request.

Confirm the important imports:

```bash
python -c "import fastapi, openai, pydantic, streamlit, certifi; print('dependencies OK')"
```

## 5. Existing FastAPI Code

The original entry point is `main.py`.

### Application setup

```python
app = FastAPI()
client = OpenAI(timeout=20.0, max_retries=3)
```

`app` is the FastAPI application object. `client` is the OpenAI client, configured with a request timeout and automatic retries.

### Request model

```python
class Question(BaseModel):
    question: str
    context: str | None = None
```

Pydantic validates incoming JSON. Every `/ask` request needs `question`; `context` is optional and is inserted as a system message when supplied.

### Existing routes

- `GET /` returns `{"status": "ok"}` and is used as a health check.
- `GET /health` returns a second health message.
- `POST /ask` sends a question to the OpenAI model and returns structured JSON.
- `POST /ask/stream` returns generated text as a plain-text stream.

### Original structured response

The original `Answer` model contained:

```python
class Answer(BaseModel):
    answer: str
    sources: list[str]
    confidence: float
```

The OpenAI call uses `client.chat.completions.parse(...)` with this Pydantic model as `response_format`. That asks the model for data matching the declared response shape instead of arbitrary text.

## 6. API Changes Made

The `Answer` model was extended with:

```python
tokens_used: int
cost_usd: float
```

After the OpenAI request succeeds, the code reads usage data:

```python
usage = completion.usage
parsed.tokens_used = usage.total_tokens if usage else 0
parsed.cost_usd = 0.0
```

This means the response reports the total token count returned by the API. `cost_usd` is currently set to `0.0`; it is a placeholder and is not calculated from model pricing yet.

The fallback response was also updated so failed API calls still return the same JSON shape:

```json
{
  "answer": "Something went wrong.",
  "sources": [],
  "confidence": 0.0,
  "tokens_used": 0,
  "cost_usd": 0.0
}
```

During testing, one request returned this fallback because the OpenAI account had no credits. A later retry succeeded after the account became available again.

## 7. Start FastAPI Locally

With `.venv` active and `.env` configured, run:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

What the command means:

- `uvicorn` starts the ASGI web server.
- `main:app` means load the variable `app` from `main.py`.
- `--reload` restarts the server when source files change.
- `--host 127.0.0.1` makes it available on this computer.
- `--port 8000` uses port 8000.

Leave this terminal running. Open a second terminal for tests and curl commands.

Check the health route:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"status":"ok"}
```

## 8. Automated Test Script

`test_all_stages.py` was added because the project did not contain the requested stage test runner.

Run it while Uvicorn is running:

```bash
python test_all_stages.py
```

The script:

1. Calls `/` and asserts that its status is `ok`.
2. Sends a POST request to `/ask`.
3. Parses the response as JSON.
4. Asserts that `answer`, `tokens_used`, and `cost_usd` exist.
5. Prints the response for inspection.

Expected success output resembles:

```text
PASS: health check
PASS: /ask response contains answer, tokens_used, and cost_usd
```

## 9. Manual curl Test

Send a question directly to the local API:

```bash
curl -sS -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is FastAPI?"}'
```

A successful response includes fields like:

```json
{
  "answer": "FastAPI is ...",
  "sources": [],
  "confidence": 0.98,
  "tokens_used": 274,
  "cost_usd": 0.0
}
```

Validate the response automatically with `jq`:

```bash
curl -sS -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is FastAPI?"}' \
  | jq -e 'type == "object" and (.answer | type == "string") and (.tokens_used | type == "number") and (.cost_usd | type == "number")'
```

The same request can target the deployed service:

```bash
curl -sS -X POST https://ai-internship-05zx.onrender.com/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is FastAPI?"}'
```

## 10. Streamlit Demo Added

There was no Streamlit file in the original project, so `streamlit_app.py` was added.

The page does the following:

1. Shows a Local/Live Render radio selector.
2. Uses `http://127.0.0.1:8000/ask` for Local.
3. Uses `https://ai-internship-05zx.onrender.com/ask` for Live Render.
4. Lets the user type a question in a text area.
5. POSTs `{"question": "..."}` as JSON.
6. Displays the answer, token count, and cost.
7. Provides a Full JSON expander for the complete response.
8. Shows a readable error if the request fails.

The app uses Python's standard `urllib` client instead of adding another HTTP library. The HTTPS request explicitly uses `certifi` because the machine's default Python certificate store rejected the Render certificate during the first live UI test.

## 11. Run the Streamlit UI

Keep the API terminal running. In another terminal, activate the environment and run:

```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

Open the URL Streamlit prints, usually:

```text
http://localhost:8501
```

For local testing, leave the API target as **Local**. For testing the deployed service, select **Live Render**. Type a question, click **Ask**, and verify that the response panel shows:

- an answer paragraph;
- `Tokens used` with a number;
- `Cost (USD)` with a number;
- the complete JSON under **Full JSON**.

## 12. Git Safety and Publishing

Check the worktree before staging:

```bash
git status --short
```

Stage changes:

```bash
git add -A
```

Inspect exactly what will be committed:

```bash
git diff --cached --name-status
```

Stop if any path ending in `/.env` appears. A stronger check is:

```bash
if git diff --cached --name-only | grep -E '(^|/)\.env$'; then
  echo 'ERROR: .env is staged'
  exit 1
else
  echo '.env is not staged'
fi
```

Commit with a descriptive message:

```bash
git commit -m "Add stage 5 API usage reporting tests"
```

Push the current branch:

```bash
git push origin main
```

Verify the remote tree after pushing:

```bash
git ls-tree -r --name-only origin/main | grep -E '(^|/)\.env$'
```

This command should print nothing. Also check the GitHub folder in a browser and confirm that `.env` is absent.

## 13. Important Current Repository State

At the time this document was created:

- The API and test changes were pushed in commit `837865d`.
- The commit message was `Add stage 5 API usage reporting tests`.
- `.env` was not staged, committed, or uploaded.
- `.env` is protected by `.gitignore`.
- The Streamlit app, `requirements.txt` changes, README updates, and `.env.example` restoration are currently local changes.
- `git status --short` currently shows:

```text
 M README.md
 M requirements.txt
?? .env.example
?? streamlit_app.py
```

To publish those remaining safe changes, run:

```bash
git add README.md requirements.txt streamlit_app.py .env.example
git diff --cached --name-only
git commit -m "Add Streamlit demo UI"
git push origin main
```

Before the commit, verify that `.env` is absent from the staged list. After the push, repeat the remote `.env` check and inspect the GitHub directory in the browser.

## 14. Useful Troubleshooting

### `ModuleNotFoundError: No module named streamlit`

Activate `.venv` and reinstall:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Port 8000 is already in use

Stop the old Uvicorn process, or use another port and update the UI target. For example:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

The current UI is configured for port 8000, so use port 8000 unless you also edit `streamlit_app.py`.

### The API returns `Something went wrong.`

Check that `.env` contains a valid key and that the OpenAI account has available credits. The app intentionally returns a safe fallback response when the OpenAI call raises an exception.

### The live UI reports an SSL certificate error

Make sure `certifi` is installed from `requirements.txt`. The Streamlit app uses `certifi.where()` to provide a trusted CA bundle for the Render HTTPS request.

### The API key was ever committed or uploaded

Treat it as leaked: revoke it immediately in the OpenAI dashboard, create a replacement key, update local and deployment secrets, and remove the old secret from the repository and its history.