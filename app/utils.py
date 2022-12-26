import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a password and returns the hash
    """
    byte_pwd = password.encode('utf-8')
    salt = bcrypt.gensalt(10)
    hash = bcrypt.hashpw(byte_pwd, salt)
    return hash.decode('utf-8')

def compare_password(password: str, hash: str) -> bool:
    """
    Compares provided password with hashed password
    """
    return bcrypt.checkpw(password, hash)