import os
import socket
from typing import Dict, Any
from file_transfer.file_sender import send_file
from .models import log_transfer


class FileTransferService:
    """Wrapper service for existing P2P file transfer system"""
    
    @staticmethod
    def send_file_to_peer(peer_ip: str, peer_port: int, file_path: str) -> Dict[str, Any]:
        """
        Send file to peer using existing socket + send_file logic
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "message": f"File not found: {file_path}"
                }
            
            # Create socket connection
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                # Connect to peer
                client.connect((peer_ip, peer_port))
                print(f"[API] Connected to peer {peer_ip}:{peer_port}")
                
                # ✅ CRITICAL FIX: Send protocol signal BEFORE file transfer
                client.sendall(b"FILE")
                
                # Use existing send_file function
                send_file(client, file_path)
                
                # Log successful transfer to database
                try:
                    file_size = os.path.getsize(file_path)
                    log_transfer(
                        filename=os.path.basename(file_path),
                        filesize=file_size,
                        peer_ip=peer_ip,
                        port=peer_port,
                        status="success"
                    )
                except Exception as e:
                    print(f"[WARNING] Failed to log transfer: {e}")
                
                return {
                    "status": "success",
                    "message": f"File sent successfully to {peer_ip}:{peer_port}"
                }
                
            finally:
                # Ensure connection is closed
                try:
                    client.close()
                except:
                    pass
                    
        except socket.ConnectionRefusedError:
            # Log failed transfer
            try:
                file_size = os.path.getsize(file_path)
                log_transfer(
                    filename=os.path.basename(file_path),
                    filesize=file_size,
                    peer_ip=peer_ip,
                    port=peer_port,
                    status="connection_refused"
                )
            except Exception as e:
                print(f"[WARNING] Failed to log transfer: {e}")
            
            return {
                "status": "error",
                "message": f"Connection refused. Peer {peer_ip}:{peer_port} not available."
            }
        except socket.TimeoutError:
            # Log failed transfer
            try:
                file_size = os.path.getsize(file_path)
                log_transfer(
                    filename=os.path.basename(file_path),
                    filesize=file_size,
                    peer_ip=peer_ip,
                    port=peer_port,
                    status="timeout"
                )
            except Exception as e:
                print(f"[WARNING] Failed to log transfer: {e}")
            
            return {
                "status": "error", 
                "message": f"Connection timeout to {peer_ip}:{peer_port}"
            }
        except Exception as e:
            # Log failed transfer
            try:
                file_size = os.path.getsize(file_path)
                log_transfer(
                    filename=os.path.basename(file_path),
                    filesize=file_size,
                    peer_ip=peer_ip,
                    port=peer_port,
                    status="failed"
                )
            except Exception as log_e:
                print(f"[WARNING] Failed to log transfer: {log_e}")
            
            return {
                "status": "error",
                "message": f"Transfer failed: {str(e)}"
            }
    
    @staticmethod
    def save_uploaded_file(uploaded_file, temp_dir: str = "temp_uploads") -> str:
        """
        Save uploaded file to temporary directory
        """
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, uploaded_file.filename)
        
        # Handle filename conflicts
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        # Save file
        with open(file_path, "wb") as f:
            content = uploaded_file.file.read()
            f.write(content)
        
        return file_path
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Clean up temporary file after transfer"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"[WARNING] Failed to cleanup temp file {file_path}: {e}")