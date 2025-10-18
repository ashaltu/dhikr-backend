import hashlib
import hmac
import os


def hash_url(url: str, secret_key: str | None = None) -> str:
    if secret_key is None:
        secret_key = os.getenv("SERVER_HMAC_KEY")
        if not secret_key:
            raise ValueError(
                "SERVER_HMAC_KEY environment variable must be set for secure URL hashing. "
                "Set it in your .env file to a long random string."
            )
    
    url_bytes = url.encode('utf-8')
    key_bytes = secret_key.encode('utf-8')
    
    hash_obj = hmac.new(key_bytes, url_bytes, hashlib.sha256)
    return hash_obj.hexdigest()
