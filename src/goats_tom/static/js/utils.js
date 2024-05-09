class Utils {
  static capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
  }

  static isEmpty(obj) {
    return Object.keys(obj).length === 0 && obj.constructor === Object;
  }

  /**
   * Creates a new HTML element with optional class names.
   * @param {string} tag - The tag name of the element to create.
   * @param {string | string[]} classNames - The class name(s) to add to the element.
   * @returns {Element} The newly created element.
   */
  static createElement(tag, classNames) {
    const element = document.createElement(tag);
    if (classNames) {
      if (Array.isArray(classNames)) {
        element.classList.add(...classNames);
      } else {
        element.classList.add(classNames);
      }
    }
    return element;
  }
}
