#!/bin/bash
VENV_DIR="$HOME/farm_app_docker/farm_app/.farm_app"
PYTHON_SCRIPT="$HOME/Documents/farm_app_docker/farm_app/mycology_progr.py"
PID_FILE="$HOME/Documents/farm_app_docker/scripts/id.txt"
source "$VENV_DIR/bin/activate"

nohup python "$PYTHON_SCRIPT" &

echo "Python script started in the background"


exit 0