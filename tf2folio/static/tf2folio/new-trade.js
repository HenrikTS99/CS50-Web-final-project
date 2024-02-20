// Variable Declarations
let saleButton;
let buyButton;
let saleForm;
let buyForm;
let itemRegisterForm;
let itemRegisterSection;
let tradeRegisterSection;
let tradeDisplaySection;
let selectedItemsContainer;
let receivedItemsContainer;
let transactionBox;
let itemsSoldDropdown;
let itemsBoughtDropdown;
let saleTransactionRadioButtons;
let purchaseTransactionRadioButtons;
let amountFields;
let currencyFields;
let boxSpan;
let currencyField;
let amountLabels;
let currencyLabels;

let selectedItems = new Set();
let transaction_type = "sale";
let isReceivedItemForm = false;

const TRANSACTION_METHODS = {
  PAYPAL: "paypal",
  SCM_FUNDS: "scm_funds",
  KEYS: "keys",
  ITEMS: "items",
};

const TRANSACTION_IMAGES = {
  [TRANSACTION_METHODS.KEYS]:
    "https://steamcdn-a.akamaihd.net/apps/440/icons/key.be0a5e2cda3a039132c35b67319829d785e50352.png",
  [TRANSACTION_METHODS.SCM_FUNDS]:
    "https://community.cloudflare.steamstatic.com/public/shared/images/responsive/share_steam_logo.png",
  [TRANSACTION_METHODS.PAYPAL]:
    "https://developer.valvesoftware.com/w/images/thumb/f/f9/Smallcredits.png/300px-Smallcredits.png",
};

// Function Declarations

// Add selected item to the selected items container in the trade preview
function addItemToSelectedItems(event, item_type) {
  const selectedItemId = event.target.value;

  // Check if the item is already selected
  if (selectedItems.has(selectedItemId)) {
    alert("Item already selected!");
    return;
  }
  selectedItems.add(selectedItemId);

  // Fetch the item's HTML and append it to the page
  fetchItemHTML(selectedItemId, item_type);
}

function fetchItemHTML(itemId, item_type) {
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  fetch(`/get_item_html/${itemId}`, {
    method: "POST",
    headers: { "X-CSRFToken": csrf },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Data sent sucsessfully", data);
      // Append the new item to the page
      appendItemToPage(data, item_type);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Append the selected item to the "Selected Items" container
function appendItemToPage(data, item_type) {
  let itemsContainer, selectedIndex;

  if (item_type == "bought" && transaction_type == "sale") {
    itemsContainer = receivedItemsContainer;
    selectedIndex = itemsBoughtDropdown.selectedIndex;
  } else {
    itemsContainer = selectedItemsContainer;
    selectedIndex = itemsSoldDropdown.selectedIndex;
  }
  itemsContainer.insertAdjacentHTML("beforeend", data.item_html);
  removeSelectedItemFromDropdowns(selectedIndex);
}

function removeSelectedItemFromDropdowns(selectedIndex) {
  itemsSoldDropdown.remove(selectedIndex);
  itemsBoughtDropdown.remove(selectedIndex);
}

// Get and remove item from the trade preview
function getAndRemoveTargetItem(event) {
  let itemElement = event.target.closest(".item-box");
  removeItemFromPreview(itemElement);
}

function clearReceivedItems() {
  Array.from(receivedItemsContainer.children).forEach((item) => {
    removeItemFromPreview(item);
  });
}

function removeItemFromPreview(itemElement) {
  // Don't remove the transaction preview
  if (itemElement === transactionBox) {
    return;
  }
  let itemId = itemElement.getAttribute("data-item-id");
  selectedItems.delete(itemId);
  itemElement.remove();
  addItemToDropdowns(itemElement, itemId);
}

// After removing an item from the trade preview, add it back to the dropdown selections
function addItemToDropdowns(itemElement, itemId) {
  let itemSelectionOption = document.createElement("option");
  itemSelectionOption.value = itemId;
  itemSelectionOption.text = itemElement.querySelector("span").textContent;
  itemsSoldDropdown.appendChild(itemSelectionOption);
  itemsBoughtDropdown.appendChild(itemSelectionOption.cloneNode(true));
}

// Toggle between sale and buy forms
function toggleForm() {
  const isSale = transaction_type == "sale";
  const transactionTitles = document.querySelectorAll(".transaction-titles *");

  saleButton.className = isSale ? "btn btn-primary" : "btn btn-outline-primary";
  buyButton.className = isSale ? "btn btn-outline-primary" : "btn btn-primary";
  saleForm.style.display = isSale ? "block" : "none";
  buyForm.style.display = isSale ? "none" : "block";
  // Change titles and toggle received items selection
  document.querySelector(".items-received-selection").style.display = isSale
    ? "block"
    : "none";
  document.querySelector("#sold-selection-title").textContent = isSale
    ? "Add sold item"
    : "Add bought item";
  transactionTitles[0].textContent = isSale ? "Sold" : "Bought";
  transactionTitles[1].textContent = isSale ? "Received" : "Paid";
}

// Show register item form, hide trade register form
function register_item(button) {
  tradeDisplaySection.style.display = "none";
  tradeRegisterSection.style.display = "none";
  itemRegisterSection.style.display = "block";
  if (button.id == "add-received-item") {
    isReceivedItemForm = true;
  }
}

// Add item to the database
function add_item(event) {
  event.preventDefault();
  updateFormDisplayForNewItem();

  const formData = new FormData(itemRegisterForm);
  fetch("/register_item", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((errors) => {
          throw errors;
        });
      }
      return response.json();
    })
    .then((data) => {
      appendNewItem(data);
      clearErrors();
    })
    .catch((errors) => {
      console.error("Server errors:", errors);
      displayErrors(errors);
    });
}

function updateFormDisplayForNewItem() {
  tradeDisplaySection.style.display = "grid";
  tradeRegisterSection.style.display = "block";
  itemRegisterSection.style.display = "none";
}
// Append the new item to the page, received items container if it's a received item
function appendNewItem(data) {
  itemsContainer = isReceivedItemForm
    ? receivedItemsContainer
    : selectedItemsContainer;
  isReceivedItemForm = false;
  itemsContainer.insertAdjacentHTML("beforeend", data.item_html);
}

// Register trade to server, if successful redirect to trade display page
function register_trade(event) {
  console.log("Registering trade");
  // get selected items
  event.preventDefault();
  let itemIds = getItemIds(selectedItemsContainer);
  let itemReceivedIds = getItemIds(receivedItemsContainer);

  let formData = createFormData(event, itemIds, itemReceivedIds);
  fetch("/register_trade", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((errors) => {
          throw errors;
        });
      }
      return response.json();
    })
    .then((data) => {
      console.log(data.message);
      window.location.href = data.redirect_url;
    })
    .catch((errors) => {
      console.error("Server errors:", errors);
      displayErrors(errors);
    });
}

// Get the ids of the items in the trade preview selections
function getItemIds(container) {
  let ids = [];
  Array.from(container.children).forEach((item) => {
    if (item !== transactionBox) {
      let itemId = item.getAttribute("data-item-id");
      ids.push(itemId);
    }
  });
  return ids;
}

// Create and get form data to send to the server
function createFormData(event, itemIds, itemReceivedIds) {
  const formData = new FormData(event.target);
  // add transaction type
  formData.append("transaction_type", transaction_type);
  if (transaction_type == "buy") {
    formData.append("transaction_method", formData.get("transaction_method-2"));
    formData.delete("transaction_method-2");
  }
  formData.append("itemIds", JSON.stringify(itemIds));
  formData.append("itemReceivedIds", JSON.stringify(itemReceivedIds));
  formData.set("currency", formData.get("currency").toUpperCase());

  return formData;
}

// Function for handling JsonResponse errors and form errors
function displayErrors(errors) {
  console.log(errors);
  const errorElement = document.getElementById("trade-register-error");
  errorElement.innerHTML = "";
  errorElement.style.display = "block";

  if (errors.error) {
    // handle JsonResponse error message
    let errorDiv = document.createElement("div");
    errorDiv.textContent = errors.error;
    errorElement.appendChild(errorDiv);
  } else {
    // handle form errors
    for (let field in errors.errors) {
      let fieldErrors = errors.errors[field];
      for (let error of fieldErrors) {
        let errorDiv = document.createElement("div");
        errorDiv.textContent = `${field}: ${error}`;
        errorElement.appendChild(errorDiv);
      }
    }
  }
}

// Clear and hide error messages
function clearErrors() {
  const errorElement = document.getElementById("trade-register-error");
  errorElement.style.display = "none";
  errorElement.innerHTML = "";
}

// Make sure all amount fields have the same value in the sale and purchase forms
function duplicateFieldValues(fields, newValue) {
  fields.forEach((field) => {
    if (field.value !== newValue) {
      field.value = newValue;
    }
  });
}

// Update the transaction box display with the amount and currency
function updateTransactionBox(fieldValue) {
  if (fieldValue !== "") {
    boxSpan.textContent = fieldValue;
    if (currencyField.value !== "") {
      boxSpan.textContent += ` ${currencyField.value}`;
    }
  } else {
    boxSpan.textContent = "0";
  }
}

// Handle changes in the transaction method in the sale and purchase forms
function handleTransactionChange(transactionMethod) {
  switch (transactionMethod) {
    case TRANSACTION_METHODS.PAYPAL:
    case TRANSACTION_METHODS.SCM_FUNDS:
      handleCashTransactionMethod(transactionMethod);
      break;
    case TRANSACTION_METHODS.KEYS:
      handleKeyTransactionMethod(transactionMethod);
      break;
    case TRANSACTION_METHODS.ITEMS:
      handleItemsTransactionMethod(transactionMethod);
      break;
  }
  updateTransactionBoxCurrency(transactionMethod);
}

function handleCashTransactionMethod(transactionMethod) {
  const defaultSCMCurrency = document.querySelector(
    "#default-scm-currency"
  ).value;
  const defaultPaypalCurrency = document.querySelector(
    "#default-paypal-currency"
  ).value;

  setDisplayValue("block");
  const defaultCurrency =
    transactionMethod == TRANSACTION_METHODS.PAYPAL
      ? defaultPaypalCurrency
      : defaultSCMCurrency;
  currencyFields.forEach((field) => {
    field.value = defaultCurrency;
  });
  setTransactionBoxDisplay(transactionMethod, "normal");
}

function handleKeyTransactionMethod(transactionMethod) {
  setTransactionBoxDisplay(transactionMethod, "unique");
  setDisplayValue("block");
  hideCurrencyFieldsAndLabels();
}

function handleItemsTransactionMethod(transactionMethod) {
  setTransactionBoxDisplay(transactionMethod);
  setDisplayValue("none");
  // set the transaction method to keys if it's a purchase form
  const keysRadioButton2 = [...purchaseTransactionRadioButtons].find(
    (radioButton2) => radioButton2.value == TRANSACTION_METHODS.KEYS
  );
  if (keysRadioButton2) {
    keysRadioButton2.checked = true;
    if (amountFields[1] && amountLabels[1]) {
      amountFields[1].style.display = "block";
      amountLabels[1].style.display = "block";
    }
  }
}

// Set the transaction box display based on the transaction method, quality is border and text color
function setTransactionBoxDisplay(transactionMethod, quality) {
  if (transactionMethod == TRANSACTION_METHODS.ITEMS) {
    transactionBox.style.display = "none";
    return;
  }

  const itemBox = document.getElementById("transaction-method-box");
  const transactionSpan = document.querySelector(".transaction-method");
  const itemImage = document.getElementById("transaction-method-image");

  transactionBox.style.display = "flex";
  itemImage.src = TRANSACTION_IMAGES[transactionMethod];
  updateClassList(itemBox, `border-${quality}`);
  updateClassList(transactionSpan, quality);
  transactionSpan.textContent =
    transactionMethod == TRANSACTION_METHODS.SCM_FUNDS
      ? "scm funds"
      : transactionMethod;
}

function updateClassList(element, newClass) {
  element.classList.remove(element.className.split(" ").pop());
  element.classList.add(newClass);
}

// Set display for amount and currency fields ( block or none)
function setDisplayValue(displayValue) {
  amountFields.forEach((field, index) => {
    field.style.display = displayValue;
    amountLabels[index].style.display = displayValue;
    currencyFields[index].style.display = displayValue;
    currencyLabels[index].style.display = displayValue;
  });
}

// Update the currency in the transaction box, if any
function updateTransactionBoxCurrency(transactionMethod) {
  boxSpan.textContent = boxSpan.textContent.split(" ")[0];
  if (
    currencyField.value !== "" &&
    transactionMethod !== TRANSACTION_METHODS.KEYS
  ) {
    boxSpan.textContent += ` ${currencyField.value}`;
  }
}

// Hide currency fields and labels (if the transaction method is 'keys')
function hideCurrencyFieldsAndLabels() {
  currencyFields.forEach((field, index) => {
    field.style.display = "none";
    currencyLabels[index].style.display = "none";
  });
}

// Add item removal event listeners
function addItemRemovalListener(elements) {
  elements.forEach((element) => {
    element.addEventListener("dblclick", (event) => {
      if (event.target.closest(".item-box")) {
        getAndRemoveTargetItem(event);
      }
    });
  });
}

// Event Listeners

function addListeners() {
  saleButton.addEventListener("click", () => {
    transaction_type = "sale";
    toggleForm();
  });

  buyButton.addEventListener("click", () => {
    transaction_type = "buy";
    toggleForm();
    clearReceivedItems();
  });

  // Add item to selected sold items
  itemsSoldDropdown.addEventListener("dblclick", (event) => {
    addItemToSelectedItems(event, "sold");
  });

  // Add item to selected bought items
  itemsBoughtDropdown.addEventListener("dblclick", (event) => {
    addItemToSelectedItems(event, "bought");
  });

  addItemRemovalListener([selectedItemsContainer, receivedItemsContainer]);

  amountFields.forEach((field) => {
    field.addEventListener("input", () => {
      duplicateFieldValues(amountFields, field.value);
      updateTransactionBox(field.value);
    });
  });

  // Make sure the currency field is updated when the currency is changed
  currencyFields.forEach((field) => {
    field.addEventListener("input", () => {
      duplicateFieldValues(currencyFields, field.value);
      updateTransactionBox(amountFields[0].value);
    });
  });

  // Handle transaction method changes to sale and purchase forms
  saleTransactionRadioButtons.forEach((radioButton, index) => {
    radioButton.addEventListener("change", () => {
      handleTransactionChange(radioButton.value);
      if (radioButton.value != TRANSACTION_METHODS.ITEMS) {
        purchaseTransactionRadioButtons[index].checked = radioButton.checked;
      }
    });
  });

  purchaseTransactionRadioButtons.forEach((radioButton, index) => {
    radioButton.addEventListener("change", () => {
      handleTransactionChange(radioButton.value);
      saleTransactionRadioButtons[index].checked = radioButton.checked;
    });
  });

  // add new item to trade
  document.querySelectorAll(".add-item").forEach((button) => {
    button.addEventListener("click", () => register_item(button));
  });

  // Form submit buttons

  itemRegisterForm.addEventListener("submit", (event) => {
    add_item(event);
  });

  saleForm.addEventListener("submit", (event) => {
    register_trade(event);
  });
  buyForm.addEventListener("submit", (event) => {
    register_trade(event);
  });
}

document.addEventListener("DOMContentLoaded", function () {
  saleButton = document.querySelector("#sale");
  buyButton = document.querySelector("#buy");
  saleForm = document.querySelector("#sale-form");
  buyForm = document.querySelector("#buy-form");

  itemRegisterForm = document.querySelector("#item-register-form");
  itemRegisterSection = document.querySelector("#item-register");
  tradeRegisterSection = document.querySelector("#trade-register");
  tradeDisplaySection = document.querySelector(".trade-display-container");
  selectedItemsContainer = document.getElementById("selected-items");
  receivedItemsContainer = document.getElementById("received-items");
  transactionBox = document.getElementById("transaction-method-box");
  itemsSoldDropdown = document.querySelector("#id_items_sold");
  itemsBoughtDropdown = document.querySelector("#id_items_bought");
  saleTransactionRadioButtons = document.querySelectorAll(
    'input[name="transaction_method"]'
  );
  purchaseTransactionRadioButtons = document.querySelectorAll(
    'input[name="transaction_method-2"]'
  );
  amountFields = document.querySelectorAll(".amount-field");
  currencyFields = document.querySelectorAll(".currency-field");
  boxSpan = document.querySelector(".pure-amount");
  currencyField = document.querySelector(".currency-field");
  amountLabels = document.querySelectorAll(".amount-label");
  currencyLabels = document.querySelectorAll(".currency-label");

  // Set initial display styles
  document.querySelector("#buy-form").style.display = "none";
  itemRegisterSection.style.display = "none";

  // Add event listeners and set initial transaction method
  addListeners();
  handleTransactionChange(TRANSACTION_METHODS.KEYS);
});
