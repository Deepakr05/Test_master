"""
llm_client.py — Layer 3 Tool
Routes LLM calls to OpenAI, Anthropic, or Google Gemini.
SOP: architecture/llm_generation_sop.md
"""
import re
from typing import Optional


def generate(prompt: str, system_prompt: str, provider: str, settings: dict) -> str:
    """
    Route to the correct LLM provider and return raw markdown string.
    provider: 'openai' | 'anthropic' | 'google' | 'groq' | 'local_llm'
    """
    provider_cfg = settings.get("llm", {}).get("providers", {}).get(provider, {})
    api_key = provider_cfg.get("api_key", "")
    model = provider_cfg.get("model", "")
    temperature = float(provider_cfg.get("temperature", 0.7))
    max_tokens = int(provider_cfg.get("max_tokens", 4096))

    if not api_key:
        raise ValueError(f"No API key configured for provider '{provider}'. Check Settings.")

    if provider == "openai":
        return _call_openai(prompt, system_prompt, api_key, model, temperature, max_tokens)
    elif provider == "anthropic":
        return _call_anthropic(prompt, system_prompt, api_key, model, temperature, max_tokens)
    elif provider == "google":
        return _call_google(prompt, system_prompt, api_key, model, temperature, max_tokens)
    elif provider == "groq":
        return _call_groq(prompt, system_prompt, api_key, model, temperature, max_tokens)
    elif provider == "local_llm":
        base_url = provider_cfg.get("base_url", "http://localhost:11434/v1")
        return _call_local_llm(prompt, system_prompt, api_key, model, temperature, max_tokens, base_url)
    else:
        raise ValueError(f"Unknown LLM provider: '{provider}'")


def _call_openai(prompt, system_prompt, api_key, model, temperature, max_tokens) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model or "gpt-4o",
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def _call_anthropic(prompt, system_prompt, api_key, model, temperature, max_tokens) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model or "claude-3-5-sonnet-20241022",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _call_google(prompt, system_prompt, api_key, model, temperature, max_tokens) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(
        model_name=model or "gemini-1.5-pro",
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )
    response = gen_model.generate_content(prompt)
    return response.text


def _call_groq(prompt, system_prompt, api_key, model, temperature, max_tokens) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model or "llama-3.3-70b-versatile",
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def _call_local_llm(prompt, system_prompt, api_key, model, temperature, max_tokens, base_url) -> str:
    # Use OpenAI API format for local LLMs, which most frameworks (Ollama, LM Studio) emulate.
    from openai import OpenAI
    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=model or "llama3",
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def test_connection(provider: str, settings: dict) -> dict:
    """Ping the LLM with a minimal prompt to verify the API key works."""
    try:
        result = generate(
            prompt="Reply with exactly: OK",
            system_prompt="You are a test agent. Reply with exactly: OK",
            provider=provider,
            settings=settings,
        )
        ok = "ok" in result.lower()
        return {"ok": ok, "response": result[:50]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
