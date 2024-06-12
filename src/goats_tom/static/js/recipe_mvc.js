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
    this.editor = null;
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
      const response = await this.api.get(`${recipesUrl}/${recipeId}/`);
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
    this.editor = null;
    this.reduce = null;
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
      if (event.target.dataset.action === "startReduce") {
        // On start, pass in the recipe to link to.
        this.onStartReduce(event.target.dataset.recipeId);
      } else if (event.target.dataset.action === "stopReduce") {
        // On stop, need to specify what specific reduce to stop.
        this.onStopReduce(event.target.dataset.recipeId);
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
   * Creates the card body for a recipe.
   * @returns {HTMLElement} The card body.
   */
  createCardBody() {
    const cardBody = Utils.createElement("div", "card-body");
    const recipeAccordion = this.createAccordion("recipeAccordion");
    cardBody.appendChild(recipeAccordion);

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
    startButton.id = `startRecipe-${this.recipe.id}`;
    startButton.dataset.recipeId = this.recipe.id;
    startButton.setAttribute("data-action", "startReduce");
    startButton.textContent = "Start";
    stopButton.id = `stopButton-${this.recipe.id}`;
    stopButton.setAttribute("data-recipeId", this.recipe.id);
    stopButton.textContent = "Stop";
    stopButton.setAttribute("data-action", "stopReduce");
    col2.append(startButton, stopButton);

    // Build the layout.
    row.append(col1, col2);

    cardHeader.appendChild(row);
    return cardHeader;
  }

  /**
   * Creates the first footer for the recipe, showing the progress bar.
   * @return {HTMLElement} The footer.
   */
  createCardFooter1() {
    // Create footer for progress updates and logger.
    const cardFooter = Utils.createElement("div", "card-footer");
    const row = Utils.createElement("div", ["row", "g-3"]);
    const col = Utils.createElement("div", "col-12");
    const progressBar = this.createProgressBar();
    this.progressBar = progressBar;
    this.updateProgressBar(0);

    col.appendChild(progressBar);
    row.append(col);
    cardFooter.appendChild(row);

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
   * Creates a progress bar for visualizing task completion or status.
   * @returns {HTMLElement} The div containing the progress bar.
   */
  createProgressBar() {
    const progressBarDiv = Utils.createElement("div", "progress");
    progressBarDiv.setAttribute("role", "progressbar");
    progressBarDiv.setAttribute("aria-label", "Recipe progress");
    progressBarDiv.setAttribute("aria-valuemin", "0");
    progressBarDiv.setAttribute("aria-valuemax", "100");

    const progressBar = Utils.createElement("div", "progress-bar");
    progressBarDiv.appendChild(progressBar);

    return progressBarDiv;
  }

  /**
   * Updates the progress bar with a given width percentage.
   *
   * @param {number} width The new width percentage of the progress bar.
   */
  updateProgressBar(width) {
    // Ensure width is within bounds (0 to 100).
    const boundedWidth = Math.max(0, Math.min(width, 100));

    this.progressBar.setAttribute("aria-valuenow", boundedWidth);

    // Find the progress bar element within the parent div.
    const progressBar = this.progressBar.querySelector(".progress-bar");
    if (progressBar) {
      // Set the style.width, special handling if width is 0.
      progressBar.style.width = boundedWidth === 0 ? "0" : `${boundedWidth}%`;
    }
  }

  /**
   * Initializes a new logger instance and creates a container for it. This function
   * sets up a log container, attaches a unique identifier based on the recipe's ID,
   * and instantiates the Logger class with this container.
   * @returns {HTMLElement} The div element that serves as the container for the logger.
   */
  createLogger() {
    const div = Utils.createElement("div", ["log-container", "log-overflow", "ps-2", "py-2"]);
    div.id = `loggerRecipe-${this.recipe.id}`;
    this.logger = new Logger(div);

    return div;
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
    this.view.logger.clear()
    const reduce = await this.model.startReduce(recipeId);
    // TODO: Update the view.
  };

  /**
   * Handles the stop reduction process for a given reduce ID.
   * @param {number} reduceId The ID of the reduce operation to stop.
   * @async
   */
  handleStopReduce = async (reduceId) => {
    // TODO: After API is written to terminate a running recipe reduce.
    console.log("Not implemented.");
  };

  /**
   * Handles log messages and updates the logger.
   * @param {string} message - The log message to add.
   */
  handleLogMessage = (message) => {
    this.view.logger.log(message);
  };
}
