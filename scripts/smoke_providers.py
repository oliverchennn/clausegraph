"""Smoke-test configured providers using only a temporary synthetic session."""
import argparse
import httpx


def main():
    parser = argparse.ArgumentParser(description="Configured live model requests may consume provider credits.")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    with httpx.Client(base_url=args.api, timeout=180) as client:
        response = client.post("/api/sessions", json={"demo": True})
        response.raise_for_status()
        headers = {"Authorization": "Bearer " + response.json()["session_id"]}
        try:
            result = client.post("/api/providers/smoke", headers=headers)
            result.raise_for_status()
            for status in result.json():
                print(f"{status['name']}: {status['mode']} — {status['detail']}")
        finally:
            client.delete("/api/session", headers=headers).raise_for_status()


if __name__ == "__main__":
    main()
