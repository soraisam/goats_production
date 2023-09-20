import { DEFAULT_SETTINGS } from './defaults.js';

// Loads the default settings on startup.
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("url").value = DEFAULT_SETTINGS.url;
  document.getElementById("port").value = DEFAULT_SETTINGS.port;
  document.getElementById("token").value = DEFAULT_SETTINGS.token;
});