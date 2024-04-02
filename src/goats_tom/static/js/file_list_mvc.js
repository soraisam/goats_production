/**
 * Manages the data related to the file list.
 */
class FileListModel {
  /**
   * Constructs a new FileListModel instance.
   * @param {Object} api - The API service for fetching file data.
   */
  constructor(api) {
    this.api = api;
    this.files = [];
  }

  /**
   * Registers a callback to be called when the file list changes.
   * @param {Function} callback - The callback function to register.
   */
  bindFileListChanged(callback) {
    this.onFileListChanged = callback;
  }

  /**
   * Fetches the file list for a given run ID and updates the model.
   * @param {string} runId - The ID of the run for which to fetch the file list.
   */
  async fetchFileList(runId) {
    try {
      const response = await this.api.get(
        `${runId}/dragons-file-list/?sort_by_file_type=true`
      );
      this.files = response.dragons_files_metadata || [];
      this.onFileListChanged(this.files);
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  }
}

/**
 * Represents the view in the MVC architecture, responsible for UI rendering and interactions.
 */
class FileListView {
  /**
   * Constructs a new FileListView instance.
   */
  constructor() {
    this.card = document.getElementById("fileListCard");
    this.filesContainer = this.card.querySelector("#filesAccordionContainer");
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
   * Renders the files within the UI.
   * @param {Object[]} files - An array of file metadata objects.
   */
  displayFiles(files) {
    this.filesContainer.innerHTML = "";

    if (files.length === 0) {
      const p = this.createElement("p");
      p.textContent = "No files found";
      this.filesContainer.append(p);
    } else {
      // Create accordion for each file type
      const accordionFiles = this.createElement("div", [
        "accordion",
        "accordion-flush",
      ]);
      Object.entries(files).forEach(([fileType, file], index) => {
        const accordionItem = this.createAccordionItem(fileType, file, index);
        accordionFiles.appendChild(accordionItem);
      });
      this.filesContainer.appendChild(accordionFiles);
    }
  }

  /**
   * Binds the action to fetch files when the fetch button is clicked.
   * @param {Function} handler - The function to call when fetching files.
   */
  bindFetchFiles(handler) {
    document.getElementById("generateFilesListBtn").addEventListener("click", () => {
      const runId = document.getElementById("dragonsRunsSelect").value;
      if (runId) {
        handler(runId);
      }
    });
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
    collapse.setAttribute("data-parent", "#filesAccordionContainer");

    // Create the body content area for the collapsible section.
    const body = this.createElement("div", "accordion-body");
    // Loop through each file and create a detailed view for it.
    files.forEach((file) => {
      const fileDiv = this.createFileEntry(file);
      body.appendChild(fileDiv);
    });
    collapse.appendChild(body);

    // Construct the complete accordion item by adding both header and collapse sections.
    accordionItem.appendChild(header);
    accordionItem.appendChild(collapse);

    // Return the fully constructed accordion item.
    return accordionItem;
  }

  /**
   * Creates a single file entry within the accordion.
   * @param {Object} file - The file metadata object.
   * @returns {Element} The file entry element.
   */
  createFileEntry(file) {
    const fileDiv = this.createElement("div");
    fileDiv.textContent = `${file.filename} - ${file.object_name}`;
    // Add more details or interactive elements to each file entry as needed
    return fileDiv;
  }
}

/**
 * Represents the controller in the MVC architecture, acting as an intermediary
 * between the model (data) and the view (UI).
 */
class FileListController {
  /**
   * Constructs the FileListController.
   *
   * @param {FileListModel} model - The model that manages the data.
   * @param {FileListView} view - The view that displays the data.
   */
  constructor(model, view) {
    this.model = model;
    this.view = view;

    // Bind the model's change event to the controller's method to update the view.
    // This ensures the view gets updated when the model's data changes.
    this.model.bindFileListChanged(this.onFileListChanged);

    // Bind the view's request to fetch files to the controller's method.
    // This allows the controller to respond to user actions triggered in the view.
    this.view.bindFetchFiles(this.handleFetchFiles);
  }

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
   * @param {string} runId - The run ID for which files should be fetched.
   */
  handleFetchFiles = async (runId) => {
    await this.model.fetchFileList(runId);
  };
}
