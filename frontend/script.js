// 🔥 AUTO-DETECT API URL (SAFE, NO SIDE EFFECTS)
const currentHost = window.location.hostname;

// 🔥 BETTER API URL LOGIC
const API_URL = (currentHost === "localhost" || currentHost === "127.0.0.1" || currentHost === "")
    ? `http://127.0.0.1:8000`
    : `http://${currentHost}:8000`;

let client_id = localStorage.getItem("client_id");

if (!client_id) {
    client_id = "client_" + Math.random().toString(36).substring(2, 10);
    localStorage.setItem("client_id", client_id);
}

function switchTab(tabId) {
    // Update active nav button
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if(btn.getAttribute('data-target') === tabId) {
            btn.classList.add('active');
        }
    });

    // Update active section
    document.querySelectorAll('.page-section').forEach(sec => {
        sec.classList.remove('active-sec');
    });
    
    const targetSection = document.getElementById(tabId);
    if(targetSection) {
        targetSection.classList.add('active-sec');
        window.location.hash = tabId;
        
        // Auto scroll to top when changing tabs
        window.scrollTo({top: 0, behavior: 'smooth'});
    }
}

// Attach listeners to nav buttons
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        switchTab(btn.getAttribute('data-target'));
    });
});

function scrollToSection() {
    switchTab('sec-transfer');
}

/* PREVIEW */
function previewFile() {
    const file = document.getElementById("fileInput").files[0];
    const preview = document.getElementById("preview");

    preview.innerHTML = "";

    if (!file) return;

    const type = file.type;

    if (type.startsWith("image")) {
        preview.innerHTML = `<img src="${URL.createObjectURL(file)}">`;
    } 
    else if (type.startsWith("video")) {
        preview.innerHTML = `
            <video controls>
                <source src="${URL.createObjectURL(file)}">
            </video>`;
    } 
    else if (type === "application/pdf") {
        preview.innerHTML = `<p>📕 PDF: ${file.name}</p>`;
    }
    else {
        preview.innerHTML = `<p>📄 ${file.name}</p>`;
    }
}

/* SEND FILE */
function sendFile() {
    const file = document.getElementById("fileInput").files[0];
    const ip = document.getElementById("ip").value;
    const port = document.getElementById("port").value;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("ip", ip);
    formData.append("port", port);

    const xhr = new XMLHttpRequest();

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            let percent = (e.loaded / e.total) * 50;
            document.getElementById("progressBar").style.width = percent + "%";
        }
    };

    xhr.onload = function() {
        if (xhr.status !== 200) {
            document.getElementById("status").innerText = "Transfer Failed ❌";
            document.getElementById("status").style.color = "red";
            return;
        }

        const response = JSON.parse(xhr.responseText);
        
        let progress = 50;
        const interval = setInterval(() => {
            progress += 5;
            document.getElementById("progressBar").style.width = progress + "%";

            if (progress >= 100) {
                clearInterval(interval);
                
                if (response.status === "error") {
                    document.getElementById("status").innerText = "Transfer Failed ❌ (" + response.message + ")";
                    document.getElementById("status").style.color = "red";
                } else {
                    document.getElementById("status").innerText = "Transfer Complete ✅";
                    document.getElementById("status").style.color = "#22c55e";
                }
                
                loadLogs();
            }
        }, 100); // make progress animation faster
    };

    xhr.open("POST", `${API_URL}/api/v1/send-file/`);
    xhr.send(formData);
}

/* FORMAT SIZE */
function formatSize(bytes) {
    let sizes = ["B","KB","MB","GB"];
    let i = 0;
    while(bytes >= 1024){
        bytes /= 1024;
        i++;
    }
    return bytes.toFixed(2) + " " + sizes[i];
}

/* LOAD LOGS */
async function loadLogs() {
    const res = await fetch(`${API_URL}/api/v1/transfers/`);
    const data = await res.json();

    const logs = document.getElementById("logs");
    logs.innerHTML = "";

    data.data.forEach(t => {

        // ✅ FIX: Use sender IP instead of localhost
        const downloadURL = `${API_URL}/api/v1/download/${t.filename}`;

        logs.innerHTML += `
        <tr>
            <td>${t.filename}</td>
            <td>${formatSize(t.filesize)}</td>
            <td>${t.peer_ip}</td>
            <td class="${t.status === 'success' ? 'success' : 'failed'}">${t.status}</td>
            <td>${t.timestamp}</td>
            <td>
                <a class="download-btn" href="${downloadURL}">
                    ⬇ Download
                </a>
            </td>
        </tr>`;
    });
}

setInterval(loadLogs, 3000);
loadLogs();

/* ================= CHAT ================= */

let lastMessageCount = 0;
let renderedMessages = new Set();

function appendMessageToUI(message, type, msg) {
    const chatBox = document.getElementById("chatBox");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;
    
    const prefix = type === "sent" ? "You" : "Peer";
    messageDiv.textContent = prefix + ": " + message;
    
    const uniqueKey = message + "_" + type;
    renderedMessages.add(uniqueKey);
    
    const isMine = (type === "sent") || (msg && msg.client_id === client_id);
    
    if (isMine) {
        messageDiv.style.background = "#22c55e";
        messageDiv.style.color = "black";
    } else {
        messageDiv.style.background = "#1f2937";
        messageDiv.style.color = "white";
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const message = document.getElementById("messageInput").value;
    const ip = document.getElementById("chatIp") ? document.getElementById("chatIp").value : document.getElementById("ip").value;
    const port = document.getElementById("chatPort") ? document.getElementById("chatPort").value : document.getElementById("port").value;

    if (!message.trim()) return;

    try {
        await fetch(`${API_URL}/api/v1/send-message/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                ip: ip,
                port: port,
                client_id: client_id
            })
        });
        
        // Wait for next loadMessages loop instead of manually appending
        // appendMessageToUI(message, "sent");
        document.getElementById("messageInput").value = "";
    } catch(err) {
        console.error("Failed to send message:", err);
    }
}

/* LOAD CHAT */
async function loadMessages() {
    const res = await fetch(`${API_URL}/api/v1/messages/`);
    const data = await res.json();

    if (data.length === lastMessageCount) {
        return;
    }

    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML = "";

    data.forEach(msg => {
        // Use true isMine check so we don't duplicate render if we don't want to skip sent ones
        const isMine = (msg.type === "sent") || (msg.client_id === client_id);
        const prefix = isMine ? "You" : "Peer";
        
        chatBox.innerHTML += `
            <div class="${isMine ? "message sent" : "message received"}">
                ${prefix}: ${msg.message}
            </div>
        `;
    });

    chatBox.scrollTop = chatBox.scrollHeight;
    lastMessageCount = data.length;
}

setInterval(loadMessages, 1000);
loadMessages();

/* VANTA BACKGROUND (UNCHANGED) */
VANTA.NET({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  color: 0x22c55e,
  backgroundColor: 0x020617
});