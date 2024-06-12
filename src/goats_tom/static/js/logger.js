const MAX_LOG_ENTRIES = 500;

class Logger {
  /**
   * Initializes a new instance of the Logger class.
   * @param {HTMLElement} container The DOM element where logs should be displayed.
   * @param {number} maxEntries The maximum number of log entries to maintain in the log view.
   */
  constructor(container, maxEntries = MAX_LOG_ENTRIES) {
    this.container = container;
    this.maxEntries = maxEntries;
  }

  /**
   * Logs messages to the container. Can handle both single message and an array of messages.
   * @param {string|string[]} messages The message or array of messages to log.
   */
  log(messages) {
    // Check if the log viewer is scrolled to the bottom before adding new entries.
    // This is important to decide whether to auto-scroll after appending new log entries.
    const shouldScroll = this._isScrolledToBottom();

    if (Array.isArray(messages)) {
      messages.forEach((message) => this._addLogEntry(message, type));
    } else {
      this._addLogEntry(messages);
    }

    // Scroll to bottom only if user hasn't scrolled up.
    if (shouldScroll) {
      this.container.scrollTop = this.container.scrollHeight;
    }

    this._trimLogEntries();
  }

  /**
   * Adds a single log entry to the log container.
   * @private
   * @param {string} message The message to log.
   */
  _addLogEntry(message) {
    const entry = document.createElement("div");
    entry.textContent = `${message}`;
    // entry.className = `alert alert-${type} mb-2`;

    this.container.appendChild(entry);
  }

  /**
   * Determines if the scroll position is at the bottom of the container.
   * This is calculated by checking if the difference between the container's scroll height and its
   * client height is less than or equal to the current scroll top position plus a small tolerance
   * (1 pixel in this case). This tolerance helps account for fractional pixel differences that can
   * occur in some browsers.
   * @private
   * @returns {boolean} True if the scrollbar is at the bottom, false otherwise.
   */
  _isScrolledToBottom() {
    return (
      this.container.scrollHeight - this.container.clientHeight <=
      this.container.scrollTop + 1
    );
  }

  /**
   * Ensures the number of log entries does not exceed the maximum set.
   * @private
   */
  _trimLogEntries() {
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
}
