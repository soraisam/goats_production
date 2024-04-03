/**
 * Manages setup data and interactions with the API for DRAGONS runs.
 */
class SetupModel {
  constructor(api) {
    this.api = api;
    this.runs = [];
  }

  /**
   * Submits setup data to initialize a new DRAGONS run and updates runs.
   * @param {FormData} formData - Setup data from the form.
   */
  async formSubmit(formData) {
    const formDataObject = Object.fromEntries(formData);

    try {
      const response = await this.api.post(
        `${formDataObject.observation_record}/setup/`,
        formDataObject
      );
      this.runs = response.dragons_runs;

      // Notify of changes.
      this.onRunsChanged(this.runs);
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
}

/**
 * Manages the UI for DRAGONS run setup, handling form submission and dynamic updates.
 */
class SetupView {
  constructor() {
    // Initialize UI elements.
    this.card = document.getElementById("dragonsRunsCard");
    this.form = this.card.querySelector("#dragonsSetupForm");
    this.runsSelect = this.card.querySelector("#dragonsRunsSelect");
    this.newRunRadio = this.card.querySelector("#new-run");
    this.existingRunRadio = this.card.querySelector("#existing-run");

    // Set up event listeners for UI interactions.
    this._initLocalListeners();
  }

  /**
   * Populates the run selection dropdown with options based on available runs.
   * @param {Array} runs - DRAGONS run objects to display in the select dropdown.
   */
  displayRuns(runs) {
    // Reset the dropdown for new data.
    this.runsSelect.innerHTML = '<option value="" selected hidden>---</option>';
    runs.forEach((run) => {
      const option = new Option(run.run_id, run.id);
      this.runsSelect.add(option);
    });
  }

  /**
   * Resets the form to its default state and hides it if necessary.
   */
  resetForm() {
    this.form.reset();
    this.toggleFormVisibility(false);
    this.existingRunRadio.checked = true;
  }

  /**
   * Sets up event listeners for form submission and radio button changes.
   */
  _initLocalListeners() {
    this.newRunRadio.addEventListener("change", () => this.toggleFormVisibility(true));
    this.existingRunRadio.addEventListener("change", () =>
      this.toggleFormVisibility(false)
    );

    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(this.form);
      this.formSubmitHandler(formData);
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
}

/**
 * Coordinates interactions between the setup model and view.
 */
class SetupController {
  constructor(model, view) {
    this.model = model;
    this.view = view;

    // When the form is submitted, handle the data submission.
    this.view.bindFormSubmit(this.handleFormSubmit);

    // When the model's run data changes, update the view with the new runs
    this.model.bindRunsChanged(this.onRunsChanged);
  }

  /**
   * Handles the form submission, invoking the model to submit the form data.
   *
   * @param {FormData} formData The data from the setup form.
   */
  handleFormSubmit = async (formData) => {
    try {
      await this.model.formSubmit(formData);
      this.view.resetForm();
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
}
