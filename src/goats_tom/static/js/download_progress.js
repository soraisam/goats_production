/**
 * Updates the download link in the navbar to reflect the number of active downloads.
 *
 * This function modifies the text content of the download badge element based on
 * the number of active downloads. If there are active downloads, the badge is
 * made visible and updated with the count. If there are no active downloads,
 * the badge is hidden.
 *
 * @param {number} activeDownloads - The number of active downloads.
 */
const updateNavbarDownloadLink = (activeDownloads) => {
  // Get the download badge element from the DOM
  const downloadBadge = document.getElementById("downloadBadge");
  const noDownloadsMessage = document.getElementById("noDownloadsMessage");

  // Check if there are any active downloads
  if (activeDownloads > 0) {
    downloadBadge.textContent = activeDownloads;
    downloadBadge.classList.remove("d-none");
    noDownloadsMessage.classList.add("d-none");
  } else {
    // Hide the badge by adding "d-none" class
    downloadBadge.classList.add("d-none");
    noDownloadsMessage.classList.remove("d-none");
  }
};


/**
 * Updates the tasks banner with the provided tasks information.
 *
 * This function handles the dynamic creation, updating, and removal of task elements in the
 * download tasks banner. It iterates over the provided tasks, updating existing tasks or creating
 * new ones as necessary. It also removes any task elements that are no longer present in the tasks list.
 *
 * @param {Array<Object>} tasks - An array of task objects, each containing task_id, progress, and status.
 */
const updateDownloadTasksBanner = (tasks) => {
  const banner = document.getElementById("downloadTasksBanner");

  // Track the current task IDs from the tasks list
  const currentTaskIds = tasks.map(task => `task-${task.task_id}`);

  // Remove task divs that are no longer in the updated tasks list
  const taskDivs = banner.getElementsByClassName("task-progress");
  Array.from(taskDivs).forEach(div => {
    if (!currentTaskIds.includes(div.id)) {
      banner.removeChild(div);
    }
  });

  // Process each task in the tasks array
  tasks.forEach(task => {
    let taskDiv = document.getElementById(`task-${task.task_id}`);

    if (!taskDiv) {
      // If the task is new, create and add its elements to the banner
      taskDiv = createTaskElement(task);
      banner.appendChild(taskDiv);
    } else {
      // If the task already exists, update its progress and status
      updateTaskElement(task);
    }
  });

  // Update the navbar download link with the number of tasks
  updateNavbarDownloadLink(tasks.length);
};


/**
 * Creates a new task element for the banner.
 *
 * This function creates a new DOM element representing a task with its progress bar and
 * status information.
 *
 * @param {Object} task - An object containing information about the task (task_id, progress, status).
 * @returns {HTMLElement} The newly created task element.
 */
function createTaskElement(task) {
  // Create the main task div
  const taskDiv = document.createElement("div");
  taskDiv.id = `task-${task.task_id}`;
  taskDiv.className = "row task-progress align-items-center";

  // Create and append the task information div
  const taskInfoDiv = document.createElement("div");
  taskInfoDiv.className = "col-md-3";
  const taskInfo = document.createElement("p");
  taskInfo.id = `info-${task.task_id}`;
  taskInfo.classList.add("mt-3")
  taskInfo.textContent = `${task.task_id}`;
  taskInfoDiv.appendChild(taskInfo);
  taskDiv.appendChild(taskInfoDiv);

  // Create and append the progress bar
  const progressBarDivCol = createProgressBar(task);
  taskDiv.appendChild(progressBarDivCol);

  return taskDiv;
}


/**
 * Creates a progress bar element for a task.
 *
 * @param {Object} task - The task object with progress information.
 * @returns {HTMLElement} The progress bar element.
 */
function createProgressBar(task) {
  const progressBarDivCol = document.createElement("div");
  progressBarDivCol.className = "col-md-9";
  const progressBarDiv = document.createElement("div");
  progressBarDiv.className = "progress";
  const progressBar = document.createElement("div");
  progressBar.classList.add("progress-bar", "progress-bar-striped", "progress-bar-animated");
  progressBar.id = `progress-${task.task_id}`;
  progressBar.setAttribute("role", "progressbar");
  progressBar.setAttribute("aria-valuenow", task.progress);
  progressBar.setAttribute("aria-valuemin", "0");
  progressBar.setAttribute("aria-valuemax", "100");
  progressBar.style.width = `${task.progress}%`;
  progressBar.textContent = `${task.progress}%`;

  progressBarDiv.appendChild(progressBar);
  progressBarDivCol.appendChild(progressBarDiv);

  return progressBarDivCol;
}


/**
 * Updates an existing task element with new progress and status.
 *
 * @param {Object} task - The task object with updated information.
 */
function updateTaskElement(task) {
  // Update the task information
  const taskInfo = document.getElementById(`info-${task.task_id}`);
  taskInfo.textContent = `${task.task_id}`;

  // Update the progress bar
  const progressBar = document.getElementById(`progress-${task.task_id}`);
  progressBar.style.width = `${task.progress}%`;
  progressBar.setAttribute("aria-valuenow", task.progress);
  progressBar.textContent = `${task.progress}%`;
}


/**
 * Asynchronously fetches ongoing tasks from the server.
 *
 * This function makes an HTTP GET request to the "/api/ongoing-tasks/" endpoint
 * to retrieve a list of ongoing tasks. If the request is successful, it updates
 * the tasks banner with the fetched data. It also sets a timeout to
 * repeatedly call itself every second, effectively polling the server for
 * updates on ongoing tasks.
 */
const fetchOngoingTasks = async () => {
  try {
    // Fetch ongoing tasks data from the server
    const response = await fetch("/api/ongoing-tasks/");

    // Check if the HTTP request was successful
    if (!response.ok) {
        // If not successful, throw an error with the status code
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Parse the JSON response to get tasks data
    const tasks = await response.json();
    updateDownloadTasksBanner(tasks);

    // Set a timeout to re-fetch the tasks every second
    setTimeout(fetchOngoingTasks, 1000);

  } catch (error) {
    // Log any errors to the console
    console.error("Error:", error);
  }
};


// Start the polling when the page loads
document.addEventListener("DOMContentLoaded", fetchOngoingTasks);
