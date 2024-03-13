const createAndShowToast = (notification) => {
  const toastContainer = document.getElementById("toastContainer");
  const toastElement = document.createElement("div");

  // Style the toast.
  toastElement.classList.add(
    "toast",
    "border-start",
    `border-${notification.color}`,
    "border-top-0",
    "border-bottom-0",
    "border-end-0",
    "border-3"
  );
  toastElement.setAttribute("role", "alert");
  toastElement.setAttribute("aria-live", "assertive");
  toastElement.setAttribute("aria-atomic", "true");

  const toastHeader = document.createElement("div");
  toastHeader.classList.add("toast-header");

  // Create header icon.
  const toastHeaderIcon = document.createElement("i");
  toastHeaderIcon.classList.add(
    "fa-solid",
    getIconClass(notification.color),
    "pe-2",
    `text-${notification.color}`
  );

  toastHeader.appendChild(toastHeaderIcon);

  // Create header text.
  const toastHeaderStrong = document.createElement("strong");
  toastHeaderStrong.classList.add("me-auto");
  toastHeaderStrong.textContent = notification.label;

  toastHeader.appendChild(toastHeaderStrong);

  // Create close button.
  const toastHeaderButton = document.createElement("button");
  toastHeaderButton.classList.add("btn-close");
  toastHeaderButton.setAttribute("data-dismiss", "toast");
  toastHeaderButton.setAttribute("aria-label", "Close");

  toastHeader.appendChild(toastHeaderButton);

  // Work on toast body.
  const toastBody = document.createElement("div");
  toastBody.classList.add("toast-body");
  const toastBodyText = document.createElement("p");
  toastBodyText.classList.add("mb-0");
  toastBodyText.textContent = notification.message;

  toastBody.appendChild(toastBodyText);

  toastElement.appendChild(toastHeader);
  toastElement.appendChild(toastBody);

  toastContainer.appendChild(toastElement);

  const toast = new bootstrap.Toast(toastElement, {
    autohide: true,
    delay: 5000, // In milliseconds.
  });

  toast.show();
};

const getIconClass = (color) => {
  switch (color) {
    case "warning":
      return "fa-triangle-exclamation";
    case "danger":
      return "fa-circle-xmark";
    case "info":
      return "fa-comment";
    case "success":
      return "fa-circle-check";
    default:
      return "fa-circle-info";
  }
};

export { createAndShowToast };
