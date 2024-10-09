/**
 * Responsible for creating the modal's HTML structure.
 * @param {Object} options - Configuration options for the modal, including the ID.
 */
class ModalTemplate {
  constructor(options) {
    this.options = options;
  }

  /**
   * Creates the HTML structure of the modal.
   * @returns {HTMLElement} The container with the modal HTML inside.
   */
  create() {
    const container = this._createContainer();
    const modalId = `${this.options.id}`;
    const modalHeaderId = `header${modalId}`;

    const html = `
      <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalHeaderId}" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-lg">
          <div class="modal-content">
            <div class="modal-header" id=${modalHeaderId}>
              <h5 class="modal-title"></h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
            </div>
          </div>
        </div>
      </div>
    `;
    container.innerHTML = html;

    return container;
  }

  /**
   * Creates a container div for holding the modal.
   * @returns {HTMLElement} The container element.
   * @private
   */
  _createContainer() {
    const container = Utils.createElement("div");
    return container;
  }
}

/**
 * Responsible for holding modal data if needed.
 */
class ModalModel {}

/**
 * Handles rendering and updating the modal in the DOM.
 * @param {ModalTemplate} template - The template object used for creating the modal's structure.
 * @param {HTMLElement} parentElement - The parent element where the modal will be appended.
 * @param {Object} options - Configuration options for the modal.
 */
class ModalView {
  constructor(template, parentElement, options) {
    this.template = template;
    this.parentElement = parentElement;
    this.options = options;
    this.container = this._create();
    this.modal = this.container.querySelector(".modal");
    this.modalTitle = this.modal.querySelector(".modal-title");
    this.modalBody = this.modal.querySelector(".modal-body");
    this.bootstrapModal = new bootstrap.Modal(this.modal);

    this.parentElement.appendChild(this.container);
  }

  /**
   * Creates and returns the modal using the template.
   * @returns {HTMLElement} The modal element.
   * @private
   */
  _create() {
    return this.template.create();
  }

  /**
   * Renders the modal based on the command provided.
   * @param {string} viewCmd - The command for what action to take (e.g., 'show', 'hide', 'update').
   * @param {Object} parameter - Parameters for the update action (title, body).
   */
  render(viewCmd, parameter) {
    switch (viewCmd) {
      case "show":
        this._show();
        break;
      case "hide":
        this._hide();
        break;
      case "update":
        this._update(parameter.title, parameter.body);
        break;
    }
  }

  /**
   * Shows the modal.
   * @private
   */
  _show() {
    this.bootstrapModal.show();
  }

  /**
   * Hides the modal.
   * @private
   */
  _hide() {
    this.bootstrapModal.hide();
  }

  /**
   * Updates the modal's title and body content.
   * @param {string} title - The new title for the modal.
   * @param {HTMLElement|string} body - The new body content for the modal.
   * @private
   */
  _update(title, body) {
    this._updateTitle(title);
    this._updateBody(body);
  }

  /**
   * Updates the modal's title.
   * @param {string} title - The new title.
   * @private
   */
  _updateTitle(title) {
    this.modalTitle.textContent = title;
  }

  /**
   * Updates the modal's body content.
   * @param {HTMLElement|string} body - The new body content (either as a DOM element or a string).
   * @private
   */
  _updateBody(body) {
    this._clearBody();
    this._clearBody();
    if (typeof body === "string") {
      // If it's a string, directly insert as HTML.
      this.modalBody.innerHTML = body;
    } else {
      // If it's a DOM element, append it.
      this.modalBody.appendChild(body);
    }
  }

  /**
   * Clears the current body content of the modal.
   * @private
   */
  _clearBody() {
    this.modalBody.innerHTML = "";
  }
}

/**
 * Controls the logic between the model and view.
 * @param {ModalModel} model - The model that holds modal data.
 * @param {ModalView} view - The view that handles rendering the modal.
 * @param {Object} options - Configuration options for the modal.
 */
class ModalController {
  constructor(model, view, options) {
    this.model = model;
    this.view = view;
    this.options = options;
  }

  /**
   * Updates the modal's title and body.
   * @param {string} title - The new title for the modal.
   * @param {HTMLElement|string} body - The new body content for the modal.
   */
  update(title, body) {
    this.view.render("update", { title, body });
  }

  /**
   * Shows the modal.
   */
  show() {
    this.view.render("show");
  }

  /**
   * Hides the modal.
   */
  hide() {
    this.view.render("hide");
  }
}

/**
 * Creates a modal to display data.
 * @param {HTMLElement} parentElement - The parent element where the modal will be appended.
 * @param {Object} options - Configuration options for the modal (e.g., id, title).
 */
class Modal {
  static #defaultOptions = {
    id: "Modal",
  };

  constructor(parentElement, options = {}) {
    this.options = { ...Modal.#defaultOptions, ...options };
    this.model = new ModalModel(this.options);
    this.template = new ModalTemplate(this.options);
    this.view = new ModalView(this.template, parentElement, this.options);
    this.controller = new ModalController(this.model, this.view, this.options);
  }

  /**
   * Updates the modal's title and body content.
   * @param {string} title - The new title for the modal.
   * @param {HTMLElement|string} body - The new body content for the modal.
   */
  update(title, body) {
    this.controller.update(title, body);
  }

  /**
   * Shows the modal.
   */
  show() {
    this.controller.show();
  }

  /**
   * Hides the modal.
   */
  hide() {
    this.controller.hide();
  }
}
