/**
 * Manages the behavior and display of a bootstrap offcanvas component for showing help information.
 */
class HelpOffcanvas {
  /**
   * Constructs a HelpOffcanvas instance attached to a specified parent element.
   * @param {HTMLElement} parentElement The container where the offcanvas will be appended.
   */
  constructor(parentElement) {
    this.parentElement = parentElement;
    this.id = "helpOffcanvas";
    this.titleElement = null;
    this.loadingElement = null;
    this.contentElement = null;
    this.offcanvas = this._createOffcanvas();
    this.parentElement.appendChild(this.offcanvas);
    this.bsOffcanvas = new bootstrap.Offcanvas(this.offcanvas);
  }

  /**
   * Creates the offcanvas HTML structure and returns the element.
   * @private
   * @returns {HTMLElement} The fully constructed offcanvas element.
   */
  _createOffcanvas() {
    const offcanvas = Utils.createElement("div", ["offcanvas", "offcanvas-end"]);
    offcanvas.setAttribute("data-bs-scroll", "true");
    offcanvas.setAttribute("data-bs-backdrop", "false");
    offcanvas.setAttribute("tabindex", "-1");
    offcanvas.setAttribute("aria-labelledby", `${this.id}Title`);
    offcanvas.id = this.id;

    const header = Utils.createElement("div", "offcanvas-header");
    const title = Utils.createElement("h5", "offcanvas-title");
    title.id = `${this.id}Title`;
    this.titleElement = title; // Store reference to title element.

    const closeButton = Utils.createElement("button", ["btn", "btn-close"]);
    closeButton.setAttribute("type", "button");
    closeButton.setAttribute("data-bs-dismiss", "offcanvas");
    closeButton.setAttribute("aria-label", "Close");

    const body = Utils.createElement("div", "offcanvas-body");
    const helpContentDiv = Utils.createElement("div");
    this.contentElement = helpContentDiv; // Store reference to content element.

    const loadingDiv = Utils.createElement("div", ["d-flex", "justify-content-center"]);
    const spinner = Utils.createElement("div", "spinner-border");
    spinner.setAttribute("role", "status");
    const sr = Utils.createElement("span", "sr-only");
    sr.textContent = "Loading...";
    loadingDiv.appendChild(spinner);
    loadingDiv.appendChild(sr);
    this.loadingElement = loadingDiv; // Store reference to loading element.

    body.appendChild(helpContentDiv);
    body.appendChild(loadingDiv);

    header.appendChild(title);
    header.appendChild(closeButton);
    offcanvas.appendChild(header);
    offcanvas.appendChild(body);

    return offcanvas;
  }

  /**
   * Sets the title of the offcanvas.
   * @param {string} text The text to set as the offcanvas title.
   */
  setTitle(text) {
    this.titleElement.textContent = text;
  }

  /**
   * Sets the HTML content of the offcanvas.
   * @param {string} htmlContent The HTML string to display inside the offcanvas.
   */
  setContent(htmlContent) {
    this.contentElement.innerHTML = htmlContent;
  }

  /**
   * Updates the title and content of the offcanvas and shows it.
   * @param {string} title The new title of the offcanvas.
   * @param {string} htmlContent The new HTML content of the offcanvas.
   */
  updateAndShow(title, htmlContent) {
    this.setTitle(title);
    this.setContent(htmlContent);
    this.showContent();
  }

  /**
   * Shows the content of the offcanvas, hiding the loading indicator.
   */
  showContent() {
    this.loadingElement.classList.add("d-none");
    this.contentElement.classList.remove("d-none");
  }

  /**
   * Shows the loading indicator and hides the content.
   */
  isLoading() {
    this.contentElement.classList.add("d-none");
    this.loadingElement.classList.remove("d-none");
  }

  /**
   * Displays the offcanvas.
   */
  show() {
    this.bsOffcanvas.show();
  }

  /**
   * Hides the offcanvas.
   */
  hide() {
    this.bsOffcanvas.hide();
  }

  /**
   * Clears the title and content of the offcanvas.
   */
  clearTitleAndContent() {
    this.titleElement.textContent = "";
    this.contentElement.innerHTML = "";
  }
}
