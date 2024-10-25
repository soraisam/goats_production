class RecipeReductionsManagerModel {
  constructor(options) {
    this.options = options;
    this._currentRecipeId = null;
    this._runId = null;
  }

  get runId() {
    return this._runId;
  }

  set runId(value) {
    this._runId = value;
  }

  get currentRecipeId() {
    return this._currentRecipeId
  }

  set currentRecipeId(value) {
    this._currentRecipeId = value;
  }
}

class RecipeReductionsManagerTemplate {
  constructor(options) {
    this.options = options;
  }
}

class RecipeReductionsManagerView {
  constructor(template, options) {
    this.template = template;
    this.options = options;

    this.container = null;
    // Store all the recipe reductions.
    this.recipeReductions = new Map();
  }

  render(viewCmd, parameter) {
    switch (viewCmd) {
      case "create":
        this._create(parameter.parentElement, parameter.data);
        break;
      case "updateRecipe":
        this._updateRecipe(parameter.recipeId);
        break;
    }
  }

  _updateRecipe(recipeId) {
    // TODO: Improve this to cache what is already shown to prevent looping.
    // Iterate through all entries in the map
    this.recipeReductions.forEach((recipeReduction, id) => {
      if (id === recipeId) {
        recipeReduction.show();
      } else {
        recipeReduction.hide();
      }
    });
  }

  _create(parentElement, data) {
    // Loop through and create recipe reductions.
    data.results.forEach((recipe) => {
      // Use map for accessing.
      this.recipeReductions.set(
        String(recipe.id),
        new RecipeReduction(parentElement, recipe)
      );
    });
  }

  bindGlobalCallback(event, handler) {
    switch (event) {
      case "updateRecipe":
        document.addEventListener("updateRecipe", (e) => {
          const recipeId = e.detail.recipeId;
          handler({ recipeId });
        });
        break;
    }
  }
}

class RecipeReductionsManagerController {
  constructor(model, view, options) {
    this.model = model;
    this.view = view;
    this.options = options;
  }

  _bindGlobalCallbacks() {
    this.view.bindGlobalCallback("updateRecipe", (item) => {
      this._updateRecipe(item.recipeId);
    });
  }

  create(parentElement, runId, data) {
    this.model.runId = runId;
    this.view.render("create", { parentElement, data });
    this._setupWebSocket();
    this._bindGlobalCallbacks();
  }

  _updateRecipe(recipeId) {
    if (this.model.currentRecipeId !== recipeId) {
      console.log("updating because doesn't match");
      this.view.render("updateRecipe", { recipeId });
      this.model.currentRecipeId = recipeId;
    }
  }

  _setupWebSocket() {
    // TODO: Finish this.
    this.ws = new WebSocket("ws://localhost:8000/ws/dragons/");

    this.ws.onmessage = (event) => {
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

    this.ws.onopen = () => {
      console.log("DRAGONS WebSocket connection established");
    };

    this.ws.onclose = (event) => {
      console.log("DRAGONS WebSocket connection closed", event);
    };

    this.ws.onerror = (error) => {
      console.log("DRAGONS WebSocket error", error);
    };
  }
}

class RecipeReductionsManager {
  static #defaultOptions = {
    id: "RecipeReductionsManager",
  };

  constructor(parentElement, runId, data, options = {}) {
    this.options = {
      ...RecipeReductionsManager.#defaultOptions,
      ...options,
      api: window.api,
    };
    const model = new RecipeReductionsManagerModel(this.options);
    const template = new RecipeReductionsManagerTemplate(this.options);
    const view = new RecipeReductionsManagerView(template, this.options);
    this.controller = new RecipeReductionsManagerController(model, view, this.options);

    this._init(parentElement, runId, data);
  }

  _init(parentElement, runId, data) {
    this._create(parentElement, runId, data);
  }

  _create(parentElement, runId, data) {
    this.controller.create(parentElement, runId, data);
  }
}
