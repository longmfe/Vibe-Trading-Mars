import uvicorn
import sys
import os

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

# Change to agent directory
os.chdir(os.path.join(os.path.dirname(__file__), 'agent'))

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8899, log_level="info")
