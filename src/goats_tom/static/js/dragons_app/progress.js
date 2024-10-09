const PROGRESS_OPTIONS = {
  statusToColor: {
    queued: "bg-primary bg-opacity-25",
    initializing: "bg-primary bg-opacity-50",
    error: "bg-danger",
    running: "bg-primary",
    done: "bg-success",
    canceled: "bg-warning",
    default: "bg-secondary",
  },
};

/**
 * Responsible for creating the structure of the progress bar and its status element.
 */
class ProgressTemplate {
  /**
   * Creates the container and appends the progress and status elements.
   * @returns {HTMLElement} The container element.
   */
  create() {
    const container = this._createContainer();

    container.append(this._createProgress(), this._createStatus());

    return container;
  }

  /**
   * Creates the outer container for the progress bar.
   * @returns {HTMLElement} The container div.
   */
  _createContainer() {
    const div = Utils.createElement("div");
    return div;
  }

  /**
   * Creates the progress bar element.
   * @returns {HTMLElement} The progress bar element.
   */
  _createProgress() {
    const outerDiv = Utils.createElement("div", "progress");
    outerDiv.setAttribute("role", "progressbar");
    outerDiv.setAttribute("aria-label", "Recipe progress");
    outerDiv.setAttribute("aria-valuemin", "0");
    outerDiv.setAttribute("aria-valuemax", "100");

    const innerDiv = Utils.createElement("div", "progress-bar");
    innerDiv.style.width = "0";

    outerDiv.appendChild(innerDiv);

    return outerDiv;
  }

  /**
   * Creates the status element.
   * @returns {HTMLElement} The status paragraph element.
   */
  _createStatus() {
    const p = Utils.createElement("p", ["mb-0", "fst-italic"]);
    p.textContent = "Not Started";
    return p;
  }
}

/**
 * Manages the state of the progress bar, particularly the status.
 */
class ProgressModel {
  constructor() {
    this._status = null;
  }

  get status() {
    return this._status;
  }

  set status(value) {
    this._status = value;
  }

  /**
   * Clears the status, resetting it to null.
   */
  clear() {
    this._status = null;
  }
}

/**
 * Responsible for rendering and updating the visual representation of the progress bar and status.
 * @param {ProgressTemplate} template - The template for creating elements.
 * @param {HTMLElement} parentElement - The element to append the progress bar to.
 * @param {Object} options - The configuration options for the progress bar.
 */
class ProgressView {
  constructor(template, parentElement, options) {
    this.template = template;
    this.parentElement = parentElement;
    this.options = options;

    this.container = this._create();
    this.progress = this.container.querySelector(".progress-bar");
    this.status = this.container.querySelector("p");

    this.parentElement.appendChild(this.container);

    this.render = this.render.bind(this);
    this.bindCallback = this.bindCallback.bind(this);
  }

  /**
   * Creates the container by calling the template's create method.
   * @returns {HTMLElement} The container element.
   */
  _create() {
    const container = this.template.create();
    return container;
  }

  /**
   * Renders the view based on the given command and parameters.
   * @param {string} viewCmd - The command to render (e.g., "update").
   * @param {Object} parameter - The parameters required for rendering.
   */
  render(viewCmd, parameter) {
    switch (viewCmd) {
      case "update":
        this.update(parameter.status);
        break;
    }
  }

  // Placeholder for if needed in future.
  bindCallback() {}

  /**
   * Updates the progress bar's visual representation and status text based on the status.
   * @param {string} status - The current status of the progress bar.
   */
  update(status) {
    const colorClass =
      this.options.statusToColor[status] || this.options.statusToColor["default"];

    // Set the progress bar's width and color based on the status.
    this.progress.style.width = "100%";
    this.progress.className = `progress-bar ${colorClass}`;

    // Optionally, add animation class if not idle.
    if (status === "running" || status === "initializing") {
      this.progress.classList.add("placeholder-wave");
    } else {
      this.progress.classList.remove("placeholder-wave");
    }

    // Update the status text below the progress bar.
    this.status.textContent = Utils.formatDisplayText(status);
  }
}

/**
 * Handles the interaction between the model and the view.
 * @param {ProgressModel} model - The model representing the state.
 * @param {ProgressView} view - The view for rendering the progress bar.
 */
class ProgressController {
  constructor(model, view) {
    this.model = model;
    this.view = view;

    // Bind callbacks here.
  }

  /**
   * Updates the status in the model and triggers a re-render of the view.
   * @param {string} status - The new status of the progress bar.
   */
  update(status) {
    this.model.status = status;
    this.view.render("update", { status: this.model.status });
  }
}

/**
 * Initializes and manages the progress bar component.
 *
 * This class creates and manages a progress bar element that can be added to a webpage.
 * Users can update the progress bar's status to reflect different states (e.g., queued, running, done)
 * by calling the `update` method. The progress bar automatically applies the appropriate styling
 * and animations based on the provided status.
 *
 * @param {HTMLElement} parentElement - The element in which the progress bar will be created and displayed.
 * @param {Object} [options={}] - Optional configuration settings to customize the progress bar's behavior and appearance.
 */
class Progress {
  constructor(parentElement, options = {}) {
    this.options = { ...PROGRESS_OPTIONS, ...options };
    this.model = new ProgressModel();
    this.template = new ProgressTemplate();
    this.view = new ProgressView(this.template, parentElement, this.options);
    this.controller = new ProgressController(this.model, this.view);
  }

  /**
   * Updates the progress bar with the new status.
   * @param {string} status - The new status for the progress bar.
   */
  update(status) {
    this.controller.update(status);
  }
}
