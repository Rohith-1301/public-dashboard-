import json
import bcrypt
from pathlib import Path

def setup():
    # Create folders
    Path("users").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)

    # Create users
    users = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "user1", "password": "user123", "role": "user"},
    ]

    hashed_users = []
    for u in users:
        hashed_pw = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt()).decode()
        hashed_users.append({
            "username": u["username"],
            "password": hashed_pw,
            "role": u["role"],
            "created": "2024-01-01 00:00:00"
        })

    with open("users/users.json", "w") as f:
        json.dump({"users": hashed_users}, f, indent=4)

    print("Setup complete!")
    print("Users created:")
    print("  admin / admin123 (Admin)")
    print("  user1 / user123 (User)")

if __name__ == "__main__":
    setup()