import os, json
import httpx

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class LLMError(RuntimeError):
    pass

def is_enabled() -> bool:
    if LLM_PROVIDER == "none":
        return False
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        return True
    return False

async def openai_json(messages, temperature=0.0):
    if not OPENAI_API_KEY:
        raise LLMError("OPENAI_API_KEY ausente")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code >= 400:
            raise LLMError(f"OpenAI error {r.status_code}: {r.text}")
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)

async def llm_extract_json(system: str, user: str):
    if LLM_PROVIDER == "openai":
        return await openai_json(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.0,
        )
    raise LLMError(f"LLM_PROVIDER inválido: {LLM_PROVIDER}")
