from __future__ import annotations

import argparse
from app.infra.json_store import JsonStore


def main():
    parser = argparse.ArgumentParser(description="Create/update PoC user in local JSON store.")
    parser.add_argument("--tenant", required=True, help="tenant_id (e.g., electra)")
    parser.add_argument("--email", required=True, help="user email")
    parser.add_argument("--password", required=True, help="password (will be hashed)")
    parser.add_argument("--role", default="user", choices=["user", "admin"], help="role")
    args = parser.parse_args()

    store = JsonStore()
    user = store.upsert_user(args.tenant, args.email, args.password, role=args.role)
    print("OK:", {"id": user["id"], "tenant_id": user["tenant_id"], "email": user["email"], "role": user["role"]})


if __name__ == "__main__":
    main()
