/**
 * A lookup table for hosts and ports.
 * @type {Object}
 */
const URL_PORT_LOOKUP = {
  goats: { url: "localhost", port: "8000" },
  other: { url: "", port: "" },
};

/**
 * Handles the change event for the radio group, updating the URL and port
 * fields based on the selected radio button.
 *
 * @param {Event} event - The change event.
 */
function handleRadioChange(event) {
  const urlField = document.getElementById("url");
  const portField = document.getElementById("port");
  const { url, port } = URL_PORT_LOOKUP[event.target.id];
  urlField.value = url;
  portField.value = port;
}

/**
 * Handles the click event for the save button, saving the current URL and
 * port to storage.
 */
function handleSaveClick() {
  const url = document.getElementById("url").value;
  const port = document.getElementById("port").value;
  chrome.storage.local.set({ url, port }, () => {
    // Display a "Settings Saved" message
    const saveMessage = document.createElement("div");
    saveMessage.textContent = "Settings Saved. Closing...";
    document.body.appendChild(saveMessage);
  });

  // Close the options window after a short delay.
  setTimeout(() => {
    window.close();
  }, 1000);
}

/**
 * Loads the previously saved URL and port when the options page is loaded.
 */
const loadPreviousSettings = () => {
  chrome.storage.local.get(["url", "port"], (items) => {
    document.getElementById("url").value = items.url || "";
    document.getElementById("port").value = items.port || "";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementsByName("mode").forEach((radioButton) => {
    radioButton.addEventListener("change", handleRadioChange);
  });

  document.getElementById("saveButton").addEventListener("click", handleSaveClick);
});

// Load the previously saved settings when the options page is loaded.
window.onload = loadPreviousSettings;
