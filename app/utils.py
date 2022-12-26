import bcrypt

def hash_password(password):
    """
    Hashes a password and returns the hash
    """
    byte_pwd = password.encode('utf-8')
    salt = bcrypt.gensalt(10)
    hash = bcrypt.hashpw(byte_pwd, salt)
    return hash.decode('utf-8')