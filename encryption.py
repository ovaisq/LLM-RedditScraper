# encryption.py
# ©2024, Ovais Quraishi

"""This module provides functions for encrypting and decrypting 
    text using the Fernet cryptography library.
"""

from cryptography.fernet import Fernet
from config import get_config

CONFIG = get_config()

def load_key():
    """Loads a key used to encrypt and decrypt text.
    """

    filename = CONFIG.get('service', 'ENCRYPTION_KEY')
    with open(filename, 'rb') as key_file:
        key = key_file.read()
    return key

def encrypt_text(text):
    """Encrypts a piece of text using the loaded key.
    """

    key = load_key()
    cipher_suite = Fernet(key)
    encoded_text = text.encode()
    encrypted_text = cipher_suite.encrypt(encoded_text)
    return encrypted_text

def decrypt_text(encrypted_text):
    """Decrypts a piece of encrypted text using the loaded key.
    """

    key = load_key()
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(encrypted_text)
    decoded_text = decrypted_text.decode()
    return decoded_text
