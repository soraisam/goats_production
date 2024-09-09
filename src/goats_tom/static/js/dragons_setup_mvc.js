/**
 * Manages setup data and interactions with the API for run configuration.
 */
class SetupModel {
  constructor(api) {
    this.api = api;
    this.runs = [];
    this.files = [];
    this.recipesUrl = "dragonsrecipes/";
    this.runsUrl = "dragonsruns/";
    this.filesUrl = "dragonsfiles/";
    this.recipes = [];
  }

  /**
   * Fetches recipes associated with a specific DRAGONS run.
   * @param {string} runId The identifier for the DRAGONS run to fetch recipes for.
   * @returns {Promise<Object[]>} A promise that resolves to an array of recipe objects.
   */
  async fetchRecipes(runId) {
    try {
      const response = await this.api.get(
        `${this.recipesUrl}?dragons_run=${runId}&group_by_file_type=true`
      );
      this.recipes = response.results || [];
      return this.recipes;
    } catch (error) {
      console.error("Error fetching recipes:", error);
    }
  }

  /**
   * Submits setup data to initialize a new DRAGONS run and updates runs.
   * @param {FormData} formData Setup data from the form.
   */
  async formSubmit(observationRecordId, formData) {
    const formDataObject = Object.fromEntries(formData);

    try {
      const response = await this.api.post(
        `${this.runsUrl}?observation_record=${observationRecordId}`,
        formDataObject
      );
    } catch (error) {
      console.error("Error initializing DRAGONS run:", error);
      throw error;
    }
  }

  /**
   * Fetches a list of files associated with a specific run. The files are grouped by file type.
   * @param {string} runId The ID of the run for which files are to be fetched.
   * @returns {Promise<Array>} A promise that resolves to an array of files grouped by file type.
   * @throws {Error} Throws an error if the fetch operation fails.
   */
  async fetchFileList(runId) {
    try {
      const response = await this.api.get(
        `${this.filesUrl}?group_by_file_type=true&dragons_run=${runId}`
      );
      this.files = response.results || [];
      return this.files;
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  }

  /**
   * Fetches header information for a specific file.
   * @param {string} fileId The ID of the file for which header data is needed.
   * @returns {Promise<Object>} A promise that resolves to the header data.
   */
  async fetchHeader(fileId) {
    try {
      const response = await this.api.get(`${this.filesUrl}${fileId}/?include=header`);
      return response;
    } catch (error) {
      console.error("Error fetching header:", error);
    }
  }

  /**
   * Fetches, groups, and optionally filters files based on their descriptors.
   * @param {string} runId The ID of the run for which files are to be fetched.
   * @param {string | string[]} groupBy The descriptor(s) to group the files by.
   * @param {string} fileType The type of files to filter before grouping.
   * @param {string} [objectName] Optional object name to include in the query.
   * @param {string} [filterExpression] Optional filter expression to apply before grouping.
   * @param {boolean} [filterStrict] Optional filter strictly.
   * @returns {Promise<Object>} A promise that resolves to an object containing grouped files.
   */
  async fetchGroupAndFilterFiles(
    runId,
    groupBy,
    fileType,
    objectName = "",
    filterExpression = "",
    filterStrict = false
  ) {
    let groupByParams = "";

    if (Array.isArray(groupBy)) {
      // Build URL with multiple group_by parameters.
      groupByParams = groupBy.map((gb) => `&group_by=${gb}`).join("");
    } else {
      // Single group_by parameter.
      groupByParams = `&group_by=${groupBy}`;
    }

    // Base URL setup with mandatory parameters.
    const baseUrl = `${this.filesUrl}?dragons_run=${runId}${groupByParams}&file_type=${fileType}&filter_strict=${filterStrict}`;

    // Append object name if it's provided.
    const objectNameParam = objectName
      ? `&object_name=${encodeURIComponent(objectName)}`
      : "";

    // Append filter expression if it's provided.
    const filterExpressionParam = filterExpression
      ? `&filter_expression=${encodeURIComponent(filterExpression)}`
      : "";

    // Complete URL construction.
    const url = baseUrl + filterExpressionParam + objectNameParam;
    try {
      const response = await this.api.get(url);
      return response || {};
    } catch (error) {
      console.error("Error fetching, grouping, and filtering files:", error);
    }
  }

  /**
   * Fetches a list of runs associated with a specific observation record.
   * @param {string} observationRecordId The ID of the observation record.
   * @returns {Promise<Array>} A promise that resolves to an array of runs.
   * @throws {Error} Throws an error if the fetch operation fails.
   */
  async fetchRuns(observationRecordId) {
    try {
      const response = await this.api.get(
        `${this.runsUrl}?observation_record=${observationRecordId}`
      );
      this.runs = response.results || [];
      return this.runs;
    } catch (error) {
      console.error("Error fetching runs:", error);
    }
  }

  /**
   * Fetches a run.
   * @param {Number} runId The ID of the run.
   * @returns {Promise<Array>} A promise that resolves to the run information.
   * @throws {Error} Throws an error if the fetch operation fails.
   */
  async fetchRun(runId) {
    try {
      const response = await this.api.get(`${this.runsUrl}${runId}?include=groups`);
      return response;
    } catch (error) {
      console.error("Error fetching run:", error);
    }
  }
}

/**
 * Manages the UI for a run setup, handling form submission and dynamic updates.
 */
class SetupView {
  constructor() {
    // Initialize UI elements.
    this.card = document.getElementById("setupCard");
    this.form = this.card.querySelector("#setupForm");
    this.runSelect = this.card.querySelector("#runSelect");
    this.startNewRun = this.card.querySelector("#startNewRun");
    this.useExistingRun = this.card.querySelector("#useExistingRun");
    this.filesAndRecipesContainer = this.card.querySelector(
      "#filesAndRecipesContainer"
    );
    this.observationRecordId = this.card.dataset.observationRecordPk;
    this.deleteRun = this.card.querySelector("#deleteRun");
    this.headerModal = Utils.createModal("header");
    this.runContainer = this.card.querySelector("#runContainer");
    this.runContainer.appendChild(this.createRunTable());
    this.runId = null;

    // Set up event listeners for UI interactions.
    this._initLocalListeners();
  }

  /**
   * Updates the title and content of the header modal based on the provided data.
   * @param {Object} data Data object containing information to display in the modal.
   */
  updateHeaderModal(data) {
    this.headerModal.updateTitle(`Viewing header for ${data.product_id}`);

    // Format and apply to body.
    const content = this.formatHeaderData(data);
    this.headerModal.updateBody(content);
  }

  /**
   * Displays the header modal.
   */
  showHeaderModal() {
    this.headerModal.show();
  }

  /**
   * Hides the header modal.
   */
  hideHeaderModal() {
    this.headerModal.hide();
  }

  /**
   * Clears the content of the run table.
   */
  clearRunTable() {
    this.runTable.innerHTML = "";
  }

  /**
   * Resets the run table by clearing it and adding a default row indicating no run is selected.
   */
  resetRunTable() {
    this.clearRunTable();
    // Create a single row that says "No run selected...".
    const tr = Utils.createElement("tr");

    const td = Utils.createElement("td");
    td.textContent = "No run selected...";
    // Spans across both columns.
    td.setAttribute("colspan", "2");
    tr.appendChild(td);

    this.runTable.appendChild(tr);
  }

  /**
   * Displays the run details in the run table.
   * @param {Object} run The run object containing data to display in the table.
   */
  displayRun(run) {
    // Clear the existing table rows.
    this.clearRunTable();

    // Define the keys you want to display.
    const keysToDisplay = [
      "created",
      "version",
      "directory",
      "config_filename",
      "cal_manager_filename",
      "log_filename",
    ];

    // Loop through the filtered keys in the run object to create table rows.
    keysToDisplay.forEach((key) => {
      if (run.hasOwnProperty(key)) {
        // Ensure the key exists in the run object.
        const formattedKey = Utils.formatDisplayText(key);

        const tr = Utils.createElement("tr");

        const th = Utils.createElement("td");
        th.textContent = formattedKey;
        tr.appendChild(th);

        const td = Utils.createElement("td");
        td.textContent = run[key];
        tr.appendChild(td);

        this.runTable.appendChild(tr);
      }
    });
    this.runId = run.id;
  }

  /**
   * Creates the run table with initial setup.
   * The table is initially populated with a single row indicating no run is selected.
   * @returns {Element} The created table element.
   */
  createRunTable() {
    // Create a table.
    const table = Utils.createElement("table", [
      "table",
      "table-borderless",
      "table-sm",
      "small",
    ]);
    const tbody = Utils.createElement("tbody");
    this.runTable = tbody;
    table.appendChild(tbody);

    this.resetRunTable();

    return table;
  }

  /**
   * Formats header data into a Bootstrap table with rows of key-value pairs.
   * @param {Object} data The data object containing key-value pairs to display.
   * @returns {HTMLElement} A Bootstrap-styled table element with key-value pairs.
   */
  formatHeaderData(data) {
    // Create the table element.
    const table = Utils.createElement("table", ["table", "table-sm"]);

    // Create and append the table body.
    const tbody = Utils.createElement("tbody");
    for (const [key, value] of Object.entries(data.header)) {
      const row = Utils.createElement("tr");
      const cellKey = Utils.createElement("td");
      cellKey.textContent = key;
      const cellValue = Utils.createElement("td");
      cellValue.textContent = value;
      row.appendChild(cellKey);
      row.appendChild(cellValue);
      tbody.appendChild(row);
    }
    table.append(tbody);

    return table;
  }

  /**
   * Populates the run selection dropdown with options based on available runs.
   * @param {Array} runs DRAGONS run objects to display in the select dropdown.
   */
  displayRuns(runs) {
    // Reset the dropdown for new data.
    this.runSelect.innerHTML = '<option value="" selected hidden>Select A Run</option>';
    runs.forEach((run) => {
      const option = new Option(run.run_id, run.id);
      this.runSelect.add(option);
    });
  }

  /**
   * Display files and recipes in the specified container.
   * @param {Object} files The files to display, grouped by file type.
   * @param {Object} recipes The recipes associated with each file type.
   * @param groups
   */
  displayFilesAndRecipes(files, recipes, groups) {
    this.filesAndRecipesContainer.innerHTML = "";

    const filesAndRecipesContainerP = Utils.createElement("p", "mb-2");

    if (Object.keys(files).length === 0) {
      filesAndRecipesContainerP.textContent = "No Files Found";
      this.filesAndRecipesContainer.appendChild(filesAndRecipesContainerP);
    } else {
      filesAndRecipesContainerP.textContent = "Observation Type";
      this.filesAndRecipesContainer.appendChild(filesAndRecipesContainerP);

      // Sort the file types alphabetically before creating accordion items.
      const sortedEntries = Object.entries(files).sort((a, b) =>
        a[0].localeCompare(b[0])
      );

      sortedEntries.forEach(([fileType, fileGroup], index) => {
        // TODO: Fix this object check need to determine if we always want lower
        if (fileType === "object") {
          // Special handling for 'object' category.
          Object.entries(fileGroup).forEach(([objectName, fileList], objectIndex) => {
            const recipe = recipes[fileType][objectName]; // Assuming a generic recipe for simplicity.
            const accordionItem = this.createAccordionItem(
              `${fileType} | ${objectName}`,
              fileList,
              recipe,
              `${index}-${objectIndex}`,
              groups
            );
            this.filesAndRecipesContainer.appendChild(accordionItem);
          });
        } else {
          // Regular handling for other file types.
          const recipe = recipes[fileType];
          const accordionItem = this.createAccordionItem(
            fileType,
            fileGroup,
            recipe,
            index,
            groups
          );
          this.filesAndRecipesContainer.appendChild(accordionItem);
        }
      });
    }
  }

  /**
   * Binds the action to fetch files when the fetch button is clicked.
   * @param {Function} handler The function to call when fetching files.
   */
  bindFetchFiles(handler) {
    this.onChangeRun = handler;
  }

  /**
   * Resets the form to its default state and hides it if necessary.
   */
  resetForm() {
    this.form.reset();
    this.toggleFormVisibility(false);
    this.useExistingRun.checked = true;
    this.setRunControlsDisabledState(false);
  }

  /**
   * Sets the disabled state for run-related control elements.
   * @param {boolean} disable If true, disables the control elements; if false, enables them.
   */
  setRunControlsDisabledState(disable) {
    this.runSelect.disabled = disable;
    // TODO: Keep this disabled until implemented.
    //this.deleteRun.disabled = disable;
  }

  /**
   * Create an accordion item for a specific file type and its associated files and recipes.
   * @param {string} fileType The type of the files.
   * @param {Array} files The files associated with this file type.
   * @param {Array} recipes The recipes associated with the files.
   * @param {number} index The index used to generate unique IDs for DOM elements.
   * @returns {HTMLElement} The constructed accordion item.
   */
  createAccordionItem(fileType, files, recipes, index, groups) {
    const hr = Utils.createElement("hr");
    // Create the outer container for the accordion item with the 'accordion-item' class.
    const accordionItem = Utils.createElement("div", "accordion-item");

    // Generate unique IDs for the header and collapse elements based on the index.
    const headerId = `heading-${index}`;
    const collapseId = `collapse-${index}`;

    // Create the header for the accordion item with a button that toggles the collapse.
    const header = Utils.createElement("h2", "accordion-header");
    header.id = headerId;
    const button = Utils.createElement("button", [
      "accordion-button",
      "text-capitalize",
      "collapsed",
    ]);
    button.setAttribute("type", "button");
    button.setAttribute("data-toggle", "collapse");
    button.setAttribute("data-target", `#${collapseId}`);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", collapseId);
    button.textContent = fileType;
    header.appendChild(button);

    // Create the collapsible body section that will contain the file details.
    const collapse = Utils.createElement("div", ["accordion-collapse", "collapse"]);
    collapse.id = collapseId;
    collapse.setAttribute("aria-labelledby", headerId);
    collapse.setAttribute("data-parent", "#filesAndRecipesContainer");

    // Create the body content area for the collapsible section.
    const body = Utils.createElement("div", ["accordion-body", "files-overflow"]);

    // Create a container for recipes.
    const navP = Utils.createElement("p", "mb-2");
    navP.textContent = "Available Recipes";
    const navContainer = Utils.createElement("ul", ["nav", "nav-pills", "flex-column"]);
    navContainer.setAttribute("id", `js-pills-${fileType}`);

    navContainer.setAttribute("role", "tablist");
    navContainer.setAttribute("aria-orientation", "vertical");

    recipes.forEach((recipe, index) => {
      const pillId = `recipePill-${recipe.id}`;
      const paneId = `recipePane-${recipe.id}`;

      const navItem = Utils.createElement("li", ["nav-item"]);
      navItem.setAttribute("role", "presentation");

      const navLink = Utils.createElement("button", [
        "nav-link",
        "w-100",
        "text-start",
        "d-flex",
        "align-items-center",
      ]);
      if (recipe.file_type !== "other") {
        navLink.setAttribute("id", pillId);
        navLink.setAttribute("data-bs-toggle", "pill");
        navLink.setAttribute("data-bs-target", `#${paneId}`);
        navLink.setAttribute("type", "button");
        navLink.setAttribute("role", "tab");
        navLink.setAttribute("aria-controls", paneId);
        navLink.setAttribute("aria-selected", "false");
        navLink.dataset.action = "switchTab";
        navLink.dataset.recipeId = recipe.id;

        navLink.textContent = `${recipe.short_name}${
          recipe.is_default ? " (default)" : ""
        }`;
      } else {
        navLink.classList.add("disabled");
        navLink.textContent = recipe.short_name;
      }

      navItem.appendChild(navLink);
      navContainer.appendChild(navItem);
    });
    body.append(navP, navContainer);

    // Create files table.
    const tableP = Utils.createElement("p", ["mt-3", "mb-2"]);
    tableP.textContent = "Available Files";

    // Build the file filter.
    const form = this.createFileGroupingsAndFilterForm(files[0], groups);
    const availableFileGroupsRow = this.createAvailableFileGroups(
      fileType,
      files.length
    );

    const table = Utils.createElement("table", [
      "table",
      "table-sm",
      "table-borderless",
    ]);
    const tbody = Utils.createElement("tbody");
    tbody.id = `tbody-${fileType}`;
    // Create the header.
    const thead = Utils.createElement("thead");
    thead.id = `thead-${fileType}`;
    const headerRow = Utils.createElement("tr");

    // Create a checkbox in the header for selecting/deselecting all rows.
    const selectAllTh = Utils.createElement("th");
    const selectAllCheckbox = Utils.createElement("input", ["form-check-input"]);
    selectAllCheckbox.type = "checkbox";
    selectAllCheckbox.dataset.action = "selectAll";
    selectAllCheckbox.dataset.fileType = `${fileType}`;
    selectAllCheckbox.checked = true;
    selectAllCheckbox.id = `selectAll-${fileType}`;
    selectAllCheckbox.addEventListener("change", (event) => {
      const isChecked = event.target.checked;
      const checkboxes = this.runTable.querySelectorAll("input[type='checkbox']");
      checkboxes.forEach((checkbox) => (checkbox.checked = isChecked));
    });

    const div = Utils.createElement("div", ["form-check", "mb-0", "h-100"]);
    const selectAllLabel = Utils.createElement("label", [
      "form-check-label",
      "fw-normal",
    ]);
    selectAllLabel.htmlFor = `selectAll-${fileType}`;
    selectAllLabel.textContent = "Select/Deselect All";
    div.append(selectAllCheckbox, selectAllLabel);
    selectAllTh.appendChild(div);
    headerRow.appendChild(selectAllTh);

    thead.appendChild(headerRow);
    // Loop through each file and create a detailed view for it.
    files.forEach((file) => {
      const fileRow = this.createFileEntry(file);
      tbody.appendChild(fileRow);
    });
    table.append(thead, tbody);
    body.append(tableP, form, hr, availableFileGroupsRow, table);
    collapse.appendChild(body);

    // Construct the complete accordion item by adding both header and collapse sections.
    accordionItem.appendChild(header);
    accordionItem.appendChild(collapse);

    // Return the fully constructed accordion item.
    return accordionItem;
  }

  /**
   * Creates a filter input row for file filtering based on user-defined criteria.
   * @param {Object} file The file object for which the filter is being created.
   * @returns {HTMLElement} A DOM element representing the row for file filtering input.
   */
  createFileFilter(file) {
    const row = Utils.createElement("div", ["row", "ms-1", "mb-1"]);
    const col1 = Utils.createElement("div", ["col-sm-3"]);
    const col2 = Utils.createElement("div", ["col-sm-9"]);

    // Build the ID.
    const id = `filterExpression-${file.id}`;

    // Build the label.
    const label = Utils.createElement("label", ["col-form-label"]);
    label.setAttribute("for", id);
    label.textContent = "Filter";

    // Build the input.
    const input = Utils.createElement("input", ["form-control"]);
    input.id = id;
    input.setAttribute("type", "text");
    input.setAttribute("placeholder", "exposure_time > 10 and airmass == 1");
    input.name = "filter_expression";

    // Create information popover button with an icon for filter expressions.
    const infoButton = Utils.createElement("a", ["link-primary", "ms-1"]);
    infoButton.setAttribute("type", "button");
    infoButton.setAttribute("tabindex", "0");
    infoButton.setAttribute("data-bs-trigger", "focus");
    infoButton.setAttribute("data-bs-toggle", "popover");
    infoButton.setAttribute("data-bs-placement", "top");
    infoButton.setAttribute("data-bs-html", "true");
    infoButton.setAttribute("data-bs-title", "Filtering Files");
    infoButton.setAttribute(
      "data-bs-content",
      `
    <p>Filtering helps with the bookkeeping and creating lists of input files to feed to the reduction. Whatever files are displayed after filtering and checked will be used in the reduction process.</p>
    <p>Supported Logical Operators:</p>
    <ul>
      <li><code>AND</code>/<code>and</code></li>
      <li><code>OR</code>/<code>or</code></li>
      <li><code>NOT</code>/<code>not</code></li>
    </ul>
    <p>Supported Time/Date Formats:</p>
    <ul>
      <li><code>ut_time</code>:
        <ul>
          <li><code>"%H:%M:%S.%f"</code></li>
          <li><code>"%H:%M:%S"</code></li>
        </ul>
      </li>
      <li><code>local_time</code>:
        <ul>
          <li><code>"%H:%M:%S.%f"</code></li>
          <li><code>"%H:%M:%S"</code></li>
        </ul>
      </li>
      <li><code>ut_date</code>: <code>"%Y-%m-%d"</code></li>
      <li><code>ut_datetime</code>:
        <ul>
          <li><code>"%Y-%m-%d %H:%M:%S"</code></li>
          <li><code>"%Y-%m-%dT%H:%M:%S"</code></li>
          <li><code>"%Y-%m-%d %H:%M:%S.%f"</code></li>
          <li><code>"%Y-%m-%dT%H:%M:%S.%f"</code></li>
        </ul>
      </li>
    </ul>
  `
    );

    // Create icon element.
    const icon = Utils.createElement("i", ["fa-solid", "fa-circle-info"]);
    infoButton.appendChild(icon);

    new bootstrap.Popover(infoButton);

    // Put together.
    col1.append(label, infoButton);
    col2.append(input);
    row.append(col1, col2);

    return row;
  }

  /**
   * Generates a row with a multiple selection dropdown for grouping files by specified descriptors.
   * @param {Object} file The file object for which the groupings are being created.
   * @param {Array<string>} groups An array of strings representing the grouping options.
   * @returns {HTMLElement} A DOM element representing the row for file groupings.
   */
  createFileGroupings(file, groups) {
    const row = Utils.createElement("div", ["row", "mb-3", "ms-1"]);
    const col1 = Utils.createElement("div", ["col-sm-3"]);
    const col2 = Utils.createElement("div", ["col-sm-9"]);

    // Build the ID.
    const id = `fileGroupings-${file.id}`;
    // tom-select has a different ID.
    const tsId = `${id}-ts-control`;

    // Build the label.
    const label = Utils.createElement("label", ["col-form-label"]);
    label.setAttribute("for", tsId);
    label.textContent = "Create Groupings";

    // Build the select.
    const select = Utils.createElement("select", []);
    select.id = id;
    select.name = "group_by";
    select.setAttribute("autocomplete", "off");
    select.multiple = true;

    // Create a document fragment to append options.
    const fragment = document.createDocumentFragment();
    groups.forEach((group) => {
      const option = Utils.createElement("option");
      option.value = group;
      option.textContent = group;
      fragment.appendChild(option);
    });
    select.appendChild(fragment);

    // Put together.
    col1.append(label);
    col2.append(select);
    row.append(col1, col2);

    new TomSelect(select, {
      create: false,
      sortField: { field: "text", director: "asc" },
      maxOptions: null,
      onItemAdd: function (value, item) {
        // This handles clearing text and refreshing the options.
        this.setTextboxValue("");
        this.refreshOptions(true);
      },
    });

    return row;
  }

  /**
   * Creates a dropdown for selecting available file groups after files have been grouped.
   * @param {string} fileType The file type of the file, could be combination of file type and
   * object name.
   * @param {number} fileCount The number of available files.
   * @returns {HTMLElement} A DOM element representing the row for selecting available file groups.
   */
  createAvailableFileGroups(fileType, fileCount) {
    const row = Utils.createElement("div", ["row", "mb-3", "ms-1"]);
    const col1 = Utils.createElement("div", ["col-sm-3"]);
    const col2 = Utils.createElement("div", ["col-sm-9"]);

    // Build the ID.
    const id = `availableFileGroups-${fileType}`;

    // Build the label.
    const label = Utils.createElement("label", ["col-form-label"]);
    label.setAttribute("for", id);
    label.textContent = "Available Groups";

    // Build the select.
    const select = Utils.createElement("select", ["form-select"]);
    select.id = id;
    select.setAttribute("autocomplete", "off");
    const option = Utils.createElement("option");
    option.textContent = `All ${Utils.getFileCountLabel(fileCount)}`;
    option.value = "All";
    option.selected = true;
    select.appendChild(option);

    // Put together.
    col1.appendChild(label);
    col2.appendChild(select);
    row.append(col1, col2);

    return row;
  }

  /**
   * Constructs a checkbox for the user to specify if strict filtering should be applied.
   * @param {Object} file The file object for which the strict filter option is being created.
   * @returns {HTMLElement} A DOM element representing the row containing the strict filter
   * checkbox.
   */
  createStrictFileFilter(file) {
    const row = Utils.createElement("div", ["row", "mb-1", "ms-1"]);
    const col = Utils.createElement("div", ["col-sm-9", "ms-auto"]);
    const div = Utils.createElement("div", ["form-check"]);

    // Build the ID.
    const id = `strictFileFilter-${file.id}`;

    // Build the checkbox.
    const checkbox = Utils.createElement("input", ["form-check-input"]);
    checkbox.id = id;
    checkbox.setAttribute("type", "checkbox");
    checkbox.name = "filter_strict";
    checkbox.checked = false;

    // Build the label.
    const label = Utils.createElement("label", ["form-check-label"]);
    label.setAttribute("for", id);
    label.textContent = "Use strict filter expression matching";

    // Create information popover button with an icon.
    const infoButton = Utils.createElement("a", ["link-primary", "ms-1"]);
    infoButton.setAttribute("type", "button");
    infoButton.setAttribute("tabindex", "0");
    infoButton.setAttribute("data-bs-toggle", "popover");
    infoButton.setAttribute("data-bs-placement", "top");
    infoButton.setAttribute("data-bs-trigger", "focus");
    infoButton.setAttribute("data-bs-html", "true");
    infoButton.setAttribute("data-bs-title", "Understanding Strict Matching");
    infoButton.setAttribute(
      "data-bs-content",
      `
      <p>By default, matching is lenient to improve usability:</p>
      <ul>
        <li><code>exposure_time</code> and <code>central_wavelength</code> use 'close enough' matching.</li>
        <li><code>filter_name</code>, <code>disperser</code>, and <code>detector_name</code> use 'pretty name' matching.</li>
      </ul>
      <p>For example:</p>
      <ul>
        <li>Header exposure time of 10.001 seconds matches <code>exposure_time==10</code>.</li>
        <li>Filter 'H_G0203' matches <code>filter_name=='H'</code>.</li>
      </ul>
      <p>Activate the strict flag for exact matches when needed.</p>
    `
    );

    // Create icon element.
    const icon = Utils.createElement("i", ["fa-solid", "fa-circle-info"]);
    infoButton.appendChild(icon);

    new bootstrap.Popover(infoButton);

    // Put together.
    div.append(checkbox, label, infoButton);
    col.appendChild(div);
    row.appendChild(col);

    return row;
  }

  /**
   * Assembles a form containing elements for file groupings and filters, along with action buttons.
   * This form allows users to specify groupings, filters, and to submit these settings for processing.
   * @param {Object} file The file object for which the form is being created.
   * @param {Array<string>} groups An array of strings representing the grouping options.
   * @returns {HTMLElement} The complete form element ready for user interaction.
   */
  createFileGroupingsAndFilterForm(file, groups) {
    const form = Utils.createElement("form");
    // Create hidden inputs for file_type and object_name
    const fileTypeInput = Utils.createElement("input");
    fileTypeInput.setAttribute("type", "hidden");
    fileTypeInput.setAttribute("name", "file_type");
    fileTypeInput.value = file.file_type;

    const objectNameInput = Utils.createElement("input");
    objectNameInput.setAttribute("type", "hidden");
    objectNameInput.setAttribute("name", "object_name");
    objectNameInput.value = file.object_name;

    // Build the elements for the form.
    const fileFilterRow = this.createFileFilter(file);
    const fileGroupingsRow = this.createFileGroupings(file, groups);
    const strictFileFilterRow = this.createStrictFileFilter(file);
    // TODO: Build the button.
    const div = Utils.createElement("div", ["d-flex", "justify-content-end"]);
    const button = Utils.createElement("button", ["btn", "btn-primary"]);
    button.textContent = "Apply Groupings And Filter";
    button.dataset.action = "submitFileGroupingsAndFilterForm";
    button.setAttribute("type", "submit");
    div.appendChild(button);

    form.append(
      fileGroupingsRow,
      fileFilterRow,
      strictFileFilterRow,
      fileTypeInput,
      objectNameInput,
      div
    );

    return form;
  }

  /**
   * Creates a single file entry within the accordion as a table row.
   * @param {Object} file The file metadata object.
   * @returns {Element} The file entry element (table row).
   */
  createFileEntry(file) {
    const row = Utils.createElement("tr", "align-middle");
    const cellCheckbox = Utils.createElement("td", ["py-0", "mb-0"]);
    const checkbox = Utils.createElement("input", [
      "form-check-input",
      "file-checkbox",
    ]);
    const label = Utils.createElement("label", "form-check-label");

    // Configure the checkbox
    checkbox.type = "checkbox";
    checkbox.id = `file${file.id}`;
    checkbox.dataset.fileType = file.file_type;
    checkbox.checked = true;

    // Configure the label.
    label.htmlFor = checkbox.id; // Connects the label to the checkbox.
    label.textContent = file.product_id; // Assuming file object has a name property.

    const tempdiv = Utils.createElement("div", ["form-check", "mb-0", "h-100"]);
    tempdiv.appendChild(checkbox);
    tempdiv.appendChild(label); // Appends the label right after the checkbox.
    cellCheckbox.appendChild(tempdiv);
    row.appendChild(cellCheckbox);

    // Build the view dropdown.
    const viewer = Utils.createElement("td", ["py-0", "mb-0", "text-end"]);
    const viewDropdown = Utils.createElement("div", "dropdown");
    const viewLink = Utils.createElement("a", [
      "btn",
      "btn-link",
      "dropdown-toggle",
      "pt-0",
    ]);
    viewLink.href = "#";
    viewLink.setAttribute("role", "button");
    viewLink.setAttribute("data-toggle", "dropdown");
    viewLink.setAttribute("aria-expanded", "false");
    viewLink.textContent = "View";

    // Build the dropdown menu.
    const ul = Utils.createElement("ul", ["dropdown-menu", "dropdown-menu-right"]);
    const li1 = Utils.createElement("li");
    const li2 = Utils.createElement("li");
    const li3 = Utils.createElement("li");
    const button1 = Utils.createElement("button", ["dropdown-item", "header-button"]);
    button1.setAttribute("type", "button");
    button1.setAttribute("aria-current", "true");
    button1.textContent = "Header";
    button1.dataset.fileId = file.id;
    const divider = Utils.createElement("hr", "dropdown-divider");
    const button2 = Utils.createElement("button", ["dropdown-item", "js9-button"]);
    button2.setAttribute("type", "button");
    button2.setAttribute("aria-current", "true");
    button2.textContent = "JS9";
    button2.dataset.url = file.url;

    li1.appendChild(button1);
    li2.appendChild(divider);
    li3.appendChild(button2);
    ul.append(li1, li2, li3);
    viewDropdown.append(viewLink, ul);
    viewer.appendChild(viewDropdown);

    row.appendChild(viewer);

    return row;
  }

  /**
   * Binds a handler to the event that triggers showing the header.
   * @param {Function} handler The function to call when the header needs to be shown.
   */
  bindShowHeader(handler) {
    this.onShowHeader = handler;
  }

  bindSwitchTab(handler) {
    this.onSwitchTab = handler;
  }

  bindSubmitFileGroupingsAndFilterForm(handler) {
    this.onSubmitFileGroupingsAndFilterForm = handler;
  }

  /**
   * Initialize local event listeners for the component.
   * Sets up handlers to manage user interactions within the files and recipes container.
   */
  _initLocalListeners() {
    // Listen for changes to checkboxes within the files container to toggle file state.
    this.filesAndRecipesContainer.addEventListener("change", (event) => {
      if (event.target.classList.contains("file-checkbox")) {
        // Identify the specific table section (tbody) based on the file type
        const fileType = event.target.dataset.fileType;
        const tbody = document.getElementById(`tbody-${fileType}`);

        // Collect all checkboxes within the tbody
        const allCheckboxes = tbody.querySelectorAll("input[type='checkbox']");

        // Determine the overall check state
        const allChecked = Array.from(allCheckboxes).every(
          (checkbox) => checkbox.checked
        );

        // Locate the header checkbox in the corresponding thead
        const thead = document.getElementById(`thead-${fileType}`);
        const headerCheckbox = thead.querySelector("input[type='checkbox']");

        // Update the header checkbox state.
        headerCheckbox.checked = allChecked;
      }
    });

    // Listen for changes to the run selection dropdown to load different runs.
    this.runSelect.addEventListener("change", (event) => {
      let selectedRun = event.target.value;
      this.run = selectedRun;
      this.onChangeRun(selectedRun);
    });

    // Handle visibility toggling for starting a new run form.
    this.startNewRun.addEventListener("change", () => {
      this.toggleFormVisibility(true);
      this.runSelect.options[0].selected = true;
      this.filesAndRecipesContainer.innerHTML = "";
      this.setRunControlsDisabledState(true);
      // Reset the run table.
      this.resetRunTable();
    });

    // Handle visibility toggling for using an existing run form.
    this.useExistingRun.addEventListener("change", () => {
      this.toggleFormVisibility(false);
      this.setRunControlsDisabledState(false);
    });

    // Prevent form submission from refreshing the page and submit form data manually.
    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(this.form);
      this.formSubmitHandler(this.observationRecordId, formData);
    });

    // Listen for clicks on header buttons to trigger specific actions like showing file
    // details or showing recipes in recipe reduction container.
    this.filesAndRecipesContainer.addEventListener("click", (event) => {
      if (event.target.classList.contains("header-button")) {
        const fileId = event.target.dataset.fileId;
        this.onShowHeader(fileId);
      }
      if (event.target.dataset.action) {
        const action = event.target.dataset.action;
        switch (action) {
          case "switchTab":
            this.onSwitchTab(event.target.dataset.recipeId);
            this.activateTab(event.target.dataset.recipeId);
            break;
          case "submitFileGroupingsAndFilterForm":
            event.preventDefault();
            let formData = new FormData(event.target.form);
            this.onSubmitFileGroupingsAndFilterForm(formData);
            break;
          case "selectAll":
            const isChecked = event.target.checked;
            const tbody = document.getElementById(
              `tbody-${event.target.dataset.fileType}`
            );
            const checkboxes = tbody.querySelectorAll("input[type='checkbox']");
            checkboxes.forEach((checkbox) => (checkbox.checked = isChecked));
            break;
          default:
            break;
        }
      }

      // Open a new window to display JS9 analysis if a JS9 button is clicked.
      if (event.target.classList.contains("js9-button")) {
        const url = event.target.dataset.url;
        openJS9Window(url);
      }
    });
  }

  /**
   * Activates the tab that matches the specified file type and deactivates the rest.
   * @param {string} fileType The file type of the tab to activate.
   */
  activateTab(recipeId) {
    Array.from(this.filesAndRecipesContainer.querySelectorAll(".nav-link")).forEach(
      (tab) => {
        // Remove the 'active' class from all tabs.
        tab.classList.remove("active");
        // Add 'active' to the tab that matches the file type.
        if (tab.dataset.recipeId === recipeId) {
          tab.classList.add("active");
        }
      }
    );
  }
  /**
   * Shows or hides the setup form based on the user's selection.
   * @param {boolean} isVisible True to show the form, false to hide.
   */
  toggleFormVisibility(isVisible) {
    this.form.classList.toggle("d-none", !isVisible);
  }

  /**
   * Binds the form submission to a handler function.
   * @param {Function} handler The function to handle form submission.
   */
  bindFormSubmit(handler) {
    this.formSubmitHandler = handler;
  }

  /**
   * Updates the table with files based on the selected file group.
   * @param {string} fileType The type of the files.
   * @param {Array<Object>} files Array of file objects to display in the table.
   */
  updateFileTable(fileType, files) {
    const tbody = document.getElementById(`tbody-${fileType}`);
    // Loop through each file and create a detailed view for it.
    tbody.innerHTML = "";
    files.forEach((file) => {
      const fileRow = this.createFileEntry(file);
      tbody.appendChild(fileRow);
    });
  }

  /**
   * Populates the file group selection dropdown and sets up the file display.
   * @param {string} fileType The type of files, used to build unique identifiers for HTML elements.
   * @param {Array<Object>} groups Array of file group objects.
   */
  updateAvailableFileGroups(fileType, groups) {
    const select = document.getElementById(`availableFileGroups-${fileType}`);
    // Clear existing options.
    while (select.options.length > 0) {
      select.remove(0);
    }

    // Populate with new options and setup event listeners.
    groups.forEach((group, index) => {
      // Determine the correct label for the option.
      const option = new Option(
        `${Utils.truncateText(group.groupName)} ${Utils.getFileCountLabel(
          group.count
        )}`,
        group.groupName
      );
      select.add(option);

      // Set the first option as selected by default and render its files.
      if (index === 0) {
        select.selectedIndex = 0;
        this.updateFileTable(fileType, group.files);
      }
    });

    // Handle changes in selection
    select.onchange = () => {
      const selectedGroup = groups.find((g) => g.groupName === select.value);
      this.updateFileTable(fileType, selectedGroup.files);
    };
  }
}

/**
 * Coordinates interactions between the setup model and view.
 */
class SetupController {
  constructor(model, view) {
    this.model = model;
    this.view = view;

    // When the form is submitted, handle the data submission.
    this.view.bindFormSubmit(this.handleFormSubmit);

    // Bind the view's request to fetch files to the controller's method.
    // This allows the controller to respond to user actions triggered in the view.
    this.view.bindFetchFiles(this.handleUpdateFiles);

    // When a header is requested.
    this.view.bindShowHeader(this.handleFetchHeader);

    this.view.bindSubmitFileGroupingsAndFilterForm(
      this.handleSubmitFileGroupsAndFilterForm
    );
  }

  /**
   * Handles the form submission, invoking the model to submit the form data.
   * @param {FormData} formData The data from the setup form.
   */
  handleFormSubmit = async (observationRecordId, formData) => {
    try {
      await this.model.formSubmit(observationRecordId, formData);
      this.view.resetForm();
      this.handleFetchRuns(observationRecordId);
    } catch (error) {
      console.error("Setup form submission failed:", error);
    }
  };
  /**
   * Fetches and displays files and recipes associated with a specific run.
   * @param {string} runId The ID of the run for which files and recipes are to be fetched.
   * @returns {Promise<void>} A promise that resolves when both files and recipes have been fetched
   * and displayed.
   */
  handleUpdateFiles = async (runId) => {
    try {
      // Fetch the run information so I can display that.
      // TODO: Use the stored runs and make it so I just grab it by ID.
      const run = await this.model.fetchRun(runId);
      this.view.displayRun(run);

      const files = await this.model.fetchFileList(runId);
      const recipes = await this.model.fetchRecipes(runId);
      // Provide the groups for the files grouping.
      this.view.displayFilesAndRecipes(files, recipes, run.groups);
    } catch (error) {
      console.error("Failed to update files:", error);
    }
  };

  /**
   * Fetches header data and updates the modal to display it.
   * @param {string} fileId The ID of the file for which to fetch and display the header.
   */
  handleFetchHeader = async (fileId) => {
    try {
      const data = await this.model.fetchHeader(fileId);
      this.view.updateHeaderModal(data);
      this.view.showHeaderModal();
    } catch (error) {
      console.error("Failed to fetch header:", error);
    }
  };
  /**
   * Fetches and displays the list of runs associated with a specific observation record.
   * @param {string} observationRecordId The ID of the observation record for which to fetch runs.
   * @returns {Promise<void>} A promise that resolves when the runs have been fetched and displayed.
   */
  handleFetchRuns = async (observationRecordId) => {
    try {
      const runs = await this.model.fetchRuns(observationRecordId);
      this.view.displayRuns(runs);
    } catch (error) {
      console.error("Failed to fetch runs:", error);
    }
  };

  /**
   * Submits form data after formatting it correctly for handling groupings and filters.
   * @param {FormData} formData The FormData object containing form inputs from the user.
   */
  handleSubmitFileGroupsAndFilterForm = async (formData) => {
    // Put all data in the correct format for the handler.
    // Create array from 'group_by'.
    let groupBy = formData.getAll("group_by");
    // Handle 'strict_filter' to ensure it is boolean.
    let filterStrict = formData.get("filter_strict") === "on";
    // Handle 'filter_expression' to ensure it defaults to an empty string if not provided.
    let filterExpression = formData.get("filter_expression") || "";
    let fileType = formData.get("file_type");
    let objectName = formData.get("object_name");

    const response = await this.model.fetchGroupAndFilterFiles(
      this.view.runId,
      groupBy,
      fileType,
      objectName,
      filterExpression,
      filterStrict
    );

    // Get the accordion to update.
    const id = objectName ? `${fileType} | ${objectName}` : fileType;
    const groups = this.extractGroups(response);

    // Determine the identifier based on objectName.
    const identifier = objectName ? `${fileType} | ${objectName}` : fileType;

    // Update UI components.
    this.view.updateAvailableFileGroups(identifier, groups);
  };

  /**
   * Parses JSON data to extract groups and files information.
   * @param {Object} data The JSON data object.
   * @returns {Object[]} An array of group objects with their names and files.
   */
  extractGroups(data) {
    let groups = [];

    if (data.hasOwnProperty("results")) {
      // If the 'results' key exists, treat it as a single group named "All".
      groups.push({
        groupName: "All",
        files: data.results,
        count: data.count,
      });
    } else {
      // Otherwise, iterate through the top-level keys which are the groups.
      for (let groupName in data) {
        if (data.hasOwnProperty(groupName) && typeof data[groupName] === "object") {
          groups.push({
            groupName: groupName,
            files: data[groupName].files,
            count: data[groupName].count,
          });
        }
      }
    }

    return groups;
  }
}
