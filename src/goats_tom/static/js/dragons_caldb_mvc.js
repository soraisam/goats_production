CALDB_ID = "Caldb";

/**
 * Class to manage calibration database UI components.
 */
class CaldbTemplate {
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
    const accordionId = `accordion${CALDB_ID}`;
    accordion.id = accordionId;

    const header = Utils.createElement("h6", ["accordion-header"]);
    const headerId = `header${CALDB_ID}`;
    header.id = headerId;

    const button = Utils.createElement("button");
    const collapseId = `collapse${CALDB_ID}`;
    button.className = "accordion-button collapsed";
    button.setAttribute("type", "button");
    button.setAttribute("data-bs-toggle", "collapse");
    button.setAttribute("data-bs-target", `#${collapseId}`);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", collapseId);
    button.textContent = "Calibration Database";

    header.appendChild(button);

    const collapseDiv = Utils.createElement("div");
    collapseDiv.id = collapseId;
    collapseDiv.className = "accordion-collapse collapse";
    collapseDiv.setAttribute("aria-labelledby", headerId);
    collapseDiv.setAttribute("data-bs-parent", `#${accordionId}`);

    const accordionBody = Utils.createElement("div", ["accordion-body"]);
    accordionBody.appendChild(this.createTable());

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
    ]);
    table.append(this.createTHeadDefault(), this.createTBodyDefault());

    return table;
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
   * Creates a default thead element.
   * @return {HTMLElement} The newly created thead element.
   */
  createTHeadDefault() {
    const thead = Utils.createElement("thead");

    return thead;
  }

  /**
   * Creates a thead element with controls for adding files.
   * @return {HTMLElement} The thead element containing file upload controls.
   */
  createTHeadData() {
    const thead = Utils.createElement("thead");
    const tr = Utils.createElement("tr");

    // Creating a single header cell that spans two columns.
    const thForm = Utils.createElement("th");
    thForm.setAttribute("scope", "col");

    // Create form to handle file input.
    const form = Utils.createElement("form");
    form.id = `form${CALDB_ID}`;

    const fileLabel = Utils.createElement("label", ["btn", "btn-secondary", "btn-sm"]);
    fileLabel.textContent = " Add File";
    fileLabel.setAttribute("for", "fileInputCaldb");

    // Create and prepend the icon.
    const fileIcon = Utils.createElement("i", ["fa-solid", "fa-plus"]);
    fileLabel.prepend(fileIcon);

    // Hide file input to use custom text for button.
    const fileInput = Utils.createElement("input");
    fileInput.type = "file";
    fileInput.name = "file";
    fileInput.style.display = "none";
    fileInput.dataset.action = "add";
    fileInput.id = `fileInput${CALDB_ID}`;

    form.append(fileLabel, fileInput);
    thForm.appendChild(form);

    // Create another cell for the refresh button.
    const thRefresh = Utils.createElement("th", ["text-end"]);
    thRefresh.setAttribute("scope", "col");

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

    thRefresh.appendChild(refreshButton);

    tr.append(thForm, thRefresh);
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
      td.setAttribute("colspan", "2");
      td.textContent = "No calibration files found...";
      tr.appendChild(td);
      tbody.appendChild(tr);
      return tbody;
    }

    // Loop through each item in the data array to create table rows.
    data.forEach((item) => {
      const tr = Utils.createElement("tr");

      // Create the filename cell with a data attribute.
      const tdFilename = Utils.createElement("td", ["py-0", "mb-0"]);
      // TODO: Change back when formatter is figured out.
      // tdFilename.textContent = `${item.path}/${item.name}`;
      tdFilename.textContent = item.name;

      // Create the delete button cell.
      const tdRemove = Utils.createElement("td", ["text-end", "py-0", "mb-0"]);

      const removeButton = Utils.createElement("a", ["link-danger"]);
      removeButton.setAttribute("type", "button");
      removeButton.setAttribute("data-file", item.name);
      removeButton.setAttribute("data-action", "remove");
      // Create icon element for button.
      const icon = Utils.createElement("i", ["fa-solid", "fa-circle-minus"]);
      removeButton.appendChild(icon);

      tdRemove.appendChild(removeButton);

      // Append the cells to the row.
      tr.append(tdFilename, tdRemove);

      // Append the row to the tbody.
      tbody.appendChild(tr);
    });

    return tbody;
  }
}

/**
 * Constructs the view with a specified template and parent element.
 * @param {Object} template - The template object used for rendering components.
 * @param {HTMLElement} parentElement - The container where the view will be mounted.
 */
class CaldbView {
  constructor(template, parentElement) {
    this.template = template;
    this.parentElement = parentElement;

    this.card = this._create();
    this.table = this.card.querySelector("table");
    this.tbody = this.card.querySelector("tbody");
    this.thead = this.card.querySelector("thead");

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
    const newThead = this.template.createTHeadData();
    const newTbody = this.template.createTBodyData(data);
    this.table.replaceChild(newThead, this.thead);
    this.table.replaceChild(newTbody, this.tbody);
    this.thead = newThead;
    this.tbody = newTbody;
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
        Utils.delegate(this.table, selector, "change", (e) =>
          handler({ file: e.target.files[0] })
        );
        break;
      case "remove":
        Utils.delegate(this.table, selector, "click", (e) =>
          handler({ filename: e.target.dataset.file })
        );
        break;
      case "refresh":
        Utils.delegate(this.table, selector, "click", () => handler());
    }
  }
}

/**
 * Manages the data for the calibration database.
 * @param {FetchWrapper} api - Instance of the API wrapper to use.
 */
class CaldbModel {
  constructor(api) {
    this.runId = null;
    this.rawData = null;
    this.data = null;
    this.api = api;
    this.caldbUrl = "dragonscaldb/";
  }

  /**
   * Sets the run ID for the calibration database operations.
   * @param {number} runId - The run ID to set for future API requests.
   */
  setRunId(runId) {
    this.runId = runId;
  }

  /**
   * Fetches files from the calibration database for the set run ID.
   * @async
   * @throws {Error} Throws an error if the network request fails.
   */
  async fetchFiles() {
    try {
      const response = await this.api.get(`${this.caldbUrl}${this.runId}/`);
      this.setData(response);
    } catch (error) {
      console.error("Error fetching list of calibration database files:", error);
      throw error;
    }
  }

  /**
   * Removes a file from the calibration database.
   * @async
   * @param {string} filename - The name of the file to be removed.
   * @throws {Error} Throws an error if the removal operation fails.
   */
  async removeFile(filename) {
    try {
      const body = {
        file: filename,
        action: "remove",
      };
      const response = await this.api.patch(`${this.caldbUrl}${this.runId}/`, body);
      this.setData(response);
    } catch (error) {
      console.error(`Error removing file:`, error);
      throw error;
    }
  }

  // TODO:
  async addFile(file) {
    // await this._addOrRemoveFile(file, "add");
    console.log(`Called 'model.addFile' ${file.name}`);

    return;
    try {
      const body = {
        file: file,
        action: "add",
      };
      const response = await this.api.patch(`${this.caldbUrl}${this.runId}/`, body);
      this.setData(response);
    } catch (error) {
      console.error(`Error adding file:`, error);
      throw error;
    }
  }

  /**
   * Sets the data for the model.
   * @param {Object} data - The complete data object.
   */
  setData(data) {
    this.rawData = data;
    this.data = data.files;
  }

  /**
   * Returns the raw data stored in the model.
   * @return {Object} The raw data.
   */
  getRawData() {
    return this.rawData;
  }

  /**
   * Returns the processed data stored in the model.
   * @return {Array} The processed results data.
   */
  getData() {
    return this.data;
  }

  /**
   * Clears all data stored in the model.
   */
  clearData() {
    this.rawData = null;
    this.data = null;
  }
}

/**
 * Initializes a new controller instance.
 * @param {CaldbModel} model - The data model for the application.
 * @param {CaldbView} view - The UI view for the application.
 */
class CaldbController {
  constructor(model, view) {
    this.model = model;
    this.view = view;

    this.view.bindCallback("refresh", () => this.refresh());
    this.view.bindCallback("remove", (item) => this.remove(item.filename));
    this.view.bindCallback("add", (item) => this.add(item.file));
  }

  /**
   * Updates the model run ID and view with data.
   * @async
   * @param {number} runId - The run ID for the calibration database.
   */
  async update(runId) {
    this.model.setRunId(runId);
    await this.refresh();
  }

  /**
   * Removes an item by its filename.
   * @async
   * @param {string} filename - The filename of the item to remove.
   */
  async remove(filename) {
    console.log("Called 'remove': ", filename);
    await this.model.removeFile(filename);
    this.view.render("update", { data: this.model.getData() });
  }

  /**
   * Adds a new item to the model.
   * @async
   * @param {File} file - A file object to add to the database.
   */
  async add(file) {
    console.log(`Called 'controller.add' ${file.name}`);
    await this.model.addFile(file);
    this.view.render("update", { data: this.model.getData() });
  }

  /**
   * Fetches the files and refreshes the view. This does not set the model run ID.
   * @async
   */
  async refresh() {
    await this.model.fetchFiles();
    this.view.render("update", { data: this.model.getData() });
  }
}

/**
 * Constructs the calibration database application and initializes all components.
 * @param {HTMLElement} parentElement - The parent element where the application is mounted.
 * @param {FetchWrapper} api - An API instance to use for fetching.
 */
class Caldb {
  constructor(parentElement, api) {
    this.model = new CaldbModel(api);
    this.template = new CaldbTemplate();
    this.view = new CaldbView(this.template, parentElement);
    this.controller = new CaldbController(this.model, this.view);
  }

  /**
   * Sets the run ID and triggers an update of the calibration database.
   */
  update(runId) {
    this.controller.update(runId);
  }

  /**
   * Refreshes the view of the files in the calibration database.
   */
  refresh() {
    this.controller.refresh();
  }
}
