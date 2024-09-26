const OUTPUT_FILES_ID = "OutputFiles";

class OutputFilesTemplate {
  /**
   * Creates a card container.
   * @return {HTMLElement} The card element.
   */
  createCard() {
    const card = Utils.createElement("div", ["card"]);
    card.appendChild(this.createCardBody());

    return card;
  }

  /**
   * Creates the body section of the card.
   * @return {HTMLElement} The card body element.
   */
  createCardBody() {
    const cardBody = Utils.createElement("div", ["card-body"]);
    cardBody.appendChild(this.createAccordion());

    return cardBody;
  }

  /**
   * Creates an accordion for collapsible content.
   * @return {HTMLElement} The accordion element.
   */
  createAccordion() {
    const accordion = Utils.createElement("div", ["accordion"]);
    const accordionId = `accordion${OUTPUT_FILES_ID}`;
    accordion.id = accordionId;

    const header = Utils.createElement("h6", ["accordion-header"]);
    const headerId = `header${OUTPUT_FILES_ID}`;
    header.id = headerId;

    const button = Utils.createElement("button");
    const collapseId = `collapse${OUTPUT_FILES_ID}`;
    button.className = "accordion-button collapsed";
    button.setAttribute("type", "button");
    button.setAttribute("data-bs-toggle", "collapse");
    button.setAttribute("data-bs-target", `#${collapseId}`);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", collapseId);
    button.textContent = "Output Files";

    header.appendChild(button);

    const collapseDiv = Utils.createElement("div");
    collapseDiv.id = collapseId;
    collapseDiv.className = "accordion-collapse collapse";
    collapseDiv.setAttribute("aria-labelledby", headerId);
    collapseDiv.setAttribute("data-bs-parent", `#${accordionId}`);

    const accordionBody = Utils.createElement("div", [
      "accordion-body",
      "accordion-body-overflow",
    ]);
    accordionBody.append(
      this.createToolbar(),
      this.createTable(),
      this.createLoadingDiv()
    );

    collapseDiv.appendChild(accordionBody);
    accordion.append(header, collapseDiv);

    return accordion;
  }

  /**
   * Creates a table for displaying data.
   * @return {HTMLElement} The table element.
   */
  createTable() {
    const table = Utils.createElement("table", [
      "table",
      "table-borderless",
      "table-sm",
      "table-striped",
    ]);
    table.append(this.createTHeadDefault(), this.createTBodyDefault());

    return table;
  }

  /**
   * Creates a loading indicator element.
   * @return {HTMLElement} The loading div element with a spinner.
   */
  createLoadingDiv() {
    const div = Utils.createElement("div", ["d-none", "text-center"]);
    div.id = `loading${OUTPUT_FILES_ID}`;
    const spinner = Utils.createElement("div", ["spinner-border", "text-secondary"]);
    const spinnerInner = Utils.createElement("span", ["visually-hidden"]);
    spinnerInner.textContent = "Loading ...";

    spinner.appendChild(spinnerInner);
    div.appendChild(spinner);

    return div;
  }

  /**
   * Creates a default tbody element.
   * @return {HTMLElement} The newly created tbody element.
   */
  createTBodyDefault() {
    const tbody = Utils.createElement("tbody");

    return tbody;
  }

  /**
   * Creates a toolbar containing action buttons.
   * @return {HTMLElement} The toolbar element containing buttons.
   */
  createToolbar() {
    const div = Utils.createElement("div");
    div.id = `toolbar${OUTPUT_FILES_ID}`;
    const row = Utils.createElement("div", ["row", "g-3"]);
    const col = Utils.createElement("div", ["col", "text-end"]);

    const refreshButton = Utils.createElement("button", [
      "btn",
      "btn-secondary",
      "btn-sm",
    ]);
    refreshButton.textContent = " Refresh";
    refreshButton.dataset.action = "refresh";

    // Create and prepend the icon.
    const refreshIcon = Utils.createElement("i", ["fa-solid", "fa-arrow-rotate-right"]);
    refreshButton.prepend(refreshIcon);

    col.append(refreshButton);
    row.append(col);
    div.append(row);

    return div;
  }

  /**
   * Creates a default thead element.
   * @return {HTMLElement} The newly created thead element.
   */
  createTHeadDefault() {
    const thead = Utils.createElement("thead");
    const tr = Utils.createElement("tr");

    // Creating a cell.
    const thName = Utils.createElement("th", ["fw-normal"]);
    thName.setAttribute("scope", "col");
    thName.textContent = "Filename";
    thName.id = `thName${OUTPUT_FILES_ID}`;

    // Create cell for last modified.
    const thLastModified = Utils.createElement("th", ["fw-normal"]);
    thLastModified.setAttribute("scope", "col");
    thLastModified.textContent = "Last Modified (UTC)";

    // Create another cell.
    const thAdd = Utils.createElement("th", ["text-end", "fw-normal"]);
    thAdd.setAttribute("scope", "col");
    thAdd.textContent = "Add To Data Products";

    // Create remove cell.
    const thRemove = Utils.createElement("th", ["text-end", "fw-normal"]);
    thRemove.setAttribute("scope", "col");
    thRemove.textContent = "Delete";

    tr.append(thName, thLastModified, thAdd, thRemove);
    thead.appendChild(tr);

    return thead;
  }

  /**
   * Creates a tbody element populated with data rows.
   * @param {Array} data - The data to populate the tbody with.
   * @return {HTMLElement} The tbody element filled with data rows.
   */
  createTBodyData(data) {
    const tbody = Utils.createElement("tbody");
    if (data.length === 0) {
      // If no data, show a message row
      const tr = Utils.createElement("tr");
      const td = Utils.createElement("td");
      td.setAttribute("colspan", "4");
      td.textContent = "No files found...";
      tr.appendChild(td);
      tbody.appendChild(tr);
      return tbody;
    }

    // Loop through each item in the data array to create table rows.
    data.forEach((item) => {
      const tr = Utils.createElement("tr");
      tr.dataset.filename = item.name;
      tr.dataset.filepath = item.path;
      tr.dataset.productId = item.product_id;

      // Create the filename cell with a data attribute.
      const tdFilename = Utils.createElement("td");
      tdFilename.textContent = item.name;

      // Create a last modified cell.
      const tdLastModified = Utils.createElement("td");
      tdLastModified.textContent = item.last_modified;

      // Create the add to data products button cell.
      const tdAdd = Utils.createElement("td", ["text-end"]);

      if (item.is_dataproduct) {
        // If item is a data product, just show a check icon as text.
        const checkIcon = Utils.createElement("i", [
          "fa-solid",
          "fa-circle-check",
          "text-success",
        ]);
        tdAdd.appendChild(checkIcon);
      } else {
        // Otherwise, create a clickable button to add to data products.
        const addButton = Utils.createElement("a", ["link-secondary"]);
        addButton.setAttribute("type", "button");
        addButton.setAttribute("data-action", "add");

        // Create icon element for button.
        const icon = Utils.createElement("i", ["fa-solid", "fa-circle-plus"]);
        addButton.appendChild(icon);

        tdAdd.appendChild(addButton);
      }

      // Build the remove icon.
      const tdRemove = Utils.createElement("td", ["text-end"]);
      const removeButton = Utils.createElement("a", ["link-danger"]);
      removeButton.setAttribute("type", "button");
      removeButton.setAttribute("data-action", "remove");

      // Create icon element for button.
      const icon = Utils.createElement("i", ["fa-solid", "fa-trash-can"]);
      removeButton.appendChild(icon);
      tdRemove.appendChild(removeButton);

      // Append the cells to the row.
      tr.append(tdFilename, tdLastModified, tdAdd, tdRemove);

      // Append the row to the tbody.
      tbody.appendChild(tr);
    });

    return tbody;
  }
}

class OutputFilesView {
  constructor(template, parentElement) {
    this.template = template;
    this.parentElement = parentElement;

    this.card = this._create();
    this.body = this.card.querySelector(".accordion-body");
    this.table = this.card.querySelector("table");
    this.tbody = this.card.querySelector("tbody");
    this.thead = this.card.querySelector("thead");
    this.loadingDiv = this.card.querySelector(`#loading${OUTPUT_FILES_ID}`);
    this.toolbar = this.card.querySelector(`#toolbar${OUTPUT_FILES_ID}`);

    this.parentElement.appendChild(this.card);

    this.render = this.render.bind(this);
    this.bindCallback = this.bindCallback.bind(this);
  }

  /**
   * Creates the card component using the template.
   * @return {HTMLElement} The created card element.
   */
  _create() {
    const card = this.template.createCard();

    return card;
  }

  /**
   * Updates the table with new data.
   * @param {Array} data - The new data to render in the table.
   */
  update(data) {
    const newTbody = this.template.createTBodyData(data);
    this.table.replaceChild(newTbody, this.tbody);
    this.tbody = newTbody;

    // Update the file count.
    this.thead.querySelector(
      `#thName${OUTPUT_FILES_ID}`
    ).textContent = `Filename ${Utils.getFileCountLabel(data.length)}`;
  }

  /**
   * Shows the loading animation and hides the data table.
   */
  loading() {
    this.table.classList.add("d-none");
    this.loadingDiv.classList.remove("d-none");
    this._toggleToolbarButtonsDisabled(true);
  }

  /**
   * Hides the loading animation and shows the data table.
   */
  loaded() {
    this.table.classList.remove("d-none");
    this.loadingDiv.classList.add("d-none");
    this._toggleToolbarButtonsDisabled(false);
  }

  /**
   * Toggles the disabled state of all buttons in the toolbar.
   * @param {boolean} disable - True to disable the buttons, false to enable them.
   */
  _toggleToolbarButtonsDisabled(disable) {
    const buttons = this.toolbar.querySelectorAll("button");
    buttons.forEach((button) => (button.disabled = disable));
  }

  /**
   * Renders changes to the view based on a command.
   * @param {string} viewCmd - The command that dictates the rendering action.
   * @param {Object} parameter - Parameters used for rendering.
   */
  render(viewCmd, parameter) {
    switch (viewCmd) {
      case "update":
        this.update(parameter.data);
        break;
      case "loading":
        this.loading();
        break;
      case "loaded":
        this.loaded();
        break;
      case "error":
        console.log("View found error.");
        break;
    }
  }

  /**
   * Binds a callback to an event on the table.
   * @param {string} event - The event to bind.
   * @param {Function} handler - The callback function to execute on event trigger.
   */
  bindCallback(event, handler) {
    const selector = `[data-action="${event}"]`;
    switch (event) {
      case "add":
        Utils.delegate(this.table, selector, "click", (e) => {
          // Find the closest table row to the event target.
          const row = e.target.closest("tr");
          if (!row) return;
          handler({
            filename: row.dataset.filename,
            filepath: row.dataset.filepath,
          });
        });
        break;
      case "remove":
        Utils.delegate(this.table, selector, "click", (e) => {
          // Find the closest table row to the event target.
          const row = e.target.closest("tr");
          if (!row) return;
          handler({
            filename: row.dataset.filename,
            productId: row.dataset.productId,
          });
        });
        break;
      case "refresh":
        Utils.delegate(this.body, selector, "click", () => handler());
        break;
    }
  }
}

class OutputFilesModel {
  constructor(api) {
    this._runId = null;
    this._rawData = null;
    this._data = null;
    this._previousData = null;
    this.api = api;
    this.outputFilesUrl = "dragonsoutputfiles/";
    this.dragonsDataProductsUrl = "dragonsdataproducts/";
  }

  /**
   * Gets the run ID.
   * @return {number} The run ID.
   */
  get runId() {
    return this._runId;
  }

  /**
   * Sets the run ID.
   * @param {number} value - The run ID to set for future API requests.
   */
  set runId(value) {
    this._runId = value;
  }

  /**
   * Fetches files from the output directory for the set run ID.
   * @async
   * @throws {Error} Throws an error if the network request fails.
   */
  async fetchFiles() {
    try {
      const response = await this.api.get(`${this.outputFilesUrl}${this.runId}/`);
      this.data = response;
    } catch (error) {
      console.error("Error fetching list of output files:", error);
      throw error;
    }
  }

  /**
   * Adds a new file to the data product repository and fetches the updated file list.
   * @param {string} filename - The name of the file to add.
   * @param {string} filepath - The path of the file to add.
   */
  async addFile(filename, filepath) {
    try {
      const body = {
        filename: filename,
        filepath: filepath,
        data_product_type: "fits_file",
        dragons_run: this.runId,
      };
      await this.api.post(`${this.dragonsDataProductsUrl}`, body);
      // Fetch the files if the creating was successful.
    } catch (error) {
      console.error(`Error adding file:`, error);
      throw error;
    }
    await this.fetchFiles();
  }

  /**
   * Removes a file from the data product repository.
   * @param {string} filename - The name of the file to remove.
   * @param {string} productId - The product ID associated with the file.
   */
  async removeFile(filename, productId) {
    try {
      const body = {
        filename: filename,
        product_id: productId,
        action: "remove",
      };
      const response = await this.api.patch(
        `${this.outputFilesUrl}${this.runId}/`,
        body
      );
      this.data = response;
    } catch (error) {
      console.error(`Error removing file:`, error);
      throw error;
    }
  }

  /**
   * Returns the current data stored in the model.
   * @return {Array} The current array of files.
   */
  get data() {
    return this._data;
  }

  /**
   * Returns the raw data stored in the model.
   * @return {Object} The raw data object.
   */
  get rawData() {
    return this._rawData;
  }

  /**
   * Sets the current data for the model and updates the previous data state.
   * @param {Array} value - The new data to set.
   */
  set data(value) {
    this._rawData = value;
    this._previousData = this._data;
    this._data = value.files;
  }

  /**
   * Checks if the current data differs from the previous data.
   * @return {boolean} True if data has changed, false otherwise.
   */
  dataChanged() {
    return JSON.stringify(this._data) !== JSON.stringify(this._previousData);
  }

  /**
   * Clears all data stored in the model.
   */
  clearData() {
    this._rawData = null;
    this._data = null;
  }
}

/**
 * Constructs the controller for managing model and view interactions in the OutputFiles component.
 * @param {OutputFilesModel} model - The model managing the data state.
 * @param {OutputFilesView} view - The view displaying the data.
 */
class OutputFilesController {
  constructor(model, view) {
    this.model = model;
    this.view = view;

    this.view.bindCallback("refresh", () => this.refresh());
    this.view.bindCallback("add", (item) => this.add(item.filename, item.filepath));
    this.view.bindCallback("remove", (item) =>
      this.remove(item.filename, item.productId)
    );
  }

  /**
   * Updates the model run ID and view with data.
   * @async
   * @param {number} runId - The run ID to get output files for.
   */
  async update(runId) {
    this.model.runId = runId;
    await this.refresh();
  }

  /**
   * Initiates the file addition process and updates the view if data has changed.
   * @param {string} filename - The name of the file to add.
   * @param {string} filepath - The path of the file to add.
   */
  async add(filename, filepath) {
    await this.model.addFile(filename, filepath);
    if (this.model.dataChanged()) {
      this.view.render("update", { data: this.model.data });
    }
  }

  /**
   * Initiates the file removal process and updates the view if data has changed.
   * @param {string} filename - The name of the file to remove.
   * @param {string} productId - The product ID associated with the file.
   */
  async remove(filename, productId) {
    await this.model.removeFile(filename, productId);
    if (this.model.dataChanged()) {
      this.view.render("update", { data: this.model.data });
    }
  }

  /**
   * Fetches the files and refreshes the view. This does not set the model run ID.
   * @async
   */
  async refresh() {
    this.view.render("loading");
    await Utils.ensureMinimumDuration(this.model.fetchFiles(), 500);
    if (this.model.dataChanged()) {
      this.view.render("update", { data: this.model.data });
    }
    this.view.render("loaded");
  }
}

/**
 * Constructs the OutputFiles component and initializes its subcomponents.
 * @param {HTMLElement} parentElement - The DOM element to which the component will be attached.
 * @param {Object} api - The API interface used for data interactions.
 */
class OutputFiles {
  constructor(parentElement, api) {
    this.model = new OutputFilesModel(api);
    this.template = new OutputFilesTemplate();
    this.view = new OutputFilesView(this.template, parentElement);
    this.controller = new OutputFilesController(this.model, this.view);
  }

  /**
   * Sets the run ID and triggers an update of the output directory.
   */
  update(runId) {
    this.controller.update(runId);
  }

  /**
   * Refreshes the view of the files in the output directory.
   */
  refresh() {
    this.controller.refresh();
  }
}
