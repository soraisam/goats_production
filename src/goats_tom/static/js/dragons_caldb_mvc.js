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
    accordion.id = "calibrationAccordion";

    const header = Utils.createElement("h6", ["accordion-header"]);
    header.id = "headingCalibration";

    const button = Utils.createElement("button");
    button.className = "accordion-button collapsed";
    button.setAttribute("type", "button");
    button.setAttribute("data-bs-toggle", "collapse");
    button.setAttribute("data-bs-target", "#collapseCalibration");
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", "collapseCalibration");
    button.textContent = "Calibration Database";

    header.appendChild(button);

    const collapseDiv = Utils.createElement("div");
    collapseDiv.id = "collapseCalibration";
    collapseDiv.className = "accordion-collapse collapse";
    collapseDiv.setAttribute("aria-labelledby", "headingCalibration");
    collapseDiv.setAttribute("data-bs-parent", "#calibrationAccordion");

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
    const th = Utils.createElement("th");
    th.setAttribute("scope", "col");
    th.setAttribute("colspan", "2");

    // Create the add file button with an icon.
    const addButton = Utils.createElement("button", ["btn", "btn-primary", "btn-sm"]);
    addButton.setAttribute("type", "button");
    addButton.textContent = " Add File";
    addButton.dataset.action = "add";

    // Create and append the font awesome icon.
    const icon = Utils.createElement("i", ["fa-solid", "fa-plus"]);
    addButton.prepend(icon);

    const form = Utils.createElement("form");
    form.style.display = "none";
    form.id = "fileUploadForm";

    const fileInput = Utils.createElement("input");
    fileInput.type = "file";
    fileInput.name = "file";
    fileInput.id = "fileInput";

    form.appendChild(fileInput);
    th.appendChild(form);

    th.appendChild(addButton);
    tr.appendChild(th);
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
    // Loop through each item in the data array to create table rows.
    data.forEach((item) => {
      const tr = Utils.createElement("tr");

      // Create the filename cell with a data attribute.
      const tdFilename = Utils.createElement("td", ["py-0", "mb-0"]);
      tdFilename.textContent = item.filename;
      tdFilename.setAttribute("data-caldbFile", item.filename);

      // Create the delete button cell.
      const tdRemove = Utils.createElement("td", ["text-end", "py-0", "mb-0"]);

      const removeButton = Utils.createElement("a", ["link-danger"]);
      removeButton.setAttribute("type", "button");
      removeButton.setAttribute("data-filename", item.filename);
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
        Utils.delegate(this.table, selector, "click", (e) => handler());
        break;
      case "remove":
        Utils.delegate(this.table, selector, "click", (e) =>
          handler({ filename: e.target.dataset.filename })
        );
        break;
    }
  }
}

/**
 * Manages the data for the calibration database.
 */
class CaldbModel {
  constructor() {
    this.rawData = null;
    this.data = null;
  }

  /**
   * Sets the data for the model.
   * @param {Object} data - The complete data object.
   */
  setData(data) {
    this.rawData = data;
    this.data = data.results;
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

  /**
   * Sets fake data for testing purposes.
   */
  setFakeData() {
    const data = {
      count: 3,
      next: null,
      previous: null,
      results: [
        { filename: "test1.fits" },
        { filename: "test2.fits" },
        { filename: "test3.fits" },
      ],
    };
    this.rawData = data;
    this.data = data.results;
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

    this.view.bindCallback("update", () => this.update());
    this.view.bindCallback("remove", (item) => this.remove(item.filename));
    this.view.bindCallback("add", () => this.add());
  }

  /**
   * Fetches and updates data in the model and re-renders the view.
   */
  update() {
    // TODO: This should fetch the data.
    this.model.setFakeData();
    // this.model.setData(data);
    this.view.render("update", { data: this.model.getData() });
  }

  /**
   * Removes an item by its filename.
   * @param {string} filename - The filename of the item to remove.
   */
  remove(filename) {
    console.log("Called 'remove': ", filename);
  }

  /**
   * Adds a new item to the model.
   */
  add() {
    console.log("Called 'add'");
  }
}

/**
 * Constructs the calibration database application and initializes all components.
 * @param {HTMLElement} parentElement - The parent element where the application is mounted.
 */
class Caldb {
  constructor(parentElement) {
    this.model = new CaldbModel();
    this.template = new CaldbTemplate();
    this.view = new CaldbView(this.template, parentElement);
    this.controller = new CaldbController(this.model, this.view);
  }

  /**
   * Triggers an update in the controller.
   */
  update() {
    this.controller.update();
  }
}
