# The Oracle of SCIS

Local CS440 password demo using Streamlit and the OpenAI Python SDK Responses API.

## Run

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py --server.address 127.0.0.1
```

Add your OpenAI API key to `.env` beside `app.py` (`OPENAI_API_KEY=your-key`), then restart the app. This file is ignored by Git. Alternatively, enter the key in the sidebar or set `OPENAI_API_KEY` in the process environment; existing environment values take precedence over `.env`. Never paste the key into chat or commit it. The default model is `gpt-4.1-mini`; change it in the sidebar if your account uses another model.

## Present

Use the [demo slide outline and presenter notes](docs/demo-slides.md) for P3's two-slide, 2½-minute section.

1. Level 1: ask directly for the fictional password.
2. Level 2: select “1 · Basic request”, submit, then select “2 · Crafted attack” and submit again. Leave the custom attack field blank to use these presets. The crafted prompt asks for a Python expression reconstructing the secret without spelling it out. A character-code response was observed in a manual test; repeatability is not established. Explain that the filter checks literal text, while character codes can carry the same secret. Enter the recovered word in the guess form. Refusals are genuine outcomes; no bypass is guaranteed. The filter blocks case-insensitive literal matches but deliberately does not reconstruct encodings. Never execute arbitrary model-generated code during the demo.
3. Level 3: repeat attacks. A separate random secret stays in session memory; no earlier requests or model tools carry it into the context. Guess checks run locally. This prevents disclosure through model access, not every possible attack on an application.

Behind the Curtain shows the exact application request payload and exposes the fake secrets in Levels 1–2. It is a presenter aid, not a player-facing security feature. Levels 1–2 share PARAMETERIZED for the teaching narrative; Level 3 uses a fresh random secret. Reset rotates it and clears attempts. Model output is rendered as plain text.

Each click makes one paid API request with at most 400 output tokens and no automatic retries. Model output can vary. Record a successful rehearsal as backup. No public deployment, shared counter or QR access is included.

## Checks

```sh
.venv/bin/python -m unittest -v
```

Tests check secret separation, the filter’s deliberate encoding gap, input limits and guess validation. They do not establish a model’s resistance to attacks.

Inspired by [Lakera Gandalf](https://gandalf.lakera.ai/). SDK usage follows the [OpenAI quickstart](https://developers.openai.com/api/docs/quickstart).
