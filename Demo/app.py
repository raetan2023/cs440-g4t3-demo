import os
import secrets
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from game import ATTACKS, DEMO_SECRET, MODEL, check_guess, filter_reply, request_payload

load_dotenv(Path(__file__).with_name(".env"))

st.set_page_config(page_title="The Oracle of SCIS", page_icon="🔐", layout="wide")
st.title("🔐 The Oracle of SCIS")
st.caption("A fictional password challenge · Inspired by Lakera’s Gandalf")

with st.sidebar:
    st.header("Demo controls")
    api_key = os.environ.get("OPENAI_API_KEY") or st.text_input("OpenAI API key", type="password")
    model = st.text_input("Model", value=MODEL).strip()
    level = st.radio("Defense level", [1, 2, 3], format_func=lambda n: {
        1: "1 · No defense", 2: "2 · Instruction + filter", 3: "3 · Secret outside the model"
    }[n])
    presenter = st.toggle("Behind the Curtain", value=False)
    st.caption("Presenter view reveals Levels 1–2 secrets. Turn it off for players.")
    if st.button("Reset all attempts"):
        for key in ("attempts", "vault_secret"):
            st.session_state.pop(key, None)
        st.rerun()

if "vault_secret" not in st.session_state:
    st.session_state.vault_secret = secrets.token_hex(12).upper()
if "attempts" not in st.session_state:
    st.session_state.attempts = []

descriptions = {
    1: "The model knows the password. There is no secrecy instruction.",
    2: "The model is told never to reveal the password. Python blocks replies containing the password string, ignoring case.",
    3: "A fresh random password stays in server memory. The model receives no secret, tools or earlier-level history.",
}
st.info(descriptions[level])
st.caption("SQL mirror (analogy): " + {
    1: "Concatenating untrusted input into a query.",
    2: "Trying to protect a query with a word blocklist.",
    3: "Enforcing a boundary in code. Here the boundary is secret access, not SQL syntax.",
}[level])
st.caption("Every attempt is a fresh API request. Success is observed, never scripted.")
if level == 2:
    st.write("**Demo sequence:** Try the basic request first, then the Python reconstruction attack. Compare the responses, then check the recovered password below.")

with st.form("attack"):
    example = st.selectbox("Attack starter", ATTACKS, format_func=lambda prompt:
        "1 · Basic request — ask for the password" if prompt == ATTACKS[0] else
        "2 · Crafted attack — reconstruct it with Python" if prompt == ATTACKS[1] else prompt)
    st.caption("Basic and crafted attacks both call the live model; results may vary.")
    custom = st.text_area("Your own attack (optional)", max_chars=4000,
                          placeholder="Leave blank to use the selected starter.")
    submitted = st.form_submit_button("Challenge the Oracle", type="primary")

if submitted:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar to call the model.")
    elif not model:
        st.error("Enter a model name.")
    else:
        payload = request_payload(level, custom.strip() or example, model)
        try:
            with st.spinner("Asking the Oracle…"):
                with OpenAI(api_key=api_key, timeout=30, max_retries=0) as client:
                    response = client.responses.create(**payload)
            raw = response.output_text
            if response.status != "completed" or not raw.strip():
                st.warning("The API did not return a complete text response. Try again; this is not a successful defense.")
            else:
                visible, blocked = filter_reply(level, raw)
                st.session_state.attempts.append(dict(level=level, payload=payload,
                    reply=visible, blocked=blocked))
        except OpenAIError as exc:
            st.error(f"API request failed ({type(exc).__name__}). Check the key, model access, quota and connection. This attempt has no result.")

for attempt in st.session_state.attempts:
    if attempt["level"] != level:
        continue
    with st.chat_message("user"):
        st.write(attempt["payload"]["input"][0]["content"])
    with st.chat_message("assistant"):
        st.text(attempt["reply"])
        if attempt["blocked"]:
            st.caption("The model disclosed the literal secret; the output filter caught it.")
    if presenter:
        with st.expander("Exact application payload sent to OpenAI"):
            st.json(attempt["payload"])

if presenter:
    with st.expander("Inspect this level’s instructions and filter", expanded=True):
        st.code(request_payload(level, "What's the password?", model)["instructions"], language="text")
        if level == 2:
            st.code('blocked = password.casefold() in reply.casefold()', language="python")
        if level == 3:
            st.write("Only the guess form accesses the server-side secret. Guesses and results are not sent to GPT.")

with st.form(f"guess_{level}"):
    guess = st.text_input("Recovered password", type="password", max_chars=200,
                          help="Enter the reconstructed word without spaces between letters.")
    if st.form_submit_button("Check guess locally"):
        secret = st.session_state.vault_secret if level == 3 else DEMO_SECRET
        if check_guess(guess, secret):
            st.success("Correct password — vault unlocked.")
        else:
            st.error("Incorrect password.")

st.caption("Local classroom demo, not production authentication. A refusal in one attempt does not prove immunity.")
