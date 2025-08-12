// Handle file uploads
document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const uploadResponseEl = document.getElementById("uploadResponse");
  uploadResponseEl.innerText = "Processing files, please wait...";
  
  const formData = new FormData(this);

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (data.answer) {
      // Pretty print JSON if it's valid JSON
      try {
        const parsed = JSON.parse(data.answer);
        uploadResponseEl.innerText = JSON.stringify(parsed, null, 2);
      } catch {
        uploadResponseEl.innerText = data.answer;
      }
    } else if (data.error) {
      uploadResponseEl.innerText = `Error: ${data.error}`;
    } else {
      uploadResponseEl.innerText = "No response from server.";
    }
  } catch (err) {
    uploadResponseEl.innerText = `Network or server error: ${err.message}`;
  }
});

// Handle "Ask AI" button click
document.getElementById("askBtn").addEventListener("click", async () => {
  const question = document.getElementById("userQuestion").value.trim();
  const chatResponseEl = document.getElementById("chatResponse");

  if (!question) {
    chatResponseEl.innerText = "Please enter a question first.";
    return;
  }

  chatResponseEl.innerText = "Waiting for AI response...";

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();

    if (data.answer) {
      try {
        const parsed = JSON.parse(data.answer);
        chatResponseEl.innerText = JSON.stringify(parsed, null, 2);
      } catch {
        chatResponseEl.innerText = data.answer;
      }
    } else if (data.error) {
      chatResponseEl.innerText = `Error: ${data.error}`;
    } else {
      chatResponseEl.innerText = "No response from server.";
    }
  } catch (err) {
    chatResponseEl.innerText = `Network or server error: ${err.message}`;
  }
});
