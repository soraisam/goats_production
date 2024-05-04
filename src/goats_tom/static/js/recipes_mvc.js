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
 * Represents a model for managing recipes in the DRAGONS system.
 */
class RecipesModel {
  /**
   * Constructor for the RecipesModel class.
   * @param {Object} api The API service used for fetching recipes data.
   */
  constructor(api) {
    this.api = api;
    this.recipe = null;
    this.editor = null;
    this.recipesUrl = "dragonsrecipes/";
  }

  /**
   * Fetches recipes associated with a specific DRAGONS run.
   * @param {string} dragonsRun The identifier for the DRAGONS run to fetch recipes for.
   * @returns {Promise<Object[]>} A promise that resolves to an array of recipe objects.
   */
  async fetchRecipes(dragonsRun) {
    try {
      const response = await this.api.get(
        `${this.recipesUrl}?dragons_run=${dragonsRun}`
      );
      this.recipes = response.results;
      return this.recipes;
    } catch (error) {
      console.error("Error fetching recipes:", error);
    }
  }
}

/**
 * Represents the view for recipes in the DRAGONS system.
 */
class RecipesView {
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
        logAccordion: ["log-overflow"],
      },
    };
    this.editor = null;
    this.recipe = null;
    this.logger = null;
    this.progressBar = null;
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
    const cardHeader = this.createCardHeader();
    card.appendChild(cardHeader);

    // Build and append the body.
    const cardBody = this.createCardBody();
    card.append(cardBody);

    // Build and append first footer (progress bar).
    const cardFooter1 = this.createCardFooter1();
    card.appendChild(cardFooter1);

    // Build and append second footer (log viewer).
    const cardFooter2 = this.createCardFooter2();
    card.appendChild(cardFooter2);

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
    startButton.setAttribute("recipeId", this.recipe.id);
    startButton.textContent = "Start";
    stopButton.id = `stopButton-${this.recipe.id}`;
    stopButton.setAttribute("recipeId", this.recipe.id);
    stopButton.textContent = "Stop";
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
   * @param {number} width - The new width percentage of the progress bar.
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
    const div = Utils.createElement("div", "log-container");
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

class RecipesController {
  /**
   * Constructor for the RecipesController class.
   * @param {RecipesModel} model The model handling the business logic and data retrieval.
   * @param {RecipesView} view The view handling the display and UI interactions.
   */
  constructor(model, view) {
    this.model = model;
    this.view = view;
  }

  /**
   * Fetches recipes for a specific DRAGONS run and processes them for display.
   * @param {string} dragonsRun The DRAGONS run identifier to fetch recipes for.
   * @returns {Promise<HTMLElement[]>} A promise that resolves to an array of card elements for each recipe.
   */
  handleFetchRecipes = async (dragonsRun) => {
    const recipes = await this.model.fetchRecipes(dragonsRun);
    // Update the view.
    const cards = [];
    recipes.forEach((recipe) => {
      if (recipe.file_type !== "other") {
        const card = this.view.createCard(recipe);
        cards.push(card);
      }
    });
    return cards;
  };
}
