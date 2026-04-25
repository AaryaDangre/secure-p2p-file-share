import os
import hashlib
from crypto_core.aes_cipher import decrypt_file
from crypto_core.rsa_keys import load_keys
from crypto_core.key_exchange import decrypt_aes_key


def get_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def receive_file(conn):
    file_name = conn.recv(1024).decode()
    print(f"[RECEIVING FILE] {file_name}")

    file_size_bytes = conn.recv(8)
    file_size = int.from_bytes(file_size_bytes, 'big')
    print(f"[FILE SIZE] {file_size} bytes")

    try:
        private_key, _ = load_keys(private_key_path="private_key.pem")
    except FileNotFoundError:
        print("[ERROR] Private key not found.")
        return

    key_length_bytes = conn.recv(4)
    key_length = int.from_bytes(key_length_bytes, 'big')

    encrypted_aes_key = b""
    while len(encrypted_aes_key) < key_length:
        encrypted_aes_key += conn.recv(key_length - len(encrypted_aes_key))

    print("[RECEIVED ENCRYPTED KEY]")

    aes_key = decrypt_aes_key(encrypted_aes_key, private_key)

    temp_chunks = {}
    total_chunks = None

    received_bytes = 0
    chunk_number = 0

    while received_bytes < file_size:
        chunk_length_bytes = conn.recv(4)
        if not chunk_length_bytes:
            break

        chunk_length = int.from_bytes(chunk_length_bytes, 'big')

        encrypted_chunk = b""
        while len(encrypted_chunk) < chunk_length:
            encrypted_chunk += conn.recv(chunk_length - len(encrypted_chunk))

        decrypted = decrypt_file(encrypted_chunk, aes_key)

        # 🔥 EXTRACT METADATA
        try:
            parts = decrypted.split(b"|", 2)
            chunk_index = int(parts[0].decode())
            total_chunks = int(parts[1].decode())
            actual_data = parts[2]
        except:
            # fallback (old behavior)
            chunk_index = chunk_number
            actual_data = decrypted

        temp_chunks[chunk_index] = actual_data

        received_bytes += len(actual_data)
        chunk_number += 1

        progress = min(100, round((received_bytes / file_size) * 100, 2))
        print(f"[RECEIVING CHUNK] {chunk_number} | {progress}%")

    print("[ALL CHUNKS RECEIVED]")

    # 🔥 REASSEMBLE
    output_file = "received_" + file_name

    with open(output_file, "wb") as f:
        for i in sorted(temp_chunks.keys()):
            f.write(temp_chunks[i])

    print("[FILE REASSEMBLED SUCCESSFULLY]")

    print("\n[VERIFY] Received File Size:", os.path.getsize(output_file))
    print("[VERIFY] Received MD5:", get_md5(output_file))