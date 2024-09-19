1. install requirements.txt

python3 -m venv venv

MACOS:
source venv/bin/activate

WIN:
.\venv\Scripts\activate


deactivate

test:
python -m unittest discover tests

tree -I "venv|*.pyc|__pycache__"
