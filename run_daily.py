cd ~/options-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run_daily.py --force
