#!/bin/bash
# This script runs the streamlit dashboard for visualizing Charles logs
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
# Check if virtual environment exists
export MCP_CHARLES_OUTPUT_DIR="/Users/pranjulraizada/NewAIProject/git/mcp-charles-shared/output"
echo "Starting dashboard..."
streamlit run dashboard.py
deactivate
