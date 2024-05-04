class Logger {
  /**
   * Initializes a new instance of the Logger class.
   * @param {HTMLElement} container The DOM element where logs should be displayed.
   * @param {number} maxEntries The maximum number of log entries to maintain in the log view.
   */
  constructor(container, maxEntries = 100) {
    this.container = container;
    this.maxEntries = maxEntries;
  }

  /**
   * Logs messages to the container. Can handle both single message and an array of messages.
   * @param {string|string[]} messages The message or array of messages to log.
   */
  log(messages) {
    if (Array.isArray(messages)) {
      messages.forEach((message) => this.addLogEntry(message, type));
    } else {
      this.addLogEntry(messages);
    }
    this.trimLogEntries();
  }

  /**
   * Adds a single log entry to the log container.
   * @param {string} message The message to log.
   */
  addLogEntry(message) {
    const entry = document.createElement("div");
    entry.textContent = `${message}`;
    // entry.className = `alert alert-${type} mb-2`;

    this.container.appendChild(entry);
    this.container.scrollTop = this.container.scrollHeight; // Auto-scroll to the latest log entry.
  }

  /**
   * Ensures the number of log entries does not exceed the maximum set.
   */
  trimLogEntries() {
    while (this.container.children.length > this.maxEntries) {
      this.container.removeChild(this.container.firstChild);
    }
  }

  /**
   * Clears all logs from the log container.
   */
  clear() {
    this.container.innerHTML = ""; // Remove all child nodes
  }

  /**
   * Performs necessary cleanup when the logger is no longer needed.
   */
  teardown() {
    this.clear(); // Optionally clear logs on teardown
    // Further cleanup actions can be added here if necessary
  }
}
