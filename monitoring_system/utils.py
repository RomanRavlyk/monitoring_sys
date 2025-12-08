import uuid
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)

def gen_cid():
    return str(uuid.uuid4())

