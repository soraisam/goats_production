const FILE_TYPE_2_DISPLAY = {
  BIAS: "Create Master Bias",
  FLAT: "Create Master Flat Field",
  DARK: "Create Master Dark",
  ARC: "Create Master Arc",
  PINHOLE: "Create Master Pinhole",
  RONCHI: "Create Master Ronchi",
  FRINGE: "Create Master Fringe",
  BPM: "Create BPM",
  standard: "Reduce Standard",
  object: "Reduce Science",
  other: "Error",
};

const STATUS_2_PROGRESS_BAR_COLOR = {
  queued: "bg-primary bg-opacity-25",
  initializing: "bg-primary bg-opacity-50",
  error: "bg-danger",
  running: "bg-primary",
  done: "bg-success",
  canceled: "bg-warning",
};

const EDITOR_DARK_THEME = "ace/theme/cloud9_night";
const EDITOR_LIGHT_THEME = "ace/theme/dawn";

/**
 * Represents a model for managing recipe in the DRAGONS system.
 */
class RecipeModel {
  /**
   * Constructor for the RecipesModel class.
   * @param {Object} api The API service used for fetching recipes data.
   */
  constructor(api) {
    this.api = api;
    this.recipe = null;
    this.recipesUrl = "dragonsrecipes/";
    this.reduceUrl = "dragonsreduce/";
  }

  /**
   * Fetches a specific recipe by its ID.
   * @param {number} recipeId The ID of the recipe to fetch.
   * @returns {Promise<Object>} A promise that resolves to the recipe object.
   */
  async fetchRecipe(recipeId) {
    try {
      const response = await this.api.get(`${recipesUrl}${recipeId}/`);
      this.recipe = response;
      return response;
    } catch (error) {
      console.error("Error fetching recipe:", error);
    }
  }

  /**
   * Starts the reduction process for a given recipe.
   * @param {number} recipe The ID of the recipe to be reduced.
   * @returns {Promise<Object>} A promise that resolves to the response from the server.
   * @async
   */
  async startReduce(recipe) {
    const data = { recipe_id: recipe };
    try {
      const response = await this.api.post(`${this.reduceUrl}`, data);
      return response;
    } catch (error) {
      console.error("Error starting reduce:", error);
    }
  }

  /**
   * Stops the reduction process.
   * @param {number} reduce The ID of the reduction to be stopped.
   * @returns {Promise<Object>} A promise that resolves to the response from the server.
   * @async
   */
  async stopReduce(reduce) {
    const data = { status: "canceled" };
    try {
      const response = await this.api.patch(`${this.reduceUrl}${reduce}/`, data);
      return response;
    } catch (error) {
      console.error("Error stopping reduce:", error);
    }
  }
}

/**
 * Represents the view for recipe in the DRAGONS system.
 */
class RecipeView {
  /**
   * Constructor for the RecipesView class.
   */
  constructor() {
    this.accordionSetups = {
      buttons: {
        recipeAccordion: "Modify Recipe",
        logAccordion: "View Log",
      },
      callbacks: {
        recipeAccordion: this.createRecipeAccordionItem.bind(this),
        logAccordion: this.createLogAccordionItem.bind(this),
      },
      classes: {
        recipeAccordion: [],
        logAccordion: ["p-0", "border", "border-top-0", "rounded-bottom"],
      },
    };
    this.editor = null;
    this.recipe = null;
    this.logger = null;
    this.progressBar = null;
    this.card = null;
    this.cardHeader = null;
    this.reduce = null;
    this.progressStatus = null;
    this.stopButton = null;
    this.startButton = null;
  }

  /**
   * Binds a handler to be called when the reduction process is initiated.
   * @param {Function} handler The function to be called when a start reduce event occurs.
   */
  bindStartReduce(handler) {
    this.onStartReduce = handler;
  }

  /**
   * Binds a handler to be called when the reduction process needs to be stopped.
   * @param {Function} handler The function to be called when a stop reduce event occurs.
   */
  bindStopReduce(handler) {
    this.onStopReduce = handler;
  }

  /**
   * Initializes event listeners on the card header. Listeners are set up to handle
   * start and stop reduce actions based on data attributes of the event target.
   * @private
   */
  _initLocalListeners() {
    this.cardHeader.addEventListener("click", (event) => {
      if (event.target.dataset.action) {
        const action = event.target.dataset.action;
        switch (action) {
          case "startReduce":
            // On start, pass in the recipe to link to.
            this.onStartReduce(event.target.dataset.recipeId);
            break;
          case "stopReduce":
            // On stop, need to specify what specific reduce to stop.
            this.onStopReduce(event.target.dataset.reduceId);
            break;
          default:
            console.log("No action defined for this button");
        }
      }
    });
  }
  /**
   * Retrieves the display name for a given recipe file type.
   * @param {string} recipeFileType The file type of the recipe.
   * @returns {string} The user-friendly name corresponding to the recipe file type.
   */
  getDisplayName(recipeFileType) {
    return FILE_TYPE_2_DISPLAY[recipeFileType] || `Name Not Found: ${recipeFileType}`;
  }

  /**
   * Creates a card element for a recipe.
   * @param {Object} recipe The recipe object to create a card for.
   * @returns {HTMLElement} The created card element with populated recipe data.
   */
  createCard(recipe) {
    this.recipe = recipe;

    // Build and append the header.
    const card = Utils.createElement("div", "card");
    this.cardHeader = this.createCardHeader();
    card.appendChild(this.cardHeader);

    // Build and append the body.
    const cardBody = this.createCardBody();
    card.append(cardBody);

    // Build and append first footer (progress bar).
    const cardFooter1 = this.createCardFooter1();
    card.appendChild(cardFooter1);

    // Build and append second footer (log viewer).
    const cardFooter2 = this.createCardFooter2();
    card.appendChild(cardFooter2);
    this.card = card;

    // This is the entry so init the listeners here.
    this._initLocalListeners();

    return card;
  }

  /**
   * Creates the card body.
   * @returns {HTMLElement} The card body.
   */
  createCardBody() {
    const cardBody = Utils.createElement("div", "card-body");
    const row = Utils.createElement("div", ["row", "g-0"]);
    const col1 = Utils.createElement("div", ["col-12"]);
    const col2 = Utils.createElement("div", ["col-12"]);
    const progressBarDiv = this.createProgressBar();
    const progressStatusDiv = this.createProgressStatus();

    col1.appendChild(progressStatusDiv);
    col2.appendChild(progressBarDiv);
    row.append(col1, col2);
    cardBody.appendChild(row);
    return cardBody;
  }

  /**
   * Creates a header for the recipe card, containing dynamic elements based on the recipe's data.
   * @returns {HTMLElement} The card header element.
   */
  createCardHeader() {
    const cardHeader = Utils.createElement("div", "card-header");
    const row = Utils.createElement("div", ["row"]);
    const col1 = Utils.createElement("div", ["col", "align-self-center"]);
    const col2 = Utils.createElement("div", ["col", "text-end"]);

    // Create content for column 1.
    const p = Utils.createElement("p", ["my-0"]);
    p.textContent = this.getDisplayName(this.recipe.file_type);
    col1.appendChild(p);

    // Create content for column 2
    const startButton = Utils.createElement("button", ["btn", "btn-success", "me-1"]);
    const stopButton = Utils.createElement("button", ["btn", "btn-danger"]);
    startButton.dataset.recipeId = this.recipe.id;
    startButton.setAttribute("data-action", "startReduce");
    startButton.textContent = "Start";
    this.startButton = startButton;
    stopButton.dataset.reduceId = null;
    stopButton.textContent = "Stop";
    stopButton.setAttribute("data-action", "stopReduce");
    stopButton.disabled = true;
    this.stopButton = stopButton;
    col2.append(startButton, stopButton);

    // Build the layout.
    row.append(col1, col2);

    cardHeader.appendChild(row);
    return cardHeader;
  }

  /**
   * Creates the first footer for the recipe.
   * @return {HTMLElement} The footer.
   */
  createCardFooter1() {
    // Create footer.
    const cardFooter = Utils.createElement("div", "card-footer");
    const recipeAccordion = this.createAccordion("recipeAccordion");
    cardFooter.appendChild(recipeAccordion);
    return cardFooter;
  }

  /**
   * Creates the second footer for the recipe, showing the log.
   * @returns {HTMLElement} The footer.
   */
  createCardFooter2() {
    const cardFooter = Utils.createElement("div", ["card-footer"]);
    const loggerAccordion = this.createAccordion("logAccordion");

    cardFooter.appendChild(loggerAccordion);

    return cardFooter;
  }

  /**
   * Creates a collapsible accordion element.
   * @param {string} name The name to use for accordion ID and nested IDs.
   * @returns {HTMLElement} The accordion element.
   */
  createAccordion(name) {
    // Set the ID to reference the recipe ID all the recipe belong to.
    const accordionId = this.getId(name);
    const accordion = Utils.createElement("div", ["accordion", "accordion-flush"]);
    accordion.id = accordionId;

    const accordionItem = this.createAccordionItem(name);

    accordion.appendChild(accordionItem);

    return accordion;
  }

  /**
   * Helper function that generates ID for reference.
   * @param {string} type The type of element.
   * @returns {string} The ID of the element.
   */
  getId(type) {
    return `${type}-${this.recipe.id}`;
  }

  /**
   * Creates an individual accordion item within the accordion.
   * @param {string} name The name of the element to build.
   * @returns {HTMLElement} The accordion item containing interactive elements for the recipe.
   */
  createAccordionItem(name) {
    // Create IDs to use to link.
    const collapseId = this.getId(`${name}Collapse`);
    const accordionHeaderId = this.getId(`${name}AccordionHeader`);

    // Create accordion item.
    const accordionItem = Utils.createElement("div", "accordion-item");

    // Create and configure header.
    const accordionHeader = Utils.createElement("h2", "accordion-header");
    accordionHeader.id = accordionHeaderId;

    // Create and configure accordion button.
    const accordionButton = Utils.createElement("button", [
      "accordion-button",
      "collapsed",
    ]);
    accordionButton.setAttribute("type", "button");
    accordionButton.setAttribute("data-toggle", "collapse");
    accordionButton.setAttribute("data-target", `#${collapseId}`);
    accordionButton.setAttribute("aria-expanded", "false");
    accordionButton.setAttribute("aria-controls", collapseId);
    accordionButton.textContent = this.accordionSetups.buttons[name];
    accordionHeader.appendChild(accordionButton);
    accordionItem.appendChild(accordionHeader);

    // Create the collaspible body section that will contain recipe.
    const collapse = Utils.createElement("div", ["accordion-collapse", "collapse"]);
    collapse.id = collapseId;
    collapse.setAttribute("aria-labelledby", accordionHeaderId);

    collapse.setAttribute("data-parent", `#${this.getId(name)}`);

    const accordionBody = Utils.createElement("div", [
      "accordion-body",
      ...this.accordionSetups.classes[name],
    ]);

    this.accordionSetups.callbacks[name](accordionBody);

    collapse.appendChild(accordionBody);
    accordionItem.appendChild(collapse);

    return accordionItem;
  }

  /**
   * Creates and configures an Ace editor instance embedded within the card.
   * @returns {HTMLElement} The div containing the configured Ace editor.
   */
  createEditor() {
    // Create code viewer.
    const codeEditorId = `editorRecipe-${this.recipe.id}`;
    const div = Utils.createElement("div", "mb-1");
    div.id = codeEditorId;
    this.editor = ace.edit(null);

    // Move cursor back to start with -1.
    this.editor.setValue(this.recipe.function_definition, -1);
    this.editor.session.setMode("ace/mode/python");

    this.editor.container.style.height = "100%";
    this.editor.container.style.width = "100%";
    this.editor.container.style.minHeight = "300px";
    this.editor.setReadOnly(true);

    div.appendChild(this.editor.container);
    this.updateEditorTheme();

    return div;
  }

  /**
   * Creates a set of buttons for actions related to the editor within the card.
   * @returns {HTMLElement} A div containing the configured buttons.
   */
  createEditorButtons() {
    const row = Utils.createElement("div", "row");
    const col1 = Utils.createElement("div", "col");
    const col2 = Utils.createElement("div", ["col", "text-end"]);

    const editToggleButton = Utils.createElement("button", [
      "btn",
      "btn-primary",
      "me-1",
    ]);
    editToggleButton.textContent = "Edit";
    editToggleButton.setAttribute("data-recipeId", this.recipe.id);
    const resetButton = Utils.createElement("button", ["btn", "btn-secondary"]);
    resetButton.textContent = "Reset";
    resetButton.setAttribute("data-recipeId", this.recipe.id);
    const helpButton = Utils.createElement("button", ["btn", "btn-link"]);
    helpButton.textContent = "Help";
    helpButton.setAttribute("data-recipeId", this.recipe.id);

    // Build the layout.
    col1.append(editToggleButton, resetButton);
    col2.appendChild(helpButton);
    row.append(col1, col2);

    return row;
  }

  /**
   * Updates the theme of the Ace editor based on the stored theme preference.
   */
  updateEditorTheme() {
    const storedTheme = localStorage.getItem("theme");
    const theme = storedTheme === "dark" ? EDITOR_DARK_THEME : EDITOR_LIGHT_THEME;
    this.editor.setTheme(theme);
  }

  /**
   * Creates and returns a div element containing the progress status.
   * @returns {HTMLElement} The div element containing the progress status.
   */
  createProgressStatus() {
    const progressStatusDiv = Utils.createElement("div");
    this.progressStatus = Utils.createElement("p", ["mb-0", "fst-italic"]);
    this.progressStatus.textContent = "Not Started";
    progressStatusDiv.appendChild(this.progressStatus);
    return progressStatusDiv;
  }

  /**
   * Creates and returns a progress bar element with initial configurations.
   * @returns {HTMLElement} The progress bar element.
   */
  createProgressBar() {
    const progressBarDiv = Utils.createElement("div", "progress");
    progressBarDiv.setAttribute("role", "progressbar");
    progressBarDiv.setAttribute("aria-label", "Recipe progress");
    progressBarDiv.setAttribute("aria-valuemin", "0");
    progressBarDiv.setAttribute("aria-valuemax", "100");

    this.progressBar = Utils.createElement("div", "progress-bar");
    this.progressBar.style.width = "0";

    progressBarDiv.appendChild(this.progressBar);

    return progressBarDiv;
  }

  /**
   * Updates the progress bar's visual appearance and textual status based on the current status of the operation.
   * @param {string} status The current status which determines the appearance of the progress bar.
   */
  updateProgressBar(status) {
    const colorClass = STATUS_2_PROGRESS_BAR_COLOR[status] || "bg-primary";

    // Set the progress bar's width and color based on the status.
    this.progressBar.style.width = "100%";
    this.progressBar.className = `progress-bar ${colorClass}`;

    // Optionally, add animation class if not idle.
    if (status === "running" || status === "initializing") {
      this.progressBar.classList.add("placeholder-wave");
    } else {
      this.progressBar.classList.remove("placeholder-wave");
    }

    // Update the status text below the progress bar.
    this.progressStatus.textContent = this.capitalizeFirstLetter(status);
  }
  /**
   * Capitalizes the first letter of the given string.
   * @param {string} string The string to capitalize.
   * @return {string} The string with the first letter capitalized.
   */
  capitalizeFirstLetter(string) {
    return string[0].toUpperCase() + string.slice(1);
  }

  /**
   * Initializes a new logger instance and creates a container for it. This function
   * sets up a log container, attaches a unique identifier based on the recipe's ID,
   * and instantiates the Logger class with this container.
   * @returns {HTMLElement} The div element that serves as the container for the logger.
   */
  createLogger() {
    const div = Utils.createElement("div", [
      "log-container",
      "log-overflow",
      "ps-2",
      "py-2",
    ]);
    div.id = `loggerRecipe-${this.recipe.id}`;
    this.logger = new Logger(div);

    return div;
  }

  /**
   * Enables the stop button and sets its associated reduce ID.
   * @param {number} reduce The reduce ID to be assigned to the stop button.
   */
  enableStopButton(reduce) {
    if (this.stopButton) {
      this.stopButton.dataset.reduceId = reduce;
      this.stopButton.disabled = false;
    }
  }

  /**
   * Disables the stop button and clears its associated reduce ID.
   */
  disableStopButton() {
    this.stopButton.disabled = true;
    this.stopButton.dataset.reduceId = null;
  }

  /**
   * Enables the start button, typically called when a new recipe is loaded
   * or the current task is completed.
   */
  enableStartButton() {
    if (this.startButton) {
      // TODO: When swapping recipes this will be used.
      this.startButton.disabled = false;
    }
  }

  /**
   * Disables the start button, typically used when a task is running.
   */
  disableStartButton() {
    this.startButton.disabled = true;
  }

  /**
   * Appends editor and editor button components to the provided accordion body.
   * @param {HTMLElement} accordionBody The accordion section where the editor and buttons will be appended.
   */
  createRecipeAccordionItem(accordionBody) {
    const editor = this.createEditor();
    const editorButtons = this.createEditorButtons();

    accordionBody.append(editor, editorButtons);
  }

  /**
   * Appends a log viewing component to the provided accordion body.
   * @param {HTMLElement} accordionBody The accordion section where the log viewer will be appended.
   */
  createLogAccordionItem(accordionBody) {
    const logger = this.createLogger();
    accordionBody.appendChild(logger);
  }
}

class RecipeController {
  /**
   * Constructor for the RecipeController class.
   * @param {RecipeModel} model The model handling the business logic and data retrieval.
   * @param {RecipeView} view The view handling the display and UI interactions.
   */
  constructor(model, view) {
    this.model = model;
    this.view = view;

    // When starting a recipe reduce.
    this.view.bindStartReduce(this.handleStartReduce);

    // When stopping a recipe reduce.
    this.view.bindStopReduce(this.handleStopReduce);
  }

  /**
   * Initiates the reduction process for a given recipe ID.
   * @param {number} recipeId The ID of the recipe to start reducing.
   * @async
   */
  handleStartReduce = async (recipeId) => {
    // Clear logger before starting.
    this.view.logger.clear();
    const reduce = await this.model.startReduce(recipeId);
    // Update the view.
    this.handleUpdateReduce(reduce);
  };

  /**
   * Handles the stop reduction process for a given reduce ID.
   * @param {number} reduceId The ID of the reduce operation to stop.
   * @async
   */
  handleStopReduce = async (reduceId) => {
    const reduce = await this.model.stopReduce(reduceId);
    // TODO: Better error handling
    // Update the view.
    this.handleUpdateReduce(reduce);
  };

  /**
   * Handles log messages and updates the logger.
   * @param {string} message - The log message to add.
   */
  handleLogMessage = (message) => {
    this.view.logger.log(message);
  };

  /**
   * Updates the progress bar and stop/start buttons based on the status provided in the data.
   * @param {Object} data The data object containing the status to update with.
   */
  handleUpdateReduce = (data) => {
    console.log(data);
    this.view.updateProgressBar(data.status);
    // Reset the stop button if the status is in these.
    if (["canceled", "done", "error"].includes(data.status)) {
      this.view.disableStopButton();
    } else {
      // Handle from websocket or API.
      this.view.enableStopButton(data?.id ?? data?.reduce_id);
    }
    // Disable start button if task running, else enable.
    if (["queued", "running", "initializing"].includes(data.status)) {
      this.view.disableStartButton();
    } else {
      this.view.enableStartButton();
    }
  };

  /**
   * Creates a card element based on the provided data and returns it.
   * @param {Object} data The data object containing details necessary to create a card.
   * @returns {HTMLElement} The created card element.
   */
  handleCreateCard = (data) => {
    const card = this.view.createCard(data);
    return card;
  };
}
