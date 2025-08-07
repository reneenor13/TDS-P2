document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");
  const chatBox = document.getElementById("chatBox");
  const input = document.getElementById("userInput");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const userText = input.value.trim();
    if (!userText) return;

    appendMessage("You", userText, "user-msg");

    // Call your API here, for example:
    try {
      const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userText }),
      });
      const data = await response.json();

      appendMessage("AI", data.answer || "Sorry, no response.", "ai-msg");
    } catch (error) {
      appendMessage("AI", "Error fetching response.", "ai-msg");
    }

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
  });

  function appendMessage(sender, message, className) {
    const div = document.createElement("div");
    div.classList.add(className);
    div.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(div);
  }
});
