import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def generate_aes_key():
    """Generate a random 256-bit AES key"""
    return os.urandom(32)  # 32 bytes = 256 bits

def encrypt_file(data, key):
    """Encrypt file data using AES-256-CBC"""
    # Generate random IV
    iv = os.urandom(16)  # 16 bytes for AES

    # Apply PKCS7 padding
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Return IV + encrypted data
    return iv + encrypted_data

def decrypt_file(encrypted_data, key):
    """Decrypt file data using AES-256-CBC"""
    # Extract IV (first 16 bytes)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Remove PKCS7 padding
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data
