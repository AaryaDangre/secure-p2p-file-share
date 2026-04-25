from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any
from .services import FileTransferService
from .models import get_all_transfers

import socket
from fastapi.responses import FileResponse
import os
import json

router = APIRouter()

CHAT_FILE = "chat_messages.json"


def load_chat():
    try:
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_chat(data):
    with open(CHAT_FILE, "w") as f:
        json.dump(data, f)


# ================= FILE TRANSFER =================

@router.post("/send-file/")
async def send_file_to_peer(
    file: UploadFile = File(...),
    ip: str = Form(...),
    port: int = Form(...)
):

    try:
        if not ip or len(ip.split('.')) != 4:
            raise HTTPException(status_code=400, detail="Invalid IP")

        if not (1 <= port <= 65535):
            raise HTTPException(status_code=400, detail="Invalid Port")

        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")

        temp_file_path = FileTransferService.save_uploaded_file(file)

        try:
            result = FileTransferService.send_file_to_peer(
                peer_ip=ip,
                peer_port=port,
                file_path=temp_file_path
            )
            return result

        finally:
            FileTransferService.cleanup_temp_file(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= TRANSFERS =================

@router.get("/transfers/")
async def get_transfers():
    transfers = get_all_transfers()
    return {
        "status": "success",
        "data": transfers,
        "count": len(transfers)
    }


# ================= DOWNLOAD (FIXED) =================

@router.get("/download/{filename}")
async def download_file(filename: str):

    # 🔥 CRITICAL FIX: match how files are actually stored
    stored_filename = f"received_{filename}"

    if not os.path.exists(stored_filename):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=stored_filename,
        filename=filename,  # user gets original name
        media_type='application/octet-stream'
    )


# ================= CHAT =================

@router.post("/send-message/")
async def send_message(data: dict):

    message = data["message"]
    ip = data["ip"]
    port = int(data["port"])
    client_id = data.get("client_id", "unknown")

    chat = load_chat()

    # sender message
    chat.append({
        "message": message,
        "type": "sent",
        "sender_ip": ip,
        "sender_port": port,
        "client_id": client_id
    })

    save_chat(chat)

    # socket send
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    client.send(f"CHAT:{client_id}|{message}".encode())
    client.close()

    return {"status": "sent"}


@router.get("/messages/")
async def get_messages():
    return load_chat()