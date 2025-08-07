command -v python3 >/dev/null 2>&1 || { echo >&2 "Python 3 is not installed. Please install it using your system's package manager or from https://www.python.org/downloads/"; exit 1; }

echo "Creating virtual environment..."
python3 -m venv .venv || { echo >&2 "Failed to create virtual environment. Terminating..."; exit 1;}

echo "Activating virtual environment..."
source .venv/bin/activate || { echo >&2 "Failed to activate virtual environment. Terminating..."; exit 1;}

python3 -m pip --version >/dev/null 2>&1 || { echo >&2 "Pip for Python 3 is not installed. Please install it using 'python3 -m ensurepip --default-pip'."; exit 1; }

echo "Installing dependencies..."
pip install -r requirements.txt || { echo >&2 "Failed to install dependencies. Terminating..."; exit 1;}

echo "Installing Playwright browser drivers..."
playwright install || { echo >&2 "Failed to install Playwright browsers. Terminating..."; exit 1;}