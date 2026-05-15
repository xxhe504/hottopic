from flask import Flask
import requests
import os

app = Flask(__name__)

# 同时支持 GET 和 POST，浏览器访问也能触发
@app.route('/', methods=['GET', 'POST'])
@app.route('/trigger', methods=['GET', 'POST'])
def trigger():
    token = os.environ.get("GITHUB_TOKEN")
    user = "xxhe504"
    repo = "hottopic"
    workflow = "run_wb_hottopic.yaml"

    url = f"https://api.github.com/repos/{user}/{repo}/actions/workflows/{workflow}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    resp = requests.post(url, headers=headers, json={"ref": "main"})

    if resp.status_code == 204:
        return {"status": 200, "msg": "✅ 触发 GitHub Actions 成功！"}
    else:
        return {"status": resp.status_code, "msg": "触发失败", "error": resp.text}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)