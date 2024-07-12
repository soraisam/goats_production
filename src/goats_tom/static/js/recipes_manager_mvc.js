/**
 * Represents a model for managing recipes and reductions in the DRAGONS system.
 */
class RecipeManagerModel {
  /**
   * Constructor for the RecipeManagerModel class.
   * @param {Object} api The API service used for fetching recipes data.
   */
  constructor(api) {
    this.api = api;
    this.recipes = [];
    this.recipesUrl = "dragonsrecipes/";
    this.reducesUrl = "dragonsreduce/";
    this.reduces = [];
  }

  /**
   * Fetches recipes associated with a specific DRAGONS run.
   * @param {string} runId The identifier for the DRAGONS run to fetch recipes for.
   * @returns {Promise<Object[]>} A promise that resolves to an array of recipe objects.
   */
  async fetchRecipes(runId) {
    try {
      const response = await this.api.get(`${this.recipesUrl}?dragons_run=${runId}`);
      this.recipes = response.results;
      return this.recipes;
    } catch (error) {
      console.error("Error fetching recipes:", error);
    }
  }

  /**
   * Fetches the reduces data for a given run.
   * @param {number} run The ID of the run to fetch reduces for.
   * @param {boolean} [notFinished=false] Whether to fetch only not finished reduces.
   * @returns {Promise<Array<Object>>} A promise that resolves to an array of reduces data.
   * @throws {Error} Will log an error message if the request fails.
   */
  async fetchReduces(run, notFinished = False) {
    try {
      const response = await this.api.get(
        `${this.reducesUrl}?run=${run}&not_finished=${notFinished}`
      );
      this.reduces = response.results;
      return this.reduces;
    } catch (error) {
      console.error("Error fetching reduces:", error);
    }
  }
}

/**
 * Manages the user interface for recipe management in the DRAGONS system.
 */
class RecipeManagerView {
  /**
   * Constructor for the RecipeManagerView class.
   */
  constructor() {
    this.container = document.getElementById("recipesContainer");
    this.contentContainer = null;
    this.navTabs = null;
  }
  /**
   * Binds a handler for the tab switching action.
   * @param {Function} handler Function to call when a tab is switched.
   */
  bindSwitchTab(handler) {
    this.onSwitchTab = handler;
  }

  /**
   * Clears all content from the recipes container and resets references.
   */
  clear() {
    this.container.innerHTML = "";
    this.contentContainer = null;
    this.navTabs = null;
  }

  /**
   * Initializes event listeners for the navigation tabs. Uses event delegation to handle tab
   * switching.
   */
  _initLocalListeners() {
    this.navTabs.addEventListener("click", (event) => {
      if (event.target.dataset.action) {
        const action = event.target.dataset.action;
        switch (action) {
          case "switchTab":
            this.onSwitchTab(event.target.dataset.fileType);
            break;
          default:
            break;
        }
      }
    });
  }

  /**
   * Constructs and appends a card element to the main container, which includes navigation tabs
   * and content.
   * @param {Object[]} recipesAndContent Array of objects containing recipe data and associated DOM
   * content.
   */
  createCard(recipesAndContent) {
    // Create card to hold the recipes.
    const card = Utils.createElement("div", "card");
    const cardHeader = Utils.createElement("div", "card-header");

    // Create navigation to switch file type.
    const navTabs = Utils.createElement("ul", ["nav", "nav-tabs", "card-header-tabs"]);
    this.navTabs = navTabs;
    const contentContainer = Utils.createElement("div");
    this.contentContainer = contentContainer;

    // Iterate through and build the content. Hiding everything except the first.
    recipesAndContent.forEach(({ recipe, content }, index) => {
      const tab = Utils.createElement("li", "nav-item");
      const tabLink = Utils.createElement("a", "nav-link");
      tabLink.href = "#";
      tabLink.textContent = Utils.formatDisplayText(recipe.file_type);
      tabLink.dataset.fileType = recipe.file_type;
      tabLink.dataset.action = "switchTab";

      if (index === 0) {
        tabLink.classList.add("active");
        content.classList.add("d-block");
      } else {
        content.classList.add("d-none");
      }

      content.dataset.fileType = recipe.file_type;
      contentContainer.appendChild(content);

      tab.appendChild(tabLink);
      navTabs.appendChild(tab);
    });

    cardHeader.appendChild(navTabs);
    card.append(cardHeader, contentContainer);
    this.container.appendChild(card);

    // Initialize the event listeners.
    this._initLocalListeners();
  }

  /**
   * Toggles the visibility of content based on the specified file type.
   * @private
   * @param {string} fileType The file type whose content needs to be toggled.
   */
  _toggleContentVisibility(fileType) {
    Array.from(this.contentContainer.children).forEach((content) => {
      if (content.dataset.fileType === fileType) {
        content.classList.remove("d-none");
        content.classList.add("d-block");
      } else {
        content.classList.remove("d-block");
        content.classList.add("d-none");
      }
    });
  }

  /**
   * Activates the tab corresponding to the given file type and toggles the visibility of the associated content.
   * @param {string} fileType The file type to activate.
   */
  activateAndToggleTab(fileType) {
    this._activateTab(fileType);
    this._toggleContentVisibility(fileType);
  }

  /**
   * Activates the tab that matches the specified file type.
   * @private
   * @param {string} fileType The file type of the tab to activate.
   */
  _activateTab(fileType) {
    Array.from(this.navTabs.querySelectorAll(".nav-link")).forEach((tab) => {
      // Remove the 'active' class from all tabs.
      tab.classList.remove("active");
      // Add 'active' to the tab that matches the file type.
      if (tab.dataset.fileType === fileType) {
        tab.classList.add("active");
      }
    });
  }
}

/**
 * Represents the controller for managing recipes in the DRAGONS system.
 */
class RecipeManagerController {
  /**
   * Constructor for the RecipeManagerController class.
   * @param {RecipeManagerModel} model The model instance.
   * @param {RecipeManagerView} view The view instance.
   */
  constructor(model, view) {
    this.model = model;
    this.view = view;
    this.recipes = {};
    this.ws = this._setupWebSocket();

    this.view.bindSwitchTab(this.handleSwitchTab);
  }

  /**
   * Returns the recipe controller for a given recipe ID.
   * @param {number} recipeId The ID of the recipe.
   * @returns {RecipeController|null} The recipe controller, or null if not found.
   */
  getRecipeControllerById(recipeId) {
    return this.recipes[recipeId] || null;
  }

  /**
   * Handles the action of switching tabs in the user interface based on the file type.
   * @param {string} fileType The file type identifier used to determine which tab to activate
   * and which content to display.
   */
  handleSwitchTab = (fileType) => {
    this.view.activateAndToggleTab(fileType);
  };

  /**
   * Sets up the WebSocket connection for receiving log updates.
   * @returns {WebSocket} The WebSocket instance.
   * @private
   */
  _setupWebSocket() {
    const dragonsWebSocket = new WebSocket("ws://localhost:8000/ws/dragons/");

    dragonsWebSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.update === "log") {
        const recipeController = this.getRecipeControllerById(data.recipe_id);
        if (recipeController) {
          recipeController.handleLogMessage(data.message);
        }
      }
      if (data.update === "recipe") {
        const recipeController = this.getRecipeControllerById(data.recipe_id);
        if (recipeController) {
          recipeController.handleUpdateReduce(data);
        }
      }
    };

    dragonsWebSocket.onopen = () => {
      console.log("DRAGONS WebSocket connection established");
    };

    dragonsWebSocket.onclose = (event) => {
      console.log("DRAGONS WebSocket connection closed", event);
    };

    dragonsWebSocket.onerror = (error) => {
      console.log("DRAGONS WebSocket error", error);
    };

    return dragonsWebSocket;
  }

  /**
   * Updates the recipes and content for a specific DRAGONS run.
   * @param {string} runId The ID of the run to fetch recipes for.
   */
  updateRecipesCard = async (runId) => {
    this.view.clear();
    const recipes = await this.model.fetchRecipes(runId);
    const recipesAndContent = [];

    // Create the recipe content.
    recipes.forEach((recipe) => {
      if (recipe.file_type !== "other") {
        // Create MVC per recipe.
        let recipeModel = new RecipeModel(this.model.api);
        let recipeView = new RecipeView();
        let recipeController = new RecipeController(recipeModel, recipeView);

        // Store the recipe controller for easy manipulation later.
        this.recipes[recipe.id] = recipeController;

        let content = recipeController.handleCreateCard(recipe);
        // Combine recipe data and content for passing to the view.
        recipesAndContent.push({ recipe: recipe, content: content });
      }
    });
    // Have list of recipe content, update UI.
    this.view.createCard(recipesAndContent);
  };

  /**
   * Updates the reduces progress for a given run.
   * @param {number} run The ID of the run to update reduces progress for.
   * @returns {Promise<void>} A promise that resolves when the progress update is complete.
   */
  updateReducesProgress = async (run) => {
    const reducesData = await this.model.fetchReduces(run, true);

    // Iterate over running reductions.
    reducesData.forEach((reduce) => {
      const recipeController = this.getRecipeControllerById(reduce.recipe);
      if (recipeController) {
        // Update the recipe reduce progress, it will only be not finished.
        recipeController.handleUpdateReduce(reduce);
      }
    });
  };
}
