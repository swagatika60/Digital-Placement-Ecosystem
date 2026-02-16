function toggleCard() {
    document.getElementById("card").classList.toggle("flip");
}

function showLogin() {
    document.getElementById("landing").style.display = "none";
    document.getElementById("loginPage").style.display = "flex";
}
function showRegister() {
    document.getElementById("landing").style.display = "none";
    document.getElementById("registerPage").style.display = "flex";
}



/*function sendMessage() {
    const input = document.getElementById("chatInput");
    const message = input.value;
    if (!message) return;

    const chatBody = document.getElementById("chatBody");
    chatBody.innerHTML += `<p><b>You:</b> ${message}</p>`;

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
        chatBody.innerHTML += `<p><b>PrepMate AI:</b> ${data.reply}</p>`;
    });

    input.value = "";
    */
function openPage(page) {
  window.location.href = page;
}






function toggleChat() {
  let box = document.getElementById("chatbot");
  box.style.display = box.style.display === "none" ? "block" : "none";
}

document.getElementById("chatToggle").onclick = toggleChat;

function sendMessage() {
  let input = document.getElementById("chat-input");
  let msg = input.value.toLowerCase();
  if (msg === "") return;

  let body = document.getElementById("chat-body");
  body.innerHTML += `<p><b>You:</b> ${msg}</p>`;

  let reply = "I can guide you in Aptitude, DSA, Development, Projects & Placements.";

  if (msg.includes("aptitude")) {
    reply = `
    📊 Aptitude Roadmap:
    1. Percentages
    2. Profit & Loss
    3. Time & Work
    4. Probability
    Practice daily 30 mins.
    `;
  }
  else if (msg.includes("dsa")) {
    reply = `
    💻 DSA Steps:
    1. Arrays & Strings
    2. Sorting
    3. Recursion
    4. Linked List
    5. Stack & Queue
    `;
  }
  else if (msg.includes("project")) {
    reply = `
    🚀 Project Guide:
    • Portfolio Website
    • Pre-Placement Portal
    • Chatbot System
    • Full-Stack App
    Upload on GitHub.
    `;
  }
  else if (msg.includes("placement")) {
    reply = `
    🎯 Placement Plan:
    • Resume building
    • Aptitude + DSA
    • Mock interviews
    • Company-wise prep
    `;
  }
  else if (msg.includes("development")) {
    reply = `
    🌐 Development Path:
    HTML → CSS → JS
    React → Backend
    MongoDB → Deployment
    `;
  }

  body.innerHTML += `<p><b>Guide:</b> ${reply}</p>`;
  body.scrollTop = body.scrollHeight;
  input.value = "";
}



  const lines = [
    "Hey there 👋",
    "I'm your AI Placement Assistant 🤖",
    "Preparing you for real placements 🚀"
  ];

  let lineIndex = 0;
  let charIndex = 0;
  const speed = 90;
  const hold = 1600;

  const textEl = document.getElementById("ai-text");

  function type() {
    if (charIndex < lines[lineIndex].length) {
      textEl.textContent += lines[lineIndex].charAt(charIndex);
      charIndex++;
      setTimeout(type, speed);
    } else {
      setTimeout(erase, hold);
    }
  }

  function erase() {
    if (charIndex > 0) {
      textEl.textContent = lines[lineIndex].substring(0, charIndex - 1);
      charIndex--;
      setTimeout(erase, 40);
    } else {
      lineIndex = (lineIndex + 1) % lines.length;
      setTimeout(type, 300);
    }
  }

  type();


      






