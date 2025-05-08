#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "Installing required Python packages..."
pip3 install -r requirements.txt

echo "Starting the Resume Analysis Tool..."
streamlit run streamlit_app.py
