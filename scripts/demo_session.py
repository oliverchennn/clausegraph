"""Create/reset an explicitly synthetic demo through the running API."""
import argparse
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--reset-session", help="Reset only this demo session; it removes its current data")
    args = parser.parse_args()
    with httpx.Client(base_url=args.api, timeout=30) as client:
        if args.reset_session:
            response = client.post("/api/demo/reset", headers={"Authorization": f"Bearer {args.reset_session}"})
        else:
            response = client.post("/api/sessions", json={"demo": True})
        response.raise_for_status()
        workspace = response.json()
        print(f"Synthetic session: {workspace['session_id']}")
        print(f"Documents: {len(workspace['documents'])}; rules: {len(workspace['rules'])}")
        if workspace.get("plan"):
            print(f"Minimum: {workspace['plan']['proposed']['minimum_balance_cents']} cents")
        print("This token grants access to this session. Keep it private.")


if __name__ == "__main__":
    main()
