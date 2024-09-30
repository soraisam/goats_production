const LOGGER_OPTIONS = {
  maxEntries: 500,
};

/**
 * Model for Logger, potentially for future expansion.
 */ class LoggerModel {}

/**
 * Template handling HTML structure for logger components.
 */
class LoggerTemplate {
  /**
   * Creates a single log entry DOM element.
   * @param {string} data The log message.
   * @returns {HTMLElement} A div element containing the log message.
   */
  createLogEntry(data) {
    const div = Utils.createElement("div");
    div.textContent = `${data}`;

    return div;
  }

  /**
   * Creates the container for log entries.
   * @returns {HTMLElement} A div configured as a log container.
   */
  createContainer() {
    const div = Utils.createElement("div", ["log-container", "log-overflow"]);
    return div;
  }
}

/**
 * View for Logger, manages rendering of log entries.
 * @param {LoggerTemplate} template Instance of LoggerTemplate to render log entries.
 * @param {HTMLElement} parentElement Container where the logger will be appended.
 * @param {Object} options Configuration options passed to the view.
 */
class LoggerView {
  constructor(template, parentElement, options) {
    this.template = template;
    this.parentElement = parentElement;
    this.options = options;

    this.container = this._create();

    this.parentElement.appendChild(this.container);

    this.render = this.render.bind(this);
    this.bindCallback = this.bindCallback.bind(this);
  }

  /**
   * Initializes the log container.
   * @private
   * @returns {HTMLElement} The container element.
   */
  _create() {
    const container = this.template.createContainer();
    return container;
  }

  /**
   * Renders changes in the view based on commands.
   * @param {string} viewCmd The command that dictates the action to be taken.
   * @param {Object} parameter Parameters needed for the command.
   */
  render(viewCmd, parameter) {
    switch (viewCmd) {
      case "log":
        this.log(parameter.messages);
        break;
      case "clear":
        this.clear();
        break;
    }
  }

  // Placeholder for if needed in future.
  bindCallback() {}

  /**
   * Clears the log display.
   */
  clear() {
    this.container.innerHTML = ``;
  }

  /**
   * Logs messages to the container. Handles both single messages and arrays.
   * @param {string|string[]} messages The messages to log.
   */
  log(messages) {
    // Check if the log viewer is scrolled to the bottom before adding new entries.
    // This is important to decide whether to auto-scroll after appending new log entries.
    const isScrolledToBottom = this._isScrolledToBottom();
    const fragment = document.createDocumentFragment();

    const processMessage = (message) => {
      const entry = this.template.createLogEntry(message);
      fragment.appendChild(entry);
    };

    Array.isArray(messages)
      ? messages.forEach(processMessage)
      : processMessage(messages);

    this.container.appendChild(fragment);

    // Scroll to bottom only if user hasn't scrolled up.
    if (isScrolledToBottom) {
      this._scrollToBottom();
    }

    this._trimLogEntries();
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
   * Scrolls the log container to the bottom.
   * @private
   */
  _scrollToBottom() {
    this.container.scrollTop = this.container.scrollHeight;
  }

  /**
   * Ensures the number of log entries does not exceed the maximum set.
   * @private
   */
  _trimLogEntries() {
    while (this.container.children.length > this.options.maxEntries) {
      this.container.removeChild(this.container.firstChild);
    }
  }
}

/**
 * Controller for Logger, handles business logic and data management.
 * @param {LoggerModel} model The model for logger data.
 * @param {LoggerView} view The view for the logger.
 */
class LoggerController {
  constructor(model, view) {
    this.model = model;
    this.view = view;

    // No callbacks to bind.
  }

  /**
   * Logs a message or array of messages.
   * @param {string|string[]} messages The messages to log.
   */
  log(messages) {
    this.view.render("log", { messages });
  }

  /**
   * Clears all log entries.
   */
  clear() {
    this.view.render("clear");
  }
}

/**
 * Logger is a comprehensive logging utility that can be embedded within web applications
 * to display runtime messages. It is designed to provide a real-time log output to a specified
 * DOM element.
 * @param {HTMLElement} parentElement The parent element where the logger will be appended.
 * @param {Object} [options={}] Configuration options for logger behavior.
 */
class Logger {
  constructor(parentElement, options = {}) {
    this.options = { ...LOGGER_OPTIONS, ...options };
    this.model = new LoggerModel();
    this.template = new LoggerTemplate();
    this.view = new LoggerView(this.template, parentElement, options);
    this.controller = new LoggerController(this.model, this.view);
  }

  /**
   * Log messages.
   * @param {string|string[]} messages The messages to log.
   */
  log(messages) {
    this.controller.log(messages);
  }

  /**
   * Clear the log.
   */
  clear() {
    this.controller.clear();
  }
}