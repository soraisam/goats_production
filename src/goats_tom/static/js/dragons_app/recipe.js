

const STATUS_2_PROGRESS_BAR_COLOR = {
  queued: "bg-primary bg-opacity-25",
  initializing: "bg-primary bg-opacity-50",
  error: "bg-danger",
  running: "bg-primary",
  done: "bg-success",
  canceled: "bg-warning",
};

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
   * Capitalizes the first letter of the given string.
   * @param {string} string The string to capitalize.
   * @return {string} The string with the first letter capitalized.
   */
  capitalizeFirstLetter(string) {
    return string[0].toUpperCase() + string.slice(1);
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
}
