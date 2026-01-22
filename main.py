import subprocess
import os
import requests
from fastapi import FastAPI, Request
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

TEMPLATE_REPO = "git@github.com:rapid7/cookiecutter-crewai.git"
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_ORG = "your-org"


COOKIECUTTER_FIELDS = [
    "crewai_project_name",
    "project_description",
    "default_aws_region",
    "max_workers",
    "crewai_version",
    "boto3_version",
    "fastapi_version",
    "uvicorn_version",
    "gunicorn_version",
    "pydantic_version",
    "pytest_version",
    "starlette_version",
    "python_dotenv_version",
    "prometheus_client_version",
    "httpx_version",
    "validators_version",
    "pytest_mock_version",
    "pytest_asyncio_version",
    "pytest_cov_version",
    "kubernetes_version",
    "orjson_version",
    "agentic_api_models_version",
    "r7_aicoe_metrics_version",
    "r7_aicoe_correlation_id_version",
    "r7_aicoe_health_check_version",
    "r7_aicoe_guardrails_version",
    "r7_aicoe_k8s_secrets_loader_version",
    "r7_aicoe_logger_version",
]

@app.post("/slack-webhook")
async def create_project(req: Request):
    payload = await req.json()

    project_name = payload["crewai_project_name"]

    # 1️⃣ Build cookiecutter command dynamically
    cmd = ["cookiecutter", TEMPLATE_REPO, "--no-input"]

    for field in COOKIECUTTER_FIELDS:
        value = payload.get(field)
        if value is None:
            continue
        cmd.append(f"{field}={value}")

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # 2️⃣ Create GitHub repo
    repo_url = create_github_repo(project_name)

    project_dir = Path(project_name)


    # 3️⃣ Git init + push
    run(["git", "init"], project_dir)
    run(["git", "add", "."], project_dir)
    run(["git", "commit", "-m", "Initial scaffold"], project_dir)
    run(["git", "branch", "-M", "main"], project_dir)
    run(["git", "remote", "add", "origin", repo_url], project_dir)
    run(["git", "push", "-u", "origin", "main"], project_dir)

    # 🧹 Cleanup - delete local generated project
    try:
        shutil.rmtree(project_dir)
        print(f"Deleted local project folder: {project_dir}")
    except Exception as e:
        print(f"Cleanup failed for {project_dir}: {e}")


    return {
        "status": "success",
        "repo": repo_url
    }


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True)


def create_github_repo(name: str) -> str:
    url = "https://api.github.com/user/repos"
    
    #Below URL is for creating repo under an organization
    #url = f"https://api.github.com/orgs/{GITHUB_ORG}/repos"

    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "name": name,
        "private": True,
        "auto_init": False
    }

    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()

    return r.json()["ssh_url"]

