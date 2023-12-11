set -o errexit

cd $(dirname -- $0)
cd ..

echo "[sleepy] Running local developement pipeline..."

echo "[sleepy] Linting using ruff..."
poetry run ruff .

echo "[sleepy] Linting using mypy..."
poetry run mypy . 

echo "[sleepy] Running tests..."
poetry run coverage run -m pytest
poetry run coverage report

echo "[sleepy] Done!"

clear
