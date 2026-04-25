import os
import hashlib
import math
from crypto_core.aes_cipher import generate_aes_key, encrypt_file
from crypto_core.rsa_keys import load_keys
from crypto_core.key_exchange import encrypt_aes_key

SIMULATE_CORRUPTION = False  # 🔥 Toggle this ON/OFF


def get_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def send_file(conn, file_path):
    file_name = os.path.basename(file_path)

    print("[ENCRYPTING FILE]")

    aes_key = generate_aes_key()

    try:
        _, public_key = load_keys(public_key_path="public_key.pem")
    except FileNotFoundError:
        print("[ERROR] Receiver's public key not found.")
        return

    print("[SENDING ENCRYPTED KEY]")
    encrypted_aes_key = encrypt_aes_key(aes_key, public_key)

    file_size = os.path.getsize(file_path)

    conn.send(file_name.encode())
    conn.send(file_size.to_bytes(8, 'big'))
    print(f"[FILE SIZE] {file_size} bytes")

    key_length = len(encrypted_aes_key).to_bytes(4, 'big')
    conn.send(key_length)
    conn.send(encrypted_aes_key)

    print("[CHUNKING FILE]")

    chunk_size = 1024
    total_chunks = math.ceil(file_size / chunk_size)

    chunk_number = 0
    sent_bytes = 0

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            # 🔥 ADD METADATA (SAFE)
            metadata = f"{chunk_number}|{total_chunks}|".encode()
            combined = metadata + chunk

            encrypted_chunk = encrypt_file(combined, aes_key)

            # 🔥 CORRUPTION SIMULATION (SAFE)
            if SIMULATE_CORRUPTION and chunk_number == 5:
                corrupted = bytearray(encrypted_chunk)
                corrupted[0] ^= 0xFF  # flip bits
                encrypted_chunk = bytes(corrupted)
                print("[SIMULATION] Corrupting chunk 5")

            chunk_length = len(encrypted_chunk).to_bytes(4, 'big')
            conn.send(chunk_length)
            conn.send(encrypted_chunk)

            chunk_number += 1
            sent_bytes += len(chunk)

            progress = min(100, round((sent_bytes / file_size) * 100, 2))
            print(f"[SENDING CHUNK] {chunk_number}/{total_chunks} | {progress}%")

    print("[ALL CHUNKS SENT]")
    print("\n[VERIFY] Sender File Size:", os.path.getsize(file_path))
    print("[VERIFY] Sender MD5:", get_md5(file_path))