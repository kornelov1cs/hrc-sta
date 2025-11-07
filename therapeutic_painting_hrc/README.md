## Prerequisites

- Python 3.8 or higher (Python 3.11+ recommended)
- pip (Python package installer)

To check your Python version:

```bash
python --version
# or
python3 --version
```

## Installation

### Setup Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv
# On Windows, you may need to use:
# python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

**Note:** If you encounter issues activating the virtual environment on Windows PowerShell, you may need to run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
# On Windows, use: python -m venv venv

# 2. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (Command Prompt):
venv\Scripts\activate
# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run a quick simulation (comparative study, multiple runs)
python main.py --compare --runs 5 --steps 30
# On some systems, you may need: python3 main.py
```

## Usage

### Run Simulation (CLI)

```bash
# Single proactive simulation
python main.py --mode proactive --steps 30
# On some systems, use: python3 main.py --mode proactive --steps 30

# Single reactive simulation
python main.py --mode reactive --steps 30

# Comparative study (multiple runs)
python main.py --compare --runs 5 --steps 30

# Custom options
python main.py --mode proactive --steps 20 --initial-state Frustrated --no-noise
```

Results are saved to `data/simulation_logs/` as JSON files with complete state history.

### Launch Web Visualization (Optional)

For real-time human-robot interaction:

**On macOS/Linux:**

```bash
# Using the provided script
./start_canvas.sh

# Or manually using Python module
python -m api.server
# On some systems, use: python3 -m api.server
```

**On Windows:**

```bash
# Using Python module (recommended)
python -m api.server

# Alternative: Run the script directly
python api\server.py

# Or using uvicorn directly
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

**Important:** When running `python -m api.server`, make sure there are no hidden characters (like non-breaking spaces) before `api.server`. Type the command manually rather than copy-pasting if you encounter `ModuleNotFoundError: No module named '\xa0api'`.

Then open http://localhost:8000 in your browser.

## Logging & Analysis

All simulation runs produce comprehensive JSON logs:

- Timestep-by-timestep state history
- Patient true states and observations
- Robot beliefs (HMM distributions) and actions
- Canvas states (coverage, strokes, colors)
- Engagement metrics and idle duration
- Belief entropy for uncertainty tracking

Example log location: `data/simulation_logs/proactive_20251105_123456.json`

## Troubleshooting

### Python Version Issues

If you encounter compatibility errors with newer Python versions, the requirements.txt uses flexible version ranges (`>=`) that should work with Python 3.8+. If you still have issues:

1. Ensure you're using Python 3.8 or higher
2. Try upgrading pip: `pip install --upgrade pip`
3. Install packages individually if needed

### Windows-Specific Issues

**ModuleNotFoundError with non-breaking space:**
If you see an error like `ModuleNotFoundError: No module named '\xa0api'`, this indicates a hidden non-breaking space character (`\xa0`) was copied. Solution:

- Type the command manually: `python -m api.server`
- Avoid copy-pasting commands from documentation

**Virtual environment activation:**

- Use `venv\Scripts\activate` in Command Prompt
- Use `venv\Scripts\Activate.ps1` in PowerShell
- If PowerShell execution policy blocks activation, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Path separators:**

- Windows uses backslashes (`\`) in paths
- Use `python -m api.server` instead of `python api/server.py` for better cross-platform compatibility

### Command Not Found Errors

- On Windows, use `python` instead of `python3`
- On macOS/Linux, try both `python` and `python3`
- Ensure your virtual environment is activated (you should see `(venv)` in your terminal prompt)

### Port Already in Use

If port 8000 is already in use:

- Change the port in `api/server.py` or use: `uvicorn api.server:app --host 0.0.0.0 --port 8001`
- Update the browser URL accordingly

## References

- CoFRIDA: Self-Supervised Fine-Tuning for Human-Robot Co-Painting
  - Paper: https://pschaldenbrand.github.io/cofrida/
  - GitHub: https://github.com/cmubig/Frida
