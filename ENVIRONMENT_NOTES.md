# Environment Notes — Corporate Actions Workflow Application

These notes capture the development environment used for this project so it can be fully recreated later.

## Python Version
- Python 3.12.x  
  (Run `python --version` to confirm exact version.)

## Virtual Environment
- Environment type: `venv`
- Environment location: `.venv/`
- Activation:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\activate`

## Dependency Management
All Python dependencies are frozen in `requirements.txt`.

To recreate the environment:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .
```

The final step (`pip install -e .`) installs the project in editable mode so the CLI entry point (`corp-action-app`) is available during development.

## Project Structure Notes
- Uses a standard `src/` layout.
- Application code lives under `src/corporate_action_workflow_app/`.
- Tests are located under `tests/`.
- The CLI is exposed via a console script entry point defined in `pyproject.toml`.

## Environment Variables
- None required for this version.

## Tooling
- Editor: VS Code
- Recommended extensions:
  - Python
  - Pylance
  - Ruff (optional)
  - Black (optional)
- No global dependencies required beyond Python itself and Conda as the base shell.
