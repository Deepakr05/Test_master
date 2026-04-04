# LLM Generation SOP
## Goal
Send a structured prompt to the configured LLM and receive a Markdown test plan
matching the 13-section template contract.

## Input
- Jira issue dict (Schema 2)
- Generation options: `include_sub_tasks`, `include_negative_cases`, `detail_level`, `test_plan_format`
- Provider: `openai | anthropic | google`

## Tool
`tools/llm_client.py → generate()`
`tools/test_plan_generator.py → build_prompt(), parse_test_cases()`

## Prompt Architecture
Two-part prompt:
1. **System Prompt** — defines the Markdown contract: exact 13 section headers, test case format
2. **User Prompt** — injects the Jira issue JSON + generation options

## Markdown Contract
The LLM MUST produce:
- `# Test Plan: {JIRA_ID} — {TITLE}` as the H1
- `## Objective` as H2
- `## Scope` as H2 containing all H3 sub-sections
- `## Test Cases` as H2 with H3 blocks per test case

If the LLM deviates (adds extra sections), the parser will ignore them.

## Retry Policy (Self-Annealing)
- Attempt 1: Call LLM
- On failure: Wait 2 seconds
- Attempt 2: Retry same call
- On second failure: Raise RuntimeError → surface to UI as 502

## Test Case Parsing
Regex-based extraction from `## Test Cases` section:
- Split by `### TC-NNN:` headers
- Extract: id, title, priority, type, preconditions (bullets), steps (numbered), expected_result, test_data (key: value bullets)

## Provider Notes
| Provider | Library | Max Tokens | Notes |
|----------|---------|-----------|-------|
| OpenAI | `openai` | 4096 (configurable) | `gpt-4o` default |
| Anthropic | `anthropic` | 4096 (configurable) | `claude-3-5-sonnet` default |
| Google | `google-generativeai` | 4096 (configurable) | `gemini-1.5-pro` default |
