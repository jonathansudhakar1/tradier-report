#!/bin/bash

# 1. Pull latest code from GitHub
git pull origin main # Assuming your primary branch is 'main'

# 2. Run the update Python command for this script
#    **Replace with the actual command to update your dependencies**
pip install -r requirements.txt # Assuming you have a requirements.txt file

# 3. Commit the code with updated JSON
git add pnl_data.json # Replace 'your_json_file.json'
git commit -m "Update dependencies and JSON"

# 4. Push to GitHub
git push origin main
