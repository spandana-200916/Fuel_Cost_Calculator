
import csv
import os
import hashlib
import secrets

USER_FILE = "users.csv"


def create_user_file():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "username",
                "salt",
                "password_hash"
            ])


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310000
    )

    return salt.hex(), hashed.hex()


def register_user(username, password):
    create_user_file()

    username = username.strip().lower()

    if len(username) < 3:
        return False, "Username must contain at least 3 characters."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    with open(USER_FILE, "r", newline="") as file:
        users = list(csv.DictReader(file))

    for user in users:
        if user["username"] == username:
            return False, "Username already exists."

    salt, password_hash = hash_password(password)

    with open(USER_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, salt, password_hash])

    return True, "Registration successful!"


def login_user(username, password):
    create_user_file()

    username = username.strip().lower()

    with open(USER_FILE, "r", newline="") as file:
        users = list(csv.DictReader(file))

    for user in users:
        if user["username"] == username:

            salt = bytes.fromhex(user["salt"])

            _, entered_hash = hash_password(
                password,
                salt
            )

            if secrets.compare_digest(
                entered_hash,
                user["password_hash"]
            ):
                return True

    return False
