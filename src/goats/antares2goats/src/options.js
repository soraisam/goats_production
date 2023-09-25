// Import default settings to use.
import { DEFAULT_SETTINGS } from './defaults.js';

/**
 * A lookup table for hosts and ports.
 * @type {Object}
 */
const URL_PORT_LOOKUP = {
  goats: { url: DEFAULT_SETTINGS.url, port: DEFAULT_SETTINGS.port },
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
 * Handles the click event for the save button, saving the current token, URL,
 * and port to storage.
 */
function handleSaveClick() {
  const url = document.getElementById("url").value;
  const port = document.getElementById("port").value;
  const token = document.getElementById("token").value;
  chrome.storage.local.set({ url, port, token, }, () => {
    // Display a "Settings Saved" message
    const saveMessage = document.createElement("div");
    saveMessage.textContent = "Settings Saved.";
    document.body.appendChild(saveMessage);
  });
}

/**
 * Loads the previously saved URL, port, and token when the options page is
 * loaded.
 */
const loadPreviousSettings = () => {
  chrome.storage.local.get(["url", "port", "token"], (items) => {
    document.getElementById("url").value = items.url || DEFAULT_SETTINGS.url;
    document.getElementById("port").value = items.port || DEFAULT_SETTINGS.port;
    document.getElementById("token").value = items.token || DEFAULT_SETTINGS.token;
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
