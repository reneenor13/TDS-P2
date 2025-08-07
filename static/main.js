document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const responseEl = document.getElementById("response");
  responseEl.innerText = "Processing files, please wait...";
  
  const formData = new FormData(this);

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (data.answer) {
      // Pretty print JSON if it's a JSON array/string
      try {
        const parsed = JSON.parse(data.answer);
        responseEl.innerText = JSON.stringify(parsed, null, 2);
      } catch {
        responseEl.innerText = data.answer;
      }
    } else if (data.error) {
      responseEl.innerText = `Error: ${data.error}`;
    } else {
      responseEl.innerText = "No response from server.";
    }
  } catch (err) {
    responseEl.innerText = `Network or server error: ${err.message}`;
  }
});

async function askAI() {
  const question = document.getElementById("questionInput").value.trim();
  const responseEl = document.getElementById("response");

  if (!question) {
    responseEl.innerText = "Please enter a question first.";
    return;
  }

  responseEl.innerText = "Waiting for AI response...";

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();

    if (data.answer) {
      // Try pretty print if JSON
      try {
        const parsed = JSON.parse(data.answer);
        responseEl.innerText = JSON.stringify(parsed, null, 2);
      } catch {
        responseEl.innerText = data.answer;
      }
    } else if (data.error) {
      responseEl.innerText = `Error: ${data.error}`;
    } else {
      responseEl.innerText = "No response from server.";
    }
  } catch (err) {
    responseEl.innerText = `Network or server error: ${err.message}`;
  }
}
