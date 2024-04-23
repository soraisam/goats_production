/**
 * Simplifies making fetch requests by encapsulating common settings and behaviors.
 */
class FetchWrapper {
  /**
   * Initializes a new instance of the FetchWrapper class.
   * @param {string} baseUrl - The base URL for all requests made by this instance.
   */
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      "Content-Type": "application/json",
    };
  }

  /**
   * Sets the CSRF token for all requests.
   * @param {string} csrfToken - The CSRF token to include in request headers.
   */
  setCsrfToken(csrfToken) {
    this.defaultHeaders["X-CSRFToken"] = csrfToken;
  }

  /**
   * Performs a fetch request with default settings and error handling.
   * @param {string} endpoint - The endpoint to append to the base URL.
   * @param {Object} [options={}] - Additional options for the fetch request.
   * @returns {Promise<Object>} - A promise resolving to the response data.
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;

    // Merge provided headers with defaults.
    options.headers = { ...this.defaultHeaders, ...options.headers };

    try {
      const response = await fetch(url, { ...options, credentials: "same-origin" });

      if (!response.ok) {
        throw response;
      }

      const data = await response.json();

      return data;
    } catch (error) {
      console.error("Fetch operation failed:", error);
      throw error;
    }
  }

  /**
   * Performs a GET request.
   * @param {string} endpoint - The endpoint for the GET request.
   * @param {Object} [options={}] - Additional options for the GET request.
   * @returns {Promise<Object>} - A promise resolving to the response data.
   */
  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  }

  /**
   * Performs a POST request.
   * @param {string} endpoint - The endpoint for the POST request.
   * @param {Object} body - The body data to send with the POST request.
   * @param {Object} [options={}] - Additional options for the POST request.
   * @returns {Promise<Object>} - A promise resolving to the response data.
   */
  post(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  /**
   * Performs a PUT request.
   * @param {string} endpoint - The endpoint for the PUT request.
   * @param {Object} body - The body data to send with the PUT request.
   * @param {Object} [options={}] - Additional options for the PUT request.
   * @returns {Promise<Object>} - A promise resolving to the response data.
   */
  put(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body),
    });
  }

  /**
   * Performs a DELETE request.
   * @param {string} endpoint - The endpoint for the DELETE request.
   * @param {Object} [options={}] - Additional options for the DELETE request.
   * @returns {Promise<Object>} - A promise resolving to the response data.
   */
  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  }

  /**
   * Performs a PATCH request.
   * @param {string} endpoint - The endpoint for the PATCH request.
   * @param {Object} body - The body data to send with the PATCH request.
   * @param {Object} [options={}] - Additional options for the PATCH request.
   * @returns {Promise<Object>} - A promise resolving to the response data.
   */
  patch(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(body),
    });
  }
}
