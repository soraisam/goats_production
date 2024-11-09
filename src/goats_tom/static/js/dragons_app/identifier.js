/**
 * Represents an identifier for an observation.
 * This class encapsulates the identifier details and provides methods to generate formatted text and identifiers.
 *
 * @param {string} runId - The unique identifier for the run.
 * @param {string} observationType - The type of observation.
 * @param {string} observationClass - The class of the observation.
 * @param {string} objectName - The name of the object observed.
 * @class
 */
class Identifier {
  constructor(runId, observationType, observationClass, objectName) {
    this.runId = runId;
    this.observationType = observationType;
    this.observationClass = observationClass;
    this.objectName = objectName;
    this.idPrefix = this.createIdPrefix();
    this.displayText = this.createDisplayText();
    this.defaultFilterExpression = this.createDefaultFilterExpression();
  }

  /**
   * Creates a unique ID prefix based on the observation details.
   * Normalizes input strings to create a web-safe ID.
   * @returns {string} A unique identifier prefix.
   */
  createIdPrefix() {
    const normalize = (str) =>
      str
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "_");
    return `${normalize(this.observationType)}__${normalize(
      this.observationClass
    )}__${normalize(this.objectName)}__`;
  }

  /**
   * Creates a display text string for the identifier.
   * Combines observation type, class, and object name into a user-friendly string.
   * @returns {string} Formatted display text.
   */
  createDisplayText() {
    return `${this.observationType} (${this.observationClass}) | ${this.objectName}`;
  }

  /**
   * Generates a default filter expression for database queries based on observation details.
   * This method is used to facilitate database queries filtering by multiple attributes.
   * @returns {string} A default filter expression for database queries.
   */
  createDefaultFilterExpression() {
    return `(observation_type=="${this.observationType}" and observation_class=="${this.observationClass}" and object=="${this.objectName}")`;
  }
}
