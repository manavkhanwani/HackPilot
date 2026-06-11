# Deploying HackPilot to Streamlit Cloud

## Prerequisites
- GitHub account with the HackPilot repo pushed (public or private).
- Streamlit Cloud account at <https://share.streamlit.io> (free tier is sufficient).
- A Gemini API key from <https://aistudio.google.com/app/apikey>.

---

## Steps

### 1. Push to GitHub

```bash
git init          # if not already a git repo
git add .
git commit -m "Initial HackPilot commit"
git remote add origin https://github.com/<your-username>/hackpilot.git
git push -u origin main
```

Make sure `.streamlit/secrets.toml` is in `.gitignore` (it is by default).

### 2. Create a new app on Streamlit Cloud

1. Go to <https://share.streamlit.io> → **New app**.
2. Select your GitHub repo and branch (`main`).
3. Set **Main file path** to `app.py`.
4. Click **Advanced settings**.

### 3. Add the secret

In **Secrets**, paste:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```

Click **Save**.

### 4. Deploy

Click **Deploy**. Streamlit Cloud will install `requirements.txt` automatically.

First deploy takes ~2 minutes. Subsequent deploys on push are automatic.

---

## Verify

Once deployed, open the app URL and:
1. Enter a theme in the sidebar (e.g. "Sustainable Cities").
2. Click **Generate Ideas** — you should see 5 idea cards.
3. Select one and step through all 5 tabs.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `GEMINI_API_KEY not found` | Re-check the secret spelling in Streamlit Cloud settings |
| `ModuleNotFoundError` | Confirm `google-genai>=1.0.0` is in `requirements.txt` |
| Blank page on load | Check the app logs in Streamlit Cloud dashboard |
