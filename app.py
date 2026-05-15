from flask import Flask
import requests
import os

app=Flask(__name__)

GITHUB_TOKEN=os.environ.get("GITHUB_TOKEN")
USER_NAME="xxhe504"
REPO_NAME="hottopic"
WORKFLOW_FILE="run_wb_hottopic.yaml"
BRANCH="main"

@app.route('/trigger', methods=['POST'])
def trigger():
    url=f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    res=requests.post(url, headers=headers, json={"ref": BRANCH})
    return {"status": res.status_code, "text": res.text}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    