import json
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi
import streamlit as st


st.set_page_config(page_title="FastAPI Ask Demo", page_icon="⚡")
st.title("FastAPI Ask Demo")
st.caption("Send a question to the /ask endpoint and inspect the response.")

api_target = st.radio(
    "API target",
    options=["Local", "Live Render"],
    horizontal=True,
)
api_url = (
    "http://127.0.0.1:8000/ask"
    if api_target == "Local"
    else "https://ai-internship-05zx.onrender.com/ask"
)
st.code(api_url, language="text")

question = st.text_area(
    "Question",
    value="What is FastAPI?",
    height=120,
)

if st.button("Ask", type="primary"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        request = Request(
            api_url,
            data=json.dumps({"question": question}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            with urlopen(request, timeout=60, context=ssl_context) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            st.error(f"Request failed: {error}")
        else:
            st.subheader("Response")
            st.write(result.get("answer", "No answer returned."))
            st.metric("Tokens used", result.get("tokens_used", "Unknown"))
            st.metric("Cost (USD)", result.get("cost_usd", "Unknown"))
            with st.expander("Full JSON"):
                st.json(result)