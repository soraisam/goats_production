class Identifier {
  constructor(observationType, observationClass, objectName) {
    this.observationType = observationType;
    this.observationClass = observationClass;
    this.objectName = objectName;
    this.idPrefix = this.createIdPrefix(
      this.observationType,
      this.observationClass,
      this.objectName
    );
    this.displayText = this.createDisplayText(
      this.observationType,
      this.observationClass,
      this.objectName
    );
  }

  createIdPrefix(observationType, observationClass, objectName) {
    // Normalize each part to lowercase and replace spaces or special characters with underscores.
    const normalize = (str) =>
      str
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "_");

    // Create the ID by joining the normalized parts with double underscores.
    const id = `${normalize(observationType)}__${normalize(
      observationClass
    )}__${normalize(objectName)}__`;

    return id;
  }

  createDisplayText(observationType, observationClass, objectName) {
    return `${observationType} (${observationClass}) | ${objectName}`;
  }
}
