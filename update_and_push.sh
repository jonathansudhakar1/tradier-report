#!/bin/bash

# 1. Pull latest code from GitHub
git pull origin main

# 2. Run the update Python command for this script
pip install -r requirements.txt
source .venv/bin/activate
python3 tradier_pnl.py update

# 3. Commit the code with updated JSON
git add pnl_data.json
current_datetime=$(date +"%Y-%m-%d_%H-%M-%S")
git commit -m "Update dependencies and JSON - $current_datetime"

# 4. Push to GitHub
git push origin main
