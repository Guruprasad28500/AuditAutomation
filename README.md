# Excel Audit Automation

A Flask-based web application to automate an Excel audit workflow end-to-end, including:
- initial file filtering by subscript numbers,
- Local audit against SOB data,
- manual review handoff,
- Core/NonCore processing,
- description updates,
- pass/fail evaluation,
- final report generation.

## Project Structure

- `app.py` – Flask app and workflow routes
- `Audit_local.py` – Local vs SOB audit logic
- `Core_noncore.py` – Core/NonCore processing
- `update_descriptions.py` – Description enrichment/update step
- `pass_fail.py` – Pass/fail computation
- `report.py` – Final report generation
- `templates/` – UI pages for each step
- `static/css/style.css` – shared styling
- `uploads/`, `processed/` – runtime input/output files

## Requirements

- Python `3.11.9` (see `../runtime.txt`)
- Dependencies from `requirements.txt`

## Setup

From repository root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the App

```bash
python app.py
```

Open in browser:

- `http://127.0.0.1:5000/`

## Input File Expectations

- Main upload file: `.xlsx` (required)
- Optional files:
  - Rates file (`rates`) – last sheet is used
  - SOB file (`SOB`) – first sheet is used
- Main data sheet:
  - the app reads the **second sheet** (sheet index `1`) from the main file
  - must contain column: `Subscript Number`
- Form inputs:
  - `local` (required integer)
  - `core` (optional integer)
  - `noncore` (optional integer)

## Workflow

1. Upload files and subscript values (`/upload`)
2. Download initial processed file if needed (`/download`)
3. Run Local audit (`/audit_local`)
4. Perform manual review and re-upload (`/upload_reviewed`)
5. Run Core/NonCore step (`/core_noncore`)
6. Update descriptions (`/update_descriptions`)
7. Run pass/fail analysis (`/pass_fail`)
8. Generate report (`/generate_report`)
9. View completion page (`/final_result`)

## Output

- Consolidated output file: `processed/processed_data.xlsx`
- Hidden columns in output sheets include:
  - `Year`, `Month`, `Day`, `COUNTRY`, `ROWNO`, `Start Date`

## Notes

- The Flask app currently uses a hardcoded secret key in `app.py`; set a secure value through environment configuration before production deployment.
- `debug=True` is enabled in local run mode.
