/**
 * Manages setup data and interactions with the API for run configuration.
 */
class SetupModel {
  constructor(api) {
    this.api = api;
    this.runs = [];
    this.files = [];
  }

  /**
   * Updates the enabled status of a specific file.
   * @param {string} filePk - The primary key of the file to update.
   * @param {boolean} isEnabled - The new enabled state to set for the file.
   */
  async updateFile(filePk, isEnabled) {
    const fileData = { enabled: isEnabled };
    try {
      const response = await this.api.patch(`dragonsfiles/${filePk}/`, fileData);
      this.onFileChanged(response);
    } catch (error) {
      console.error("Error updating file state:", error);
      throw error; // Consider rethrowing to handle in the controller
    }
  }

  /**
   * Submits setup data to initialize a new DRAGONS run and updates runs.
   * @param {FormData} formData - Setup data from the form.
   */
  async formSubmit(observationRecordPk, formData) {
    const formDataObject = Object.fromEntries(formData);

    try {
      const response = await this.api.post(
        `dragonsruns/?observation_record=${observationRecordPk}`,
        formDataObject
      );
    } catch (error) {
      console.error("Error initializing DRAGONS run:", error);
      throw error;
    }
  }

  /**
   * Registers a callback to be called when runs data changes.
   * @param {Function} callback - Function to call on data change.
   */
  bindRunsChanged(callback) {
    this.onRunsChanged = callback;
  }

  /**
   * Registers a callback to be called when the file list changes.
   * @param {Function} callback - The callback function to register.
   */
  bindFileListChanged(callback) {
    this.onFileListChanged = callback;
  }

  /**
   * Registers a callback to be called when the file changes.
   * @param {Function} callback - The callback function to register.
   */
  bindFileChanged(callback) {
    this.onFileChanged = callback;
  }

  /**
   * Fetches the file list for a given run ID and updates the model.
   * @param {string} observationRecordPk - The ID for the observation.
   * @param {string} runId - The ID of the run for which to fetch the file list.
   */
  async fetchFileList(observationRecordPk, runId) {
    try {
      const response = await this.api.get(
        `dragonsfiles/?group_by_file_type=true&dragons_run=${runId}`
      );
      this.files = response.results || [];
      this.onFileListChanged(this.files);
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  }

  /**
   * Fetches the runs for a given observation record and updates the model.
   * @param {string} observationRecordPk - The ID for the observation.
   */
  async fetchRuns(observationRecordPk) {
    try {
      const response = await this.api.get(
        `dragonsruns/?observation_record=${observationRecordPk}`
      );
      this.runs = response.results || [];
      this.onRunsChanged(this.runs);
    } catch (error) {
      console.error("Error fetching runs:", error);
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
    this.filesContainer = this.card.querySelector("#filesContainer");
    this.observationRecordPk = this.card.dataset.observationRecordPk;
    this.deleteRun = this.card.querySelector("#deleteRun");
    this.refreshRuns = this.card.querySelector("#refreshRuns");

    // Set up event listeners for UI interactions.
    this._initLocalListeners();
  }

  /**
   * Creates a new HTML element with optional class names.
   * @param {string} tag - The tag name of the element to create.
   * @param {string | string[]} classNames - The class name(s) to add to the element.
   * @returns {Element} The newly created element.
   */
  createElement(tag, classNames) {
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
   * Populates the run selection dropdown with options based on available runs.
   * @param {Array} runs - DRAGONS run objects to display in the select dropdown.
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
   * Renders the files within the UI.
   * @param {Object[]} files - Object of file metadata.
   */
  displayFiles(files) {
    this.filesContainer.innerHTML = "";

    const filesContainerP = this.createElement("p", "mb-0");

    if (Object.keys(files).length === 0) {
      filesContainerP.textContent = "No Files Found";
      this.filesContainer.appendChild(filesContainerP);
    } else {
      filesContainerP.textContent = "Available Files";
      this.filesContainer.appendChild(filesContainerP);
      // Create accordion for each file type
      Object.entries(files).forEach(([fileType, file], index) => {
        const accordionItem = this.createAccordionItem(fileType, file, index);
        filesContainer.appendChild(accordionItem);
      });
    }
  }

  /**
   * Binds the action to fetch files when the fetch button is clicked.
   * @param {Function} handler - The function to call when fetching files.
   */
  bindFetchFiles(handler) {
    this.runSelect.addEventListener("change", (event) => {
      let selectedRun = event.target.value;
      handler(this.observationRecordPk, selectedRun);
    });
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
   * @param {boolean} disable - If true, disables the control elements; if false, enables them.
   */
  setRunControlsDisabledState(disable) {
    this.runSelect.disabled = disable;
    this.refreshRuns.disabled = disable;
    this.deleteRun.disabled = disable;
  }

  /**
   * Creates an accordion item for a specific file type.
   * @param {string} fileType - The file type to create an accordion for.
   * @param {Object[]} files - The files associated with the file type.
   * @param {number} index - The index of the accordion item.
   * @returns {Element} The accordion item element.
   */
  createAccordionItem(fileType, files, index) {
    // Create the outer container for the accordion item with the 'accordion-item' class.
    const accordionItem = this.createElement("div", "accordion-item");

    // Generate unique IDs for the header and collapse elements based on the index.
    const headerId = `heading-${index}`;
    const collapseId = `collapse-${index}`;

    // Create the header for the accordion item with a button that toggles the collapse.
    const header = this.createElement("h2", "accordion-header");
    header.id = headerId;
    const button = this.createElement("button", [
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
    const collapse = this.createElement("div", ["accordion-collapse", "collapse"]);
    collapse.id = collapseId;
    collapse.setAttribute("aria-labelledby", headerId);
    collapse.setAttribute("data-parent", "#filesContainer");

    // Create the body content area for the collapsible section.
    const body = this.createElement("div", ["accordion-body", "accordian-overflow"]);
    const table = this.createElement("table", [
      "table",
      "table-sm",
      "table-borderless",
    ]);
    const tbody = this.createElement("tbody");
    // Loop through each file and create a detailed view for it.
    files.forEach((file) => {
      const fileRow = this.createFileEntry(file);
      tbody.appendChild(fileRow);
    });
    table.appendChild(tbody);
    body.appendChild(table);
    collapse.appendChild(body);

    // Construct the complete accordion item by adding both header and collapse sections.
    accordionItem.appendChild(header);
    accordionItem.appendChild(collapse);

    // Return the fully constructed accordion item.
    return accordionItem;
  }

  /**
   * Creates a single file entry within the accordion as a table row.
   * @param {Object} file - The file metadata object.
   * @returns {Element} The file entry element (table row).
   */
  createFileEntry(file) {
    const row = this.createElement("tr");
    const cellCheckbox = this.createElement("td", ["form-check", "py-0", "mb-0"]);
    const checkbox = this.createElement("input", ["form-check-input", "file-checkbox"]);
    const label = this.createElement("label", "form-check-label");

    // Configure the checkbox
    checkbox.type = "checkbox";
    checkbox.id = `file${file.id}`;
    checkbox.dataset.filePk = file.id; // Store file ID for easy access in event handlers.
    checkbox.checked = file.enabled;

    // Configure the label.
    label.htmlFor = checkbox.id; // Connects the label to the checkbox.
    label.textContent = file.product_id; // Assuming file object has a name property.

    cellCheckbox.appendChild(checkbox);
    cellCheckbox.appendChild(label); // Appends the label right after the checkbox.
    row.appendChild(cellCheckbox);

    // Build the additional data to display.
    const cellObsDate = this.createElement("td", "py-0");
    cellObsDate.textContent = file.observation_date;
    row.appendChild(cellObsDate);

    return row;
  }

  /**
   * Binds the file toggle to a handler function.
   * @param {Function} handler - The function to handle file toggle.
   */
  bindFileToggle(handler) {
    this.onFileToggle = handler;
  }

  /**
   * Sets up event listeners for form submission and radio button changes.
   */
  _initLocalListeners() {
    // Delegate checkbox changes in the files container.
    this.filesContainer.addEventListener("change", (event) => {
      if (event.target.classList.contains("file-checkbox")) {
        const filePk = event.target.dataset.filePk;
        const isChecked = event.target.checked;
        this.onFileToggle(filePk, isChecked);
      }
    });

    this.startNewRun.addEventListener("change", () => {
      this.toggleFormVisibility(true);
      this.runSelect.options[0].selected = true;
      this.filesContainer.innerHTML = "";
      this.setRunControlsDisabledState(true);
    });

    this.useExistingRun.addEventListener("change", () => {
      this.toggleFormVisibility(false);
      this.setRunControlsDisabledState(false);
    });

    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(this.form);
      this.formSubmitHandler(this.observationRecordPk, formData);
    });
  }

  /**
   * Shows or hides the setup form based on the user's selection.
   * @param {boolean} isVisible - True to show the form, false to hide.
   */
  toggleFormVisibility(isVisible) {
    this.form.classList.toggle("d-none", !isVisible);
  }

  /**
   * Binds the form submission to a handler function.
   * @param {Function} handler - The function to handle form submission.
   */
  bindFormSubmit(handler) {
    this.formSubmitHandler = handler;
  }

  /**
   * Updates the checked state of a checkbox based on the provided file data.
   * @param {Object} data - An object containing the file's ID and its enabled state.
   */
  updateFile(data) {
    document.getElementById(`file${data.id}`).checked = data.enabled;
  }
}

/**
 * Coordinates interactions between the setup model and view.
 */
class SetupController {
  constructor(model, view) {
    this.model = model;
    this.view = view;

    // When a file is enabled or disabled.
    this.view.bindFileToggle(this.handleFileToggle);

    // When the form is submitted, handle the data submission.
    this.view.bindFormSubmit(this.handleFormSubmit);

    // When the model's run data changes, update the view with the new runs
    this.model.bindRunsChanged(this.onRunsChanged);

    // When the model's file data changes, update the view with the new state.
    this.model.bindFileChanged(this.onFileChanged);

    // Bind the model's change event to the controller's method to update the view.
    // This ensures the view gets updated when the model's data changes.
    this.model.bindFileListChanged(this.onFileListChanged);

    // Bind the view's request to fetch files to the controller's method.
    // This allows the controller to respond to user actions triggered in the view.
    this.view.bindFetchFiles(this.handleFetchFiles);
  }

  /**
   * Handles the file toggle, invoking the model to update the file.
   *
   * @param {string} filePk - The file to update.
   * @param {boolean} isChecked - If the file is enabled.
   */
  handleFileToggle = async (filePk, isChecked) => {
    try {
      await this.model.updateFile(filePk, isChecked);
    } catch (error) {
      console.error("Error updating file:", error);
    }
  };

  /**
   * Callback to be executed when the model notifies of file change.
   *
   * @param {Object} file - Object with file information.
   */
  onFileChanged = (file) => {
    this.view.updateFile(file);
  };

  /**
   * Handles the form submission, invoking the model to submit the form data.
   *
   * @param {FormData} formData The data from the setup form.
   */
  handleFormSubmit = async (observationRecordPk, formData) => {
    try {
      await this.model.formSubmit(observationRecordPk, formData);
      this.view.resetForm();
      await this.model.fetchRuns(observationRecordPk);
    } catch (error) {
      console.error("Setup form submission failed:", error);
    }
  };

  /**
   * Callback to be executed when the model notifies of runs data change.
   * Updates the view to display the new list of runs.
   *
   * @param {Array} runs The updated list of runs.
   */
  onRunsChanged = (runs) => {
    this.view.displayRuns(runs);
  };

  /**
   * Callback to be executed when the model notifies of a file list change.
   *
   * @param {Array} fileList - The updated list of files.
   */
  onFileListChanged = (fileList) => {
    this.view.displayFiles(fileList);
  };

  /**
   * Handles requests to fetch files based on a run ID.
   *
   * @param {string} observationRecordPk - The ID for the observation record.
   * @param {string} runId - The run ID for which files should be fetched.
   */
  handleFetchFiles = async (observationRecordPk, runId) => {
    await this.model.fetchFileList(observationRecordPk, runId);
  };

  /**
   * Handles requests to fetch runs based on a observation record ID.
   *
   * @param {string} observationRecordPk - The ID for the observation record.
   */
  handleFetchRuns = async (observationRecordPk) => {
    await this.model.fetchRuns(observationRecordPk);
  };
}
