import hashlib
import os
import random
import string

def generate_salt():
    # Generates a random salt using a secure random number generator.

    return os.urandom(16)

def hash_password(password, salty=None):

    if salty is None:
        # Generate a new salt if none is provided
        salty = generate_salt()
    else:
        # Convert the hexadecimal salt string back to bytes if provided
        # print(type(salty))
        salty = bytes.fromhex(salty)
        # print(salty)
    # Combine the password (as bytes) with the salt (also bytes)
    pwd_salt = password.encode() + salty
    hash1 = hashlib.sha256(pwd_salt).hexdigest()
    
    # print(salty.hex())
    # print(bytes.fromhex(salty.hex()))
    # Return the hash and the hex representation of the salt
    return hash1, salty.hex()


def generate_password(lenght, hasCapital, hasNumbers, hasSpecialChar):
    char_pool = string.ascii_lowercase #atleast lower case required

    if hasCapital:
        char_pool += string.ascii_uppercase #if capital is toggled
    
    if hasNumbers:
        char_pool += string.digits
    
    if hasSpecialChar:
        char_pool += string.punctuation
    password = ""
    for i in range(0, lenght):
        password += char_pool[random.randrange(0, len(char_pool))]

    return password


    