import hashlib
import secrets
import base64

PBKDF2_ITERATIONS = 100_000


def generate_token() -> str:
    return secrets.token_urlsafe(48)


def _generate_salt() -> str:
    return secrets.token_hex(16)


def hash_password(password: str) -> str:
    salt = _generate_salt()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    encoded_digest = base64.b64encode(digest).decode("utf-8")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${encoded_digest}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        algorithm, iterations, salt, encoded_digest = hashed.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        return secrets.compare_digest(
            base64.b64encode(digest).decode("utf-8"),
            encoded_digest,
        )
    except (ValueError, TypeError):
        return False