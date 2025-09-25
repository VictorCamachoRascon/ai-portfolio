#!/usr/bin/env bash
set -euo pipefail

UI_STACK="${1:-react}" # react | blazor

echo "=== Day 5 Setup in $(pwd) ==="
echo "UI stack: ${UI_STACK}"

# Basic sanity check
for must in LICENSE README.md requirements.txt src tests; do
  [ -e "$must" ] || { echo "ERROR: Missing '$must' in repo root. Aborting."; exit 1; }
done

# 1) NLP skeleton
echo "-> Creating NLP skeleton (src/nlp)..."
mkdir -p src/nlp/pipelines
: > src/nlp/__init__.py
: > src/nlp/pipelines/__init__.py

cat > src/nlp/README.md << 'EONLP'
# /src/nlp
NLP utilities for the portfolio:
- tokenization helpers
- embedding utilities
- light chat pipeline (stub)
EONLP

cat > src/nlp/tokenization.py << 'EONLP'
from typing import List

def simple_whitespace_tokenize(text: str) -> List[str]:
    """
    Minimal tokenizer: split on whitespace.
    Replace later with nltk/transformers tokenizers as needed.
    """
    return text.split()
EONLP

cat > src/nlp/embeddings.py << 'EONLP'
from typing import List
import math

def dummy_embed(texts: List[str]) -> List[List[float]]:
    """
    Stub embedding: returns a trivial 3D vector per text.
    Replace with SentenceTransformers or Azure OpenAI embeddings.
    """
    out = []
    for t in texts:
        l = len(t)
        out.append([l, math.log1p(l), (l % 7) / 7.0])
    return out
EONLP

cat > src/nlp/pipelines/chat.py << 'EONLP'
from typing import Dict

def echo_chat_pipeline(message: str, **kwargs) -> Dict:
    """
    Minimal chat stub. Replace with actual LLM calls (FastAPI route uses this).
    """
    return {"reply": f"Echo: {message}", "meta": {"model": "stub", "temperature": kwargs.get("temperature", 0.0)}}
EONLP

# 2) Backend FastAPI stubs (create or extend)
echo "-> Creating/augmenting backend/app.py ..."
mkdir -p backend

if [ -f backend/app.py ]; then
python - << 'PY'
from pathlib import Path
p = Path("backend/app.py")
txt = p.read_text()
snippet = """

# --- Day 5: NLP stub routes ---
from fastapi import Body
from src.nlp.tokenization import simple_whitespace_tokenize
from src.nlp.embeddings import dummy_embed
from src.nlp.pipelines.chat import echo_chat_pipeline

@app.get("/nlp/health")
def nlp_health():
    return {"status": "ok", "module": "nlp"}

@app.post("/nlp/tokenize")
def nlp_tokenize(payload: dict = Body(...)):
    text = payload.get("text", "")
    return {"tokens": simple_whitespace_tokenize(text)}

@app.post("/nlp/embed")
def nlp_embed(payload: dict = Body(...)):
    texts = payload.get("texts", [])
    return {"embeddings": dummy_embed(texts)}

@app.post("/nlp/chat")
def nlp_chat(payload: dict = Body(...)):
    msg = payload.get("message", "")
    temperature = payload.get("temperature", 0.0)
    return echo_chat_pipeline(msg, temperature=temperature)
"""
if "/nlp/health" not in txt:
    p.write_text(txt + snippet)
    print("Extended backend/app.py with NLP routes.")
else:
    print("backend/app.py already has NLP routes; skipping append.")
PY
else
cat > backend/app.py << 'EOBE'
from fastapi import FastAPI, Body
from src.nlp.tokenization import simple_whitespace_tokenize
from src.nlp.embeddings import dummy_embed
from src.nlp.pipelines.chat import echo_chat_pipeline

app = FastAPI(title="AI Portfolio API")

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Day 5: NLP stub routes ---
@app.get("/nlp/health")
def nlp_health():
    return {"status": "ok", "module": "nlp"}

@app.post("/nlp/tokenize")
def nlp_tokenize(payload: dict = Body(...)):
    text = payload.get("text", "")
    return {"tokens": simple_whitespace_tokenize(text)}

@app.post("/nlp/embed")
def nlp_embed(payload: dict = Body(...)):
    texts = payload.get("texts", [])
    return {"embeddings": dummy_embed(texts)}

@app.post("/nlp/chat")
def nlp_chat(payload: dict = Body(...)):
    msg = payload.get("message", "")
    temperature = payload.get("temperature", 0.0)
    return echo_chat_pipeline(msg, temperature=temperature)
EOBE
fi

# 3) Ensure Python requirements have basics (append if missing)
echo "-> Ensuring requirements.txt has FastAPI, uvicorn, pydantic, numpy ..."
python - << 'PY'
from pathlib import Path
req = Path("requirements.txt")
base = req.read_text() if req.exists() else ""
have = {l.strip().split("==")[0] for l in base.splitlines() if l.strip()}
need = {"fastapi", "uvicorn[standard]", "pydantic", "numpy"}
missing = sorted(need - have)
if missing:
    with req.open("a") as f:
        if base and not base.endswith("\n"):
            f.write("\n")
        for m in missing:
            f.write(m + "\n")
    print("Added to requirements.txt:", ", ".join(missing))
else:
    print("requirements.txt already contains needed basics.")
PY

# 4) UI setup (optional): React or Blazor, under src/ui
echo "-> Setting up UI (src/ui) ..."
mkdir -p src

case "${UI_STACK}" in
  react)
    if command -v npm >/dev/null 2>&1; then
      if [ ! -d src/ui ]; then
        ( cd src && npm create vite@latest ui -- --template react )
        ( cd src/ui && npm install && npm install axios )
      else
        echo "src/ui already exists; skipping Vite create."
      fi
      if [ -d src/ui/src ]; then
        mkdir -p src/ui/src/lib
        cat > src/ui/src/lib/api.ts << 'EOUI'
import axios from "axios";
const api = axios.create({ baseURL: "http://127.0.0.1:8000" });
export const nlpHealth = () => api.get("/nlp/health").then(r => r.data);
export const tokenize = (text: string) => api.post("/nlp/tokenize", { text }).then(r => r.data);
export const embed = (texts: string[]) => api.post("/nlp/embed", { texts }).then(r => r.data);
export const chat = (message: string, temperature=0) => api.post("/nlp/chat", { message, temperature }).then(r => r.data);
export default api;
EOUI
        cat > src/ui/src/App.jsx << 'EOUI'
import { useState } from "react";
import { nlpHealth, tokenize, embed, chat } from "./lib/api";

export default function App() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState(null);

  return (
    <div style={{ maxWidth: 720, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>AI Portfolio UI</h1>
      <div style={{ display: "grid", gap: "0.75rem" }}>
        <button onClick={async () => setOutput(await nlpHealth())}>NLP Health</button>

        <div>
          <label>Text</label><br/>
          <input value={input} onChange={e => setInput(e.target.value)} style={{ width: "100%" }}/>
        </div>

        <button onClick={async () => setOutput(await tokenize(input))}>Tokenize</button>
        <button onClick={async () => setOutput(await embed([input]))}>Embed</button>
        <button onClick={async () => setOutput(await chat(input, 0))}>Chat (Echo)</button>

        <pre style={{ background: "#111", color: "#eee", padding: "1rem", borderRadius: 8 }}>
{output ? JSON.stringify(output, null, 2) : "Output will appear here..."}
        </pre>
      </div>
    </div>
  );
}
EOUI
      fi
    else
      echo "WARN: npm not found; skipping React UI scaffolding."
    fi
    ;;
  blazor)
    if command -v dotnet >/dev/null 2>&1; then
      if [ ! -d src/ui ]; then
        ( cd src && dotnet new blazorwasm -o ui --no-https )
        ( cd src/ui && dotnet add package Microsoft.Extensions.Http )
      else
        echo "src/ui already exists; skipping Blazor scaffold."
      fi
      mkdir -p src/ui/Services
      cat > src/ui/Services/NlpApiClient.cs << 'EOBCS'
using System.Net.Http.Json;

namespace UI.Services
{
    public class NlpApiClient(HttpClient http)
    {
        public async Task<object?> Health() => await http.GetFromJsonAsync<object>("http://127.0.0.1:8000/nlp/health");
        public async Task<object?> Tokenize(string text) =>
            await http.PostAsJsonAsync("http://127.0.0.1:8000/nlp/tokenize", new { text })
                .Result.Content.ReadFromJsonAsync<object>();
        public async Task<object?> Embed(string text) =>
            await http.PostAsJsonAsync("http://127.0.0.1:8000/nlp/embed", new { texts = new[] { text } })
                .Result.Content.ReadFromJsonAsync<object>();
        public async Task<object?> Chat(string message, double temperature = 0) =>
            await http.PostAsJsonAsync("http://127.0.0.1:8000/nlp/chat", new { message, temperature })
                .Result.Content.ReadFromJsonAsync<object>();
    }
}
EOBCS
      if [ -f src/ui/Pages/Index.razor ]; then
        cat > src/ui/Pages/Index.razor << 'EOBCS'
@page "/"
@inject HttpClient Http
@code {
    UI.Services.NlpApiClient? Api;
    protected override void OnInitialized() => Api = new(Http);
    string Input = "";
    object? Output;
    async Task DoHealth() => Output = await Api!.Health();
    async Task DoTokenize() => Output = await Api!.Tokenize(Input);
    async Task DoEmbed() => Output = await Api!.Embed(Input);
    async Task DoChat() => Output = await Api!.Chat(Input, 0);
}
<h1>AI Portfolio UI (Blazor)</h1>
<input @bind="Input" style="width:100%" />
<div style="display:flex; gap:.5rem; margin:.5rem 0">
    <button @onclick="DoHealth">NLP Health</button>
    <button @onclick="DoTokenize">Tokenize</button>
    <button @onclick="DoEmbed">Embed</button>
    <button @onclick="DoChat">Chat</button>
</div>
<pre>@(Output is null ? "Output will appear here..." : System.Text.Json.JsonSerializer.Serialize(Output, new System.Text.Json.JsonSerializerOptions{WriteIndented=true}))</pre>
EOBCS
      fi
    else
      echo "WARN: dotnet not found; skipping Blazor UI scaffolding."
    fi
    ;;
  *)
    echo "ERROR: Unknown UI stack '${UI_STACK}'. Use 'react' or 'blazor'."
    exit 2
    ;;
esac

echo "=== Day 5 setup complete ==="
echo "Next steps:"
echo "1) Start API:    uvicorn backend.app:app --reload --port 8000"
if [ "${UI_STACK}" = "react" ]; then
  echo "2) Start UI:     (cd src/ui && npm run dev)"
else
  echo "2) Start UI:     (cd src/ui && dotnet run)"
fi
echo "3) Test endpoints:"
echo "   curl http://127.0.0.1:8000/nlp/health"
echo "   curl -X POST http://127.0.0.1:8000/nlp/tokenize -H 'Content-Type: application/json' -d '{\"text\":\"hello from day five\"}'"
