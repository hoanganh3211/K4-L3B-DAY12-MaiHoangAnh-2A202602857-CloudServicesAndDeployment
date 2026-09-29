"""Run real HTTP checks without printing credentials; optionally save evidence."""
import argparse
import json
import os
from pathlib import Path
import uuid

from dotenv import load_dotenv
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    load_dotenv()
    key = os.getenv("DEPLOY_API_KEY") or os.environ["AGENT_API_KEY"]
    headers = {"X-API-Key": key, "X-User-Id": "smoke-" + uuid.uuid4().hex[:12]}
    observations = []
    with httpx.Client(base_url=args.url.rstrip("/"), timeout=60) as client:
        for path in ("/health", "/ready"):
            response = client.get(path)
            observations.append({"path": path, "status": response.status_code, "body": response.json()})
            assert response.status_code == 200
        response = client.post("/ask", json={"question": "Hello"})
        observations.append({"path": "/ask without key", "status": response.status_code})
        assert response.status_code == 401
        statuses, lengths = [], []
        for _ in range(15):
            response = client.post("/ask", headers=headers, json={"question": "Docker la gi?"})
            statuses.append(response.status_code)
            if response.status_code == 200:
                lengths.append(response.json()["history_length"])
        observations.append({"path": "/ask with key", "statuses": statuses, "history_lengths": lengths})
        assert lengths[:2] == [0, 2]
        assert 429 in statuses
    text = json.dumps(observations, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
