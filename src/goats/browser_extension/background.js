// Import the default settings.
import { DEFAULT_SETTINGS } from './defaults.js';

/**
 * An object representing the colors for badge background.
 * @type {Object}
 */
const COLORS = {
  YELLOW: [255, 255, 0, 255],
  GREEN: [0, 255, 0, 255],
  RED: [255, 0, 0, 255],
  WHITE: [255, 255, 255, 255],
  DEFAULT: [128, 128, 128, 255]
};

/**
 * The trusted hostname for checking the URL.
 * @type {string}
 */
const ANTARES_URL = "https://antares.noirlab.edu/loci";

/**
 * Resets the badge color and text based on the tab URL.
 *
 * @param {chrome.tabs.Tab} tab - The tab where the URL is checked.
 */
const resetBadgeColor = (tab) => {
  const isTrustedHost = tab.url.startsWith(ANTARES_URL);
  const badgeColor = isTrustedHost ? COLORS.WHITE : COLORS.DEFAULT;
  const badgeText = isTrustedHost ? "→" : "✗";

  chrome.action.setBadgeBackgroundColor({ color: badgeColor, tabId: tab.id });
  chrome.action.setBadgeText({ text: badgeText, tabId: tab.id });
};

/**
 * Listens for tab updates and resets badge color and text accordingly.
 *
 * @param {number} tabId - The ID of the tab that was updated.
 * @param {chrome.tabs.TabChangeInfo} changeInfo - Information about the tab
 * update.
 * @param {chrome.tabs.Tab} tab - The state of the tab that was updated.
 */
const onTabUpdated = (tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    resetBadgeColor(tab);
  }
};

// Add listener for tab updates
chrome.tabs.onUpdated.addListener(onTabUpdated);

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "options",
    title: "Options",
    contexts: ["browser_action"],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "options") {
    chrome.runtime.openOptionsPage();
  }
});

/**
 * The function listens for clicks on the Chrome browser extension's icon.
 * It then checks if the active tab's URL matches the specified conditions.
 * If conditions are met, it sends parsed data to a Django backend.
 *
 * @async
 * @param {Object} tab - Information about the active tab.
 */
chrome.action.onClicked.addListener(async (tab) => {
  // Parse the current URL of the active tab.
  const currentURL = new URL(tab.url);
  // Split the pathname to get individual elements.
  const pathnameArray = currentURL.pathname.split("/");
  // Initialize an empty object to hold the data to send.
  let dataToSend = {};

  // Check if the hostname and pathname match the specified conditions.
  if (currentURL.hostname === "antares.noirlab.edu" && pathnameArray[1] === "loci") {
    // If a query parameter exists in the URL.
    if (currentURL.searchParams.get("query")) {
      // Get the query parameter.
      const queryParam = currentURL.searchParams.get("query");

      try {
        // Decode and parse the query parameter into a JSON object.
        const decodedQuery = decodeURIComponent(queryParam);
        const parsedJSON = JSON.parse(decodedQuery);
        const transformedQuery = transformQuery(parsedJSON);
        // Add parsed query to the data to send, match ANTARES plugin.
        dataToSend.esquery = transformedQuery;
      } catch (error) {
        // Log errors related to decoding and parsing.
        console.error("Error while decoding and parsing the query parameter:", error);
      }
    }

    // If an object name exists in the URL.
    if (pathnameArray.length > 2) {
      const objectName = pathnameArray[2];
      // Add the object name to the data to send.
      dataToSend.locusid = objectName;
    }

    chrome.storage.local.get(["url", "port", "token"], async (items) => {
      try {
        if (chrome.runtime.lastError) {
          throw new Error(chrome.runtime.lastError);
        }

        const url = items.url || DEFAULT_SETTINGS.url;
        const port = items.port || DEFAULT_SETTINGS.port;
        const token = items.token || DEFAULT_SETTINGS.token;

        // Construct the URL using the retrieved items.
        const baseUrl = `http://${url}:${port}/receive_query/`;

        // Send data to app.
        const response = await fetch(baseUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Token ${token}`,
          },
          body: JSON.stringify(dataToSend),
        });

        // Check if the response status is in the 2xx success range.
        if (response.status >= 200 && response.status < 300) {
          chrome.action.setBadgeBackgroundColor({ color: COLORS.GREEN, tabId: tab.id });
          chrome.action.setBadgeText({ text: "✓", tabId: tab.id });
        } else {
          if (response.status === 401) {
            // Change badge to red and token icon.
            chrome.action.setBadgeBackgroundColor({ color: COLORS.RED, tabId: tab.id });
            chrome.action.setBadgeText({ text: "TKN", tabId: tab.id });
          }
          else if (response.status === 409) {
            // Change badge to yellow and duplicate icon.
            chrome.action.setBadgeBackgroundColor({ color: COLORS.YELLOW, tabId: tab.id });
            chrome.action.setBadgeText({ text: "DUP", tabId: tab.id });
          }
          else {
            // If the response status is not in the 2xx range, throw an error.
            throw new Error(`${response.statusText}`);
          }
        }
      } catch (error) {
        // Log any errors that occur during the operation.
        console.error("Error:", error);
        chrome.action.setBadgeBackgroundColor({ color: COLORS.RED, tabId: tab.id });
        chrome.action.setBadgeText({ text: "✗", tabId: tab.id });
      } finally {
        // Reset the badge color after a delay.
        setTimeout(() => resetBadgeColor(tab), 2000);
      }
    });
  }
});

/**
 * Transforms the query format from the URL into the specific query format
 * needed.
 *
 * This function receives a query object with a certain structure. It then
 * transforms this query object into a new structure that fits the desired
 * query format. Specifically, it extracts filters from the received object and
 * organizes them into a "must" array within a nested "bool" and "filter"
 * hierarchy.
 *
 * @param {Object} receivedQuery - The parsed JSON object from the URL.
 * @returns {Object} - The transformed query object in the desired format.
 */
const transformQuery = (receivedQuery) => {
  // Extract the "filters" array from the received query object.
  const { filters } = receivedQuery;

  // Map each filter object to a new object that fits the desired query format.
  const mustArray = filters.map(filter => {
    // Extract relevant properties from each filter object.
    const { type, field, value } = filter;

    // Return a new object where the keys and values are organized according to
    // the desired format.
    return {
      [type]: {
        [field]: value
      }
    };
  });

  // Build and return the complete query object in the desired format.
  return {
    query: {
      bool: {
        filter: {
          bool: {
            must: mustArray
          }
        }
      }
    }
  };
};
