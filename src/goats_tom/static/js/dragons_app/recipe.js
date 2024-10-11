const OBSERVATION_TYPE_2_DISPLAY = {
  bias: "Bias reduction",
  flat: "Flat reduction",
  dark: "Dark reduction",
  arc: "Arc reduction",
  pinhole: "Pinhole reduction",
  ronchi: "Ronchi reduction",
  fringe: "Fringe reduction",
  bpm: "BPM reduction",
  standard: "Standard reduction",
  object: "Science reduction",
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
    this.reduce = null;
    this.functionDefinition = null;
    this.uparms = null;
  }

  /**
   * Fetches a specific recipe by its ID.
   * @param {number} recipeId The ID of the recipe to fetch.
   * @returns {Promise<Object>} A promise that resolves to the recipe object.
   * @throws {Error} If the API request fails, an error is logged to the console.
   * @async
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
   * @throws {Error} If the API request fails, an error is logged to the console.
   * @async
   */
  async startReduce(recipe, fileIds) {
    const data = { recipe_id: recipe, file_ids: fileIds };
    try {
      const response = await this.api.post(`${this.reduceUrl}`, data);
      this.reduce = response;
      return response;
    } catch (error) {
      console.error("Error starting reduce:", error);
    }
  }

  /**
   * Stops the reduction process.
   * @param {number} reduce The ID of the reduction to be stopped.
   * @returns {Promise<Object>} A promise that resolves to the response from the server.
   * @throws {Error} If the API request fails, an error is logged to the console.
   * @async
   */
  async stopReduce(reduce) {
    const data = { status: "canceled" };
    try {
      const response = await this.api.patch(`${this.reduceUrl}${reduce}/`, data);
      this.reduce = response;
      return response;
    } catch (error) {
      console.error("Error stopping reduce:", error);
    }
  }

  /**
   * Asynchronously fetches help documentation for a specified recipe.
   * @param {string} recipeId The ID of the recipe for which help documentation is being requested.
   * @returns {Promise<Object>} A promise that resolves with the help documentation for the
   * specified recipe.
   * @throws {Error} If the API request fails, an error is logged to the console.
   * @async
   */
  async fetchHelp(recipeId) {
    try {
      const response = await this.api.get(
        `${this.recipesUrl}${recipeId}/?include=help`
      );
      this.recipe = response;
      return response;
    } catch (error) {
      console.error("Error stopping recipe:", error);
    }
  }

  /**
   * Asynchronously updates the function definition of a recipe by sending a PATCH request.
   * @param {number} recipeId The unique identifier of the recipe.
   * @param {string|null} functionDefinition The new function definition to update, or null to
   * reset.
   * @returns {Promise<Object|null>} The updated recipe object if successful, or null if an error
   * occurs.
   */
  async updateFunctionDefinitionAndUparms(
    recipeId,
    functionDefinition = null,
    uparms = null
  ) {
    const data = { function_definition: functionDefinition, uparms: uparms };
    try {
      const response = await this.api.patch(`${this.recipesUrl}${recipeId}/`, data);
      this.functionDefinition = response;
      this.uparms = response;
      return response;
    } catch (error) {
      console.error("Error updating function definition:", error);
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
        logAccordion: "Log",
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
    this.progress = null;
    this.card = null;
    this.cardHeader = null;
    this.reduce = null;
    this.stopButton = null;
    this.startButton = null;
    this.editToggleButton = null;
    this.resetButton = null;
    this.helpButton = null;
    this.isEditMode = false;
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
   * Binds the handler for updating a function definition.
   * @param {Function} handler The handler function to invoke.
   */
  bindUpdateFunctionDefinitionAndUparms(handler) {
    this.onUpdateFunctionDefinitionAndUparms = handler;
  }

  /**
   * Binds the handler for resetting a function definition.
   * @param {Function} handler The handler function to invoke.
   */
  bindResetFunctionDefinitionAndUparms(handler) {
    this.onResetFunctionDefinitionAndUparms = handler;
  }

  /**
   * Binds the handler for showing help for a recipe.
   * @param {Function} handler The handler function to invoke.
   */
  bindShowHelp(handler) {
    this.onShowHelp = handler;
  }

  /**
   * Initializes event listeners on the card header. Listeners are set up to handle
   * start and stop reduce actions based on data attributes of the event target.
   * @private
   */
  _initLocalListeners() {
    this.card.addEventListener("click", (event) => {
      if (event.target.dataset.action) {
        const action = event.target.dataset.action;
        switch (action) {
          case "startReduce":
            // On start, pass in the recipe to link to.
            this.onStartReduce(
              event.target.dataset.recipeId,
              event.target.dataset.observationType
            );
            break;
          case "stopReduce":
            // On stop, need to specify what specific reduce to stop.
            this.onStopReduce(event.target.dataset.reduceId);
            break;
          case "editRecipe":
            this.onUpdateFunctionDefinitionAndUparms(event.target.dataset.recipeId);
            break;
          case "helpRecipe":
            this.onShowHelp(event.target.dataset.recipeId);
            break;
          case "resetRecipe":
            this.onResetFunctionDefinitionAndUparms(event.target.dataset.recipeId);
            break;
          default:
            console.log("No action defined for this button");
        }
      }
    });
  }
  /**
   * Retrieves the display name for a given recipe file type.
   * @param {string} recipeObservationType The file type of the recipe.
   * @returns {string} The user-friendly name corresponding to the recipe file type.
   */
  getDisplayName(recipeObservationType) {
    return OBSERVATION_TYPE_2_DISPLAY[recipeObservationType] || `Name Not Found: ${recipeObservationType}`;
  }

  /**
   * Creates a card element for a recipe.
   * @param {Object} recipe The recipe object to create a card for.
   * @returns {HTMLElement} The created card element with populated recipe data.
   */
  createCard(recipe) {
    this.recipe = recipe;

    // Build and append the header.
    const card = Utils.createElement("div");
    this.cardHeader = this.createCardHeader();
    card.appendChild(this.cardHeader);

    // Build and append the body.
    const cardBody = this.createCardBody();
    card.append(cardBody);

    // Build and append first footer (Modify Recipe).
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
    this.progress = new Progress(cardBody);
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
    p.textContent = this.getDisplayName(this.recipe.observation_type);
    col1.appendChild(p);

    // Create content for column 2
    const startButton = Utils.createElement("button", ["btn", "btn-success", "me-1"]);
    const stopButton = Utils.createElement("button", ["btn", "btn-danger"]);
    startButton.dataset.recipeId = this.recipe.id;
    startButton.dataset.observationType = this.recipe.object_name
      ? `${this.recipe.observation_type} | ${this.recipe.object_name}`
      : this.recipe.observation_type;
    startButton.dataset.action = "startReduce";
    startButton.textContent = "Start";
    this.startButton = startButton;
    stopButton.dataset.reduceId = null;
    stopButton.textContent = "Stop";
    stopButton.dataset.action = "stopReduce";
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
    ]);
    accordionButton.setAttribute("type", "button");
    accordionButton.setAttribute("data-toggle", "collapse");
    accordionButton.setAttribute("data-target", `#${collapseId}`);
    accordionButton.setAttribute("aria-expanded", "true");
    accordionButton.setAttribute("aria-controls", collapseId);
    accordionButton.textContent = this.accordionSetups.buttons[name];
    accordionHeader.appendChild(accordionButton);
    accordionItem.appendChild(accordionHeader);

    // Create the collaspible body section that will contain recipe.
    const collapse = Utils.createElement("div", ["accordion-collapse", "collapse", "show"]);
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
    this.editor.setValue(this.recipe.active_function_definition, -1);
    this.editor.session.setMode("ace/mode/python");

    this.editor.container.style.height = "100%";
    this.editor.container.style.width = "100%";
    this.editor.container.style.minHeight = "300px";
    this.editor.container.classList.add("editor-disabled");
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
    editToggleButton.dataset.recipeId = this.recipe.id;
    editToggleButton.dataset.action = "editRecipe";
    this.editToggleButton = editToggleButton;

    const resetButton = Utils.createElement("button", ["btn", "btn-secondary"]);
    resetButton.textContent = "Reset";
    resetButton.dataset.recipeId = this.recipe.id;
    resetButton.dataset.action = "resetRecipe";
    this.resetButton = resetButton;

    const helpButton = Utils.createElement("button", ["btn", "btn-link"]);
    helpButton.textContent = "Help";
    helpButton.dataset.recipeId = this.recipe.id;
    helpButton.dataset.action = "helpRecipe";
    helpButton.setAttribute("data-bs-toggle", "offcanvas");
    helpButton.setAttribute("data-bs-target", `#helpOffcanvas`);
    this.helpButton = helpButton;

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
      "ps-2",
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
    const uparmsInput = this.createUparms();
    const editor = this.createEditor();
    const editorButtons = this.createEditorButtons();

    accordionBody.append(uparmsInput, editor, editorButtons);
  }

  /**
   * Creates an input element for modifying 'uparms' parameters.
   * @returns {HTMLElement} The input element with associated label for 'uparms' parameters.
   */
  createUparms() {
    // Create a container.
    const div = Utils.createElement("div", "mb-3");
    const row = Utils.createElement("div", ["row", "g-3"]);
    const labelCol = Utils.createElement("div", ["col-sm-3"]);
    const inputCol = Utils.createElement("div", ["col-sm-9"]);

    // Create a label element.
    const uparmsId = `uparms-${this.recipe.id}`;
    const label = Utils.createElement("label", ["col-form-label"]);
    label.textContent = "Set Uparms";
    label.htmlFor = uparmsId;

    // Create an input element.
    const input = Utils.createElement("input", ["form-control"]);
    input.type = "text";
    input.id = uparmsId;
    input.placeholder =
      "[('stackFrames:memory', None), ('darkCorrect:dark', 'blah_dark.fits')]";
    input.value = this.recipe.uparms;
    input.disabled = true;
    this.uparms = input;

    // Append the label and input to the container.
    inputCol.appendChild(input);
    labelCol.appendChild(label);
    row.append(labelCol, inputCol);
    div.appendChild(row);

    return div;
  }

  /**
   * Appends a log viewing component to the provided accordion body.
   * @param {HTMLElement} accordionBody The accordion section where the log viewer will be appended.
   */
  createLogAccordionItem(accordionBody) {
    const logger = this.createLogger();
    accordionBody.appendChild(logger);
  }

  /**
   * Enables edit mode for the recipe editor.
   */
  enableEditMode() {
    this.editor.setReadOnly(false);
    this.editToggleButton.textContent = "Save";
    this.isEditMode = true;
    this.editor.container.classList.remove("editor-disabled");
    this.uparms.disabled = false;
  }

  /**
   * Saves changes and exits edit mode for the recipe editor.
   */
  saveRecipeChanges() {
    this.editor.setReadOnly(true);
    this.editToggleButton.textContent = "Edit";
    this.isEditMode = false;
    this.editor.container.classList.add("editor-disabled");
    this.uparms.disabled = true;
  }

  /**
   * Sets the text of the editor.
   * @param {string} text The text to set in the editor.
   */
  setEditorText(text) {
    this.editor.setValue(text, -1);
  }

  setUparms(text) {
    this.uparms.value = text;
  }

  getUparms() {
    return this.uparms.value;
  }

  /**
   * Retrieves the current text from the editor.
   * @returns {string} The current text in the editor.
   */
  getFunctionDefinition() {
    return this.editor.getValue();
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

    this.view.bindUpdateFunctionDefinitionAndUparms(
      this.handleUpdateFunctionDefinitionAndUparms
    );

    this.view.bindResetFunctionDefinitionAndUparms(
      this.handleResetFunctionDefinitionAndUparms
    );

    this.view.bindShowHelp(this.handleShowHelp);
  }

  /**
   * Resets the function definition for the specified recipe and updates the editor.
   * @param {number} recipeId The ID of the recipe to reset.
   */
  handleResetFunctionDefinitionAndUparms = async (recipeId) => {
    // Pass nothing to reset.
    const recipe = await this.model.updateFunctionDefinitionAndUparms(recipeId);
    // Update the editor with the new value.
    this.view.setEditorText(recipe.active_function_definition);
    this.view.setUparms(recipe.uparms);
  };

  /**
   * Handles fetching help information for primitives and updates display.
   * @param {number} recipeId The ID of the recipe to fetch help for.
   */
  handleShowHelp = async (recipeId) => {
    // Clear and show loading bar since it is not hidden.
    window.helpOffcanvas.clearTitleAndContent();
    window.helpOffcanvas.isLoading();

    // Pass in the recipe to get the help for it.
    const recipe = await this.model.fetchHelp(recipeId);
    window.helpOffcanvas.updateAndShowPrimitivesDocumentation(recipe);
  };

  /**
   * Handles the update of a function definition. It either enables edit mode or saves changes
   * depending on the mode.
   * @param {number} recipeId The ID of the recipe to update.
   */
  handleUpdateFunctionDefinitionAndUparms = async (recipeId) => {
    if (this.view.isEditMode) {
      this.view.saveRecipeChanges();
      // Update the recipe.
      const functionDefinition = this.view.getFunctionDefinition();
      const uparms = this.view.getUparms();
      const recipe = await this.model.updateFunctionDefinitionAndUparms(
        recipeId,
        functionDefinition,
        uparms
      );
      this.view.setEditorText(recipe.active_function_definition);
      this.view.setUparms(recipe.uparms);
    } else {
      this.view.enableEditMode();
    }
  };

  /**
   * Initiates the reduction process for a given recipe ID.
   * @param {number} recipeId The ID of the recipe to start reducing.
   * @param {string} observationType The file type identifier.
   * @async
   */
  handleStartReduce = async (recipeId, observationType) => {
    // Clear logger before starting.
    this.view.logger.clear();
    // Get the file IDs to run on.
    const tbody = document.getElementById(`tbody-${observationType}`);
    const fileIds = Array.from(
      tbody.querySelectorAll("input[type='checkbox']:checked")
    ).map((input) => input.dataset.filePk);
    const reduce = await this.model.startReduce(recipeId, fileIds);
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
   * @param {string} message The log message to add.
   */
  handleLogMessage = (message) => {
    this.view.logger.log(message);
  };

  /**
   * Updates the progress bar and stop/start buttons based on the status provided in the data.
   * @param {Object} data The data object containing the status to update with.
   */
  handleUpdateReduce = (data) => {
    this.view.progress.update(data.status);
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
