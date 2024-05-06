#!/usr/bin/env python3
"""This module provides a function for generating and saving an
    encryption key to a file using the Fernet cryptography library.

   ©2024, Ovais Quraishi
"""

from pathlib import Path
from cryptography.fernet import Fernet

def generate_and_save_key(filename):
    """Generates and saves an encryption key to a file using the Fernet cryptography library.
    
        Args:
            filename (str or pathlib.Path): The name of the file to save the key to.

        Returns:
            None
    """

    if not filename.exists():
        key = Fernet.generate_key()
        with open(filename, 'wb') as key_file:
            key_file.write(key)
        print(f'Encrption Key File {filename} created')
    else:
        print(f'{filename} already exists!')

# Generate and save the key to a file
key_filename = Path('text_encryption.key')
generate_and_save_key(key_filename)

