set -o errexit

cd $(dirname -- $0)
cd ..

echo "[sleepy] Running local developement pipeline..."

echo "[sleepy] Installing dependencies..."
poetry install
poetry update
poetry lock

echo "[sleepy] Linting using ruff..."
poetry run ruff .

echo "[sleepy] Linting using mypy..."
poetry run mypy . 

echo "[sleepy] Running tests..."
poetry run pytest

echo "[sleepy] Done!"

clear
