# Week 1 — FastAPI + OpenAI

## Run locally

```bash
cp .env.example .env        # add your OPENAI_API_KEY
pip install -r requirements.txt
fastapi dev main.py
```

## Streamlit demo

Start the API first, then run the demo UI in a second terminal:

```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

Open `http://localhost:8501`, choose `Local` for `http://127.0.0.1:8000/ask` or `Live Render` for the deployed API, enter a question, and click **Ask**.

The response panel displays `answer`, `tokens_used`, and `cost_usd`, with the complete response available under **Full JSON**.

## Test

```bash
# Health check
curl http://localhost:8000/

# Ask (structured response)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is FastAPI?"}'

# Ask with context
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarise this", "context": "FastAPI is a modern Python web framework."}'

# Stream
curl -X POST http://localhost:8000/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain Python in 3 sentences."}'
```
