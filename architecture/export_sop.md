# Export SOP
## Goal
Convert a test plan record into downloadable DOCX and PDF files.

## Tools
- `tools/export_engine.py → to_docx()` — uses python-docx
- `tools/export_engine.py → to_pdf()` — uses reportlab

## DOCX Style Mapping
| Markdown Level | DOCX Style |
|----------------|-----------|
| `# Title` | Heading 1 |
| `## Section` | Heading 2 |
| `### Sub-section` | Heading 3 |
| `#### Sub-sub-section` | Heading 4 |
| Normal paragraph | Normal |
| `- bullet` | List Bullet |
| `1. numbered` | List Number |
| `\| table \|` | Table Grid |

## PDF Layout (reportlab)
- Page size: A4
- Fonts: Helvetica (reportlab built-in — no font installs needed)
- Color scheme: Cyan headers (#00C9B1), dark body (#1A1A2E)
- Tables: Styled with light grey borders and cyan header background

## File Naming
`{JIRA_ID}_{YYYYMMDD}.{ext}` — stored in `data/exports/`

## Edge Cases
- If a table row is a markdown separator (`---`), skip it
- If markdown has unicode bullet chars (▪), normalize to `•` before rendering
- Test cases are written separately from body markdown to maintain structure
