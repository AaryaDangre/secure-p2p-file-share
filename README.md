# SecureShare 🔐

SecureShare is a robust, LAN-based peer-to-peer (P2P) file sharing and chat application. It provides end-to-end encrypted file transfers, large file chunking, and real-time private messaging, all wrapped in a sleek, modern web interface.

No middle-man servers store your data! Files are transmitted directly across your local network.

## ✨ Features

- **End-to-End Encryption**: Secure your files with AES symmetric encryption and RSA key exchange.
- **Large File Chunking**: Seamlessly transfer massive files by breaking them down into easily verifiable chunks.
- **Real-Time Private Chat**: Exchange text messages directly with peers instantly.
- **Unified Local UI**: An elegant, dynamic web dashboard built with HTML/CSS and Javascript (no complex frontend dependencies).
- **SQLite Database**: Automatically logs all of your incoming and outgoing transfers with file sizes, timestamps, and network details.
- **High-Performance Backend**: Driven by an asynchronous Python FastAPI server and raw TCP sockets for maximum transfer speeds over LAN.

## 🛠️ Technology Stack

- **Backend Framework**: Python Fastapi & Uvicorn
- **Sockets**: Raw Python TCP Sockets for Peer-to-Peer file delivery
- **Cryptography**: Python `cryptography` module (AES + RSA)
- **Database**: SQLite3
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (with Vanta.js for dynamic backgrounds)

---

## 🚀 Getting Started

To run SecureShare on your machine, you must run three separate components: the Socket Server (for receiving communication), the FastAPI Server (for backend processing), and the Frontend UI (to view the app).

### Prerequisites
Make sure you have **Python 3.x** installed. We highly recommend using a virtual environment (`venv`).

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Peer Node (TCP Server)
This socket server listens on port `5000` to receive chunks, files, and chat messages sent by other computers on your network.
```bash
python peer_node/peer_server.py
```

### 3. Start the API Server
This FastAPI server acts as a bridge between the Frontend UI and the Peer Socket Server. It manages the database and triggers uploads.
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 4. Launch the Frontend Web Client
Navigate to the `frontend` folder and start a static file server to avoid CORS issues.
```bash
cd frontend
python -m http.server 3000
```
Open your web browser and navigate to: **`http://localhost:3000`**

---

## 🌐 Transferring Files Over LAN

To transfer files and chat between *two different* computers on the same local network:

1. **Find your local IP Addresses**: Use `ipconfig` (Windows) or `ifconfig` (Mac/Linux) on both machines.
2. Follow the deployment steps above to run all three commands on **both** machines.
3. Open `http://localhost:3000` on both machines.
4. Entering IP addresses:
   - On **Computer A**: In the "Target Node Details" section, enter the IPv4 address of **Computer B**.
   - On **Computer B**: Enter the IPv4 address of **Computer A**.
5. Select a file or type a chat message. Both machines will now beam data securely over the network!

## 📜 License
See `LICENSE` file for broad usage details.
