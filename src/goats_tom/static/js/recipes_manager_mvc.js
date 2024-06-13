/**
 * Represents a model for managing recipes in the DRAGONS system.
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
}

/**
 * Represents the view for managing recipes in the DRAGONS system.
 */
class RecipeManagerView {
  /**
   * Constructor for the RecipeManagerView class.
   */
  constructor() {
    this.container = document.getElementById("recipesContainer");
  }

  /**
   * Clears the recipes container.
   */
  clear() {
    this.container.innerHTML = "";
  }

  /**
   * Adds recipe cards to the container.
   * @param {HTMLElement[]} cards The array of card elements to add.
   */
  addCards(cards) {
    cards.forEach((card) => {
      const col = Utils.createElement("div", ["col-xl-6", "col-12"]);
      col.appendChild(card);
      this.container.appendChild(col);
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
   * Updates the recipe cards for a specific DRAGONS run.
   * @param {string} runId The ID of the run to fetch recipes for.
   */
  updateRecipeCards = async (runId) => {
    this.view.clear();
    const recipesData = await this.model.fetchRecipes(runId);
    const recipeCards = [];

    // Create the recipe cards.
    recipesData.forEach((recipe) => {
      if (recipe.file_type !== "other") {
        // Create MVC per recipe.
        let recipeModel = new RecipeModel(this.model.api);
        let recipeView = new RecipeView();
        let recipeController = new RecipeController(recipeModel, recipeView);

        // Store the recipe controller for easy manipulation later.
        this.recipes[recipe.id] = recipeController;

        let recipeCard = recipeController.handleCreateCard(recipe);
        recipeCards.push(recipeCard);
      }
    });
    // Have list of recipe cards, update UI.
    this.view.addCards(recipeCards);
  };
}
