class Utils {
  static capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
  }

  static isEmpty(obj) {
    return Object.keys(obj).length === 0 && obj.constructor === Object;
  }

  /**
   * Creates a new HTML element with optional class names.
   * @param {string} tag The tag name of the element to create.
   * @param {string | string[]} classNames The class name(s) to add to the element.
   * @returns {Element} The newly created element.
   */
  static createElement(tag, classNames) {
    const element = document.createElement(tag);
    if (classNames) {
      if (Array.isArray(classNames)) {
        element.classList.add(...classNames);
      } else {
        element.classList.add(classNames);
      }
    }
    return element;
  }

  /**
   * Creates a modal for displaying content.
   * @param {string} name The name to assign to elements within the modal for unique referencing.
   * @returns {Object} An object containing methods to manipulate the modal.
   */
  static createModal(name) {
    // Append modals to a default container.
    const element = document.getElementById("modalContainer");

    // Create IDs for reference.
    const modalId = `${name}Modal`;
    const modalHeaderTitleId = `${modalId}HeaderTitle`;

    // Create the main modal element.
    const modal = this.createElement("div", ["modal", "fade"]);
    modal.id = modalId;
    modal.setAttribute("tabindex", "-1");
    modal.setAttribute("aria-labelledby", modalHeaderTitleId);
    modal.setAttribute("aria-hidden", "true");

    // Create the modal dialog.
    const modalDialog = this.createElement("div", [
      "modal-dialog",
      "modal-dialog-centered",
      "modal-dialog-scrollable",
      "modal-lg",
    ]);

    // Create the modal content container.
    const modalContent = this.createElement("div", "modal-content");

    // Create and append the modal header.
    const modalHeader = this.createElement("div", "modal-header");
    const modalHeaderTitle = this.createElement("h5", "modal-title");
    modalHeaderTitle.id = modalHeaderTitleId;

    const closeButton = this.createElement("button", "btn-close");
    closeButton.setAttribute("data-dismiss", "modal");
    closeButton.setAttribute("aria-label", "Close");
    modalHeader.appendChild(modalHeaderTitle);
    modalHeader.appendChild(closeButton);

    // Create the modal body.
    const modalBody = this.createElement("div", "modal-body");

    // Append the header and body to the modal content.
    modalContent.appendChild(modalHeader);
    modalContent.appendChild(modalBody);

    // Append the modal content to the modal dialog.
    modalDialog.appendChild(modalContent);

    // Append the modal dialog to the main modal element.
    modal.appendChild(modalDialog);

    // Append the modal to the document body.
    element.appendChild(modal);

    // Initialize the modal with Bootstrap's JavaScript and return the modal instance.
    const bootstrapModal = new bootstrap.Modal(modal);
    // Return an object that can manipulate the modal.
    return {
      modalInstance: bootstrapModal,
      updateTitle: (newTitle) => {
        modalHeaderTitle.textContent = newTitle;
      },
      updateBody: (newContent) => {
        modalBody.innerHTML = "";
        modalBody.appendChild(newContent);
      },
      show: () => {
        bootstrapModal.show();
      },
      hide: () => {
        bootstrapModal.hide();
      },
    };
  }

  /**
   * Escapes HTML characters to prevent XSS and ensure proper display of text.
   * @param {string} str The string to escape.
   * @returns {string} The escaped HTML string.
   */
  static escapeHTML(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  /**
   * Formats a snake_case string into a human-readable title format with spaces and capitalization.
   * @param {string} text The text to format, typically a key from a documentation object.
   * @returns {string} The formatted text with underscores replaced by spaces and each word
   * capitalized.
   */
  static formatDisplayText(text) {
    return text
      .toLowerCase()
      .replace(/_/g, " ")
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }
}
