// Variable decorations
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

let selectedItems = new Set();
let transaction_type = 'sale';

// Function Declarations

function addItemToSelectedItems(event, item_type) {
    console.log(event.target)
    const selectedItemId = event.target.value;

    // Check if the item is already selected
    if (selectedItems.has(selectedItemId)) {
        alert('Item already selected!');
        return;
    }

    selectedItems.add(selectedItemId);
    console.log(selectedItemId)

    // Append the selected item to the "Selected Items" container
    const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/get_item_html/${selectedItemId}`, {
        method: 'POST',
        headers: { "X-CSRFToken": csrf }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Data sent sucsessfully", data);
        // Append the new item to the page
        
        if (item_type == 'bought' && transaction_type == 'sale') {
            receivedItemsContainer.insertAdjacentHTML('beforeend', data.item_html);
            let selectedIndex = itemsBoughtDropdown.selectedIndex;
            itemsBoughtDropdown.remove(selectedIndex);
            itemsSoldDropdown.remove(selectedIndex);
        } else {
            selectedItemsContainer.insertAdjacentHTML('beforeend', data.item_html);
            let selectedIndex = itemsSoldDropdown.selectedIndex;
            itemsSoldDropdown.remove(selectedIndex);
            itemsBoughtDropdown.remove(selectedIndex);
        }
        
    })
    .catch(error => {
        console.error('Error:', error);
    })
}

function getAndRemoveTargetItem(event) {
    let itemElement = event.target.closest('.item-box');
    removeItemFromSelection(itemElement);
}

function clearReceivedItems() {
    Array.from(receivedItemsContainer.children).forEach(item => {
        removeItemFromSelection(item);
    });
}

function removeItemFromSelection(itemElement) {
    if (itemElement === transactionBox) {
        return;
    }
    let itemId = itemElement.getAttribute('data-item-id');
    selectedItems.delete(itemId);
    itemElement.remove();
    let itemSelectionOption = document.createElement('option');
    itemSelectionOption.value = itemId;
    itemSelectionOption.text = itemElement.querySelector('span').textContent;
    itemsSoldDropdown.appendChild(itemSelectionOption);
    itemsBoughtDropdown.appendChild(itemSelectionOption.cloneNode(true));
}


function toggleForm() {
    const transactionTitles = document.querySelectorAll('.transaction-titles *');

    saleButton.className = (transaction_type == 'sale') ? 'btn btn-primary' : 'btn btn-outline-primary';
    buyButton.className = (transaction_type == 'buy') ? 'btn btn-primary' : 'btn btn-outline-primary';
    saleForm.style.display = (transaction_type == 'sale') ? 'block' : 'none';
    buyForm.style.display = (transaction_type == 'buy') ? 'block' : 'none';
    // Change titles and hide received items selection
    document.querySelector('.items-received-selection').style.display = (transaction_type == 'sale') ? 'block' : 'none';
    document.querySelector('#sold-selection-title').textContent = (transaction_type == 'sale') ? 'Add sold item' : 'Add bought item';
    transactionTitles[0].textContent = (transaction_type == 'sale') ? 'Sold' : 'Bought';
    transactionTitles[1].textContent = (transaction_type == 'sale') ? 'Received' : 'Paid';
}

function register_item(button) {
    tradeDisplaySection.style.display = 'none';
    tradeRegisterSection.style.display = 'none';
    itemRegisterSection.style.display = 'block';
    if (button.id == 'add-received-item') {
        itemRegisterForm.className += ' received-item-form';
    }
}

function add_item(event) {
    event.preventDefault();
    tradeDisplaySection.style.display = 'grid';
    tradeRegisterSection.style.display = 'block';
    itemRegisterSection.style.display = 'none';

    const formData = new FormData(itemRegisterForm);
    console.log(formData);
    fetch('/register_item', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errors => {
                throw errors;
            });
        }
        return response.json();
    })
    .then(data => {
        console.log("Data sent sucsessfully", data);
        // Append the new item to the page

        itemsContainer = selectedItemsContainer;
        if (itemRegisterForm.classList.contains('received-item-form')) {
            itemsContainer = receivedItemsContainer;
            itemRegisterForm.classList.remove('received-item-form');
        }
        itemsContainer.insertAdjacentHTML('beforeend', data.item_html);
        clearErrors();
        
    })
    .catch(errors => {
        console.error('Server errors:', errors);
        displayErrors(errors);
    })
}

function register_trade(event) {
    console.log("Registering trade")
    // get selected items
    event.preventDefault();
    let itemIds = [];
    itemReceivedIds = [];
    Array.from(selectedItemsContainer.children).forEach(item => {
        let itemId = item.getAttribute('data-item-id');
        itemIds.push(itemId);
    });
    Array.from(receivedItemsContainer.children).forEach(item => {
        if (item !== transactionBox) {
            let itemId = item.getAttribute('data-item-id');
            itemReceivedIds.push(itemId);
        }
    });

    const formData = new FormData(event.target);
    // add transaction type
    formData.append('transaction_type', transaction_type);
    if (transaction_type == 'buy') {
        formData.append('transaction_method', formData.get('transaction_method-2'));
        formData.delete('transaction_method-2');
    }
    formData.append('itemIds', JSON.stringify(itemIds));
    formData.append('itemReceivedIds', JSON.stringify(itemReceivedIds));
    console.log(formData);
    formData.set('currency', formData.get('currency').toUpperCase());
    fetch('/register_trade', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errors => {
                throw errors;
            });
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message);
        window.location.href = data.redirect_url;
    })
    .catch(errors => {
        console.error('Server errors:', errors);
        displayErrors(errors);
    });
}

function displayErrors(errors) {
    console.log(errors);
    const errorElement = document.getElementById('trade-register-error');
    errorElement.innerHTML = '';
    errorElement.style.display = 'block';

    if (errors.error) {
        // handle JsonResponse error message
        let errorDiv = document.createElement('div');
        errorDiv.textContent = errors.error;
        errorElement.appendChild(errorDiv);
    } else {
        // handle form errors
        for (let field in errors.errors) {
            let fieldErrors = errors.errors[field];
            for (let error of fieldErrors) {
                let errorDiv = document.createElement('div');
                errorDiv.textContent = `${field}: ${error}`;
                errorElement.appendChild(errorDiv);
            }
        }
    }
}

function clearErrors() {
    const errorElement = document.getElementById('trade-register-error');
    errorElement.style.display = 'none';
    errorElement.innerHTML = '';
}

// Make sure all amount fields have the same value
function duplicateFieldValues(fields, newValue) {
    fields.forEach(field => {
        if (field.value !== newValue) {
            field.value = newValue;
        }
    });
}

function updateTransactionBox(fieldValue) {
    if (fieldValue !== '') {
        boxSpan.textContent = fieldValue;
        if (currencyField.value !== '') {
            boxSpan.textContent += ` ${currencyField.value}`;
        }
    } else {
        boxSpan.textContent = '0';
    }
}

function handleTransactionChange(transactionMethod) {
    const amountLabels = document.querySelectorAll(".amount-label");
    
    const currencyLabels = document.querySelectorAll('.currency-label');
    const defaultSCMCurrency = document.querySelector('#default-scm-currency').value;
    const defaultPaypalCurrency = document.querySelector('#default-paypal-currency').value;

    function setDisplayAndValue(displayValue) {
        amountFields.forEach((field, index) => {
            field.style.display = displayValue;
            amountLabels[index].style.display = displayValue;
            currencyFields[index].style.display = displayValue;
            currencyLabels[index].style.display = displayValue;
        });
    }

    function setTransactionBoxDisplay(transactionMethod, quality) {
        if (transactionMethod == 'items') {
            transactionBox.style.display = 'none';
            return;
        }
        transactionMethod = transactionMethod == 'scm_funds' ? 'scm funds' : transactionMethod;
        const keyImage = 'https://steamcdn-a.akamaihd.net/apps/440/icons/key.be0a5e2cda3a039132c35b67319829d785e50352.png';
        const scmImage = 'https://community.cloudflare.steamstatic.com/public/shared/images/responsive/share_steam_logo.png';
        const paypalImage = 'https://developer.valvesoftware.com/w/images/thumb/f/f9/Smallcredits.png/300px-Smallcredits.png';
        const itemBox = document.getElementById('transaction-method-box')
        const transactionSpan = document.querySelector('.transaction-method');
        const itemImage = document.getElementById('transaction-method-image')

        transactionBox.style.display = 'flex';
        itemImage.src = transactionMethod === 'keys' ? keyImage : transactionMethod === 'scm funds' ? scmImage : paypalImage;
        updateClassList(itemBox, `border-${quality}`);
        updateClassList(transactionSpan, quality);
        transactionSpan.textContent = transactionMethod;    
    }

    function updateClassList(element, newClass) {
        element.classList.remove(element.className.split(' ').pop());
        element.classList.add(newClass);
    }

    function updateTransactionBoxCurrency(transactionMethod) {
        boxSpan.textContent = boxSpan.textContent.split(' ')[0];
        if (currencyField.value !== '' && transactionMethod !== 'keys') {
            boxSpan.textContent += ` ${currencyField.value}`;
        }
    }

    function hideCurrencyFieldsAndLabels() {
        currencyFields.forEach((field, index) => {
            field.style.display = 'none';
            currencyLabels[index].style.display = 'none';
        });
    }

    if (transactionMethod == 'paypal' || transactionMethod == 'scm_funds') {
        setDisplayAndValue('block');
        const defaultCurrency = transactionMethod == 'paypal' ? defaultPaypalCurrency : defaultSCMCurrency;
        currencyFields.forEach(field => {
            field.value = defaultCurrency;
        });
        setTransactionBoxDisplay(transactionMethod, 'normal');
    } else if (transactionMethod == 'keys') {
        setTransactionBoxDisplay(transactionMethod, 'unique');
        setDisplayAndValue('block');
        hideCurrencyFieldsAndLabels();
    
    } else if (transactionMethod == 'items') {
        setTransactionBoxDisplay(transactionMethod);
        // If 'items' selected, default option 2 to 'keys'
        setDisplayAndValue('none');
        const keysRadioButton2 = [...purchaseTransactionRadioButtons].find(radioButton2 => radioButton2.value == 'keys');
        if (keysRadioButton2) {
            keysRadioButton2.checked = true;
            if (amountFields[1] && amountLabels[1]) {
                amountFields[1].style.display = 'block';
                amountLabels[1].style.display = 'block';
            }
        }
    }
    updateTransactionBoxCurrency(transactionMethod);
}

// update location

function addItemRemovalListener(elements) {
    elements.forEach(element => {
        element.addEventListener('dblclick', (event) => {
            if (event.target.closest('.item-box')) {
                getAndRemoveTargetItem(event);
            }
        });
    });
}

// Event Listeners

function addListeners() {
    
    saleButton.addEventListener('click', () => {
        transaction_type = 'sale';
        toggleForm();
    });

    buyButton.addEventListener('click', () => {
        transaction_type = 'buy';
        toggleForm();
        clearReceivedItems();
    });

    // Add item to selected sold items
    itemsSoldDropdown.addEventListener('dblclick', (event) => {
        addItemToSelectedItems(event, 'sold')
    });
    
    // Add item to selected bought items
    itemsBoughtDropdown.addEventListener('dblclick', (event) => {
            addItemToSelectedItems(event, 'bought')
    });

    addItemRemovalListener([selectedItemsContainer, receivedItemsContainer]);


    amountFields.forEach(field => {
        field.addEventListener('input', () => {
            duplicateFieldValues(amountFields, field.value);
            updateTransactionBox(field.value);
        });
    });

    // Make sure the currency field is updated when the currency is changed
    currencyFields.forEach(field => {
        field.addEventListener('input', () => {
            duplicateFieldValues(currencyFields, field.value);
            updateTransactionBox(amountFields[0].value);
        });
    });

    // Handle transaction method changes to sale and purchase forms
    saleTransactionRadioButtons.forEach((radioButton, index) => {
        radioButton.addEventListener('change', () => {
            handleTransactionChange(radioButton.value);
            if (radioButton.value != 'items') {
                purchaseTransactionRadioButtons[index].checked = radioButton.checked;
            }
        });
    });

    purchaseTransactionRadioButtons.forEach((radioButton, index) => {
        radioButton.addEventListener('change', () => {
            handleTransactionChange(radioButton.value);
            saleTransactionRadioButtons[index].checked = radioButton.checked;
        });
    });

    // add new item to trade
    document.querySelectorAll('.add-item').forEach(button => {
        button.addEventListener('click', () => register_item(button));
    });

    // Form submit buttons

    itemRegisterForm.addEventListener('submit', (event) => {
        add_item(event)
    });

    saleForm.addEventListener('submit', (event) => {
            register_trade(event)
    });
    buyForm.addEventListener('submit', (event) => {
        register_trade(event)
    });
}

document.addEventListener('DOMContentLoaded', function() {
    saleButton = document.querySelector('#sale');
    buyButton = document.querySelector('#buy');
    saleForm = document.querySelector('#sale-form');
    buyForm = document.querySelector('#buy-form');
    
    itemRegisterForm = document.querySelector('#item-register-form');
    itemRegisterSection = document.querySelector('#item-register');
    tradeRegisterSection = document.querySelector('#trade-register');
    tradeDisplaySection = document.querySelector('.trade-display-container');
    selectedItemsContainer = document.getElementById('selected-items');
    receivedItemsContainer = document.getElementById('received-items');
    transactionBox = document.getElementById('transaction-method-box');
    itemsSoldDropdown = document.querySelector('#id_items_sold');
    itemsBoughtDropdown = document.querySelector('#id_items_bought');
    saleTransactionRadioButtons = document.querySelectorAll('input[name="transaction_method"]');
    purchaseTransactionRadioButtons = document.querySelectorAll('input[name="transaction_method-2"]');
    amountFields = document.querySelectorAll('.amount-field');
    currencyFields = document.querySelectorAll('.currency-field');
    boxSpan = document.querySelector('.pure-amount');
    currencyField = document.querySelector('.currency-field');
    
    // Set initial display styles
    document.querySelector('#buy-form').style.display = 'none';
    itemRegisterSection.style.display = 'none';

    // Add event listeners and set initial transaction method
    addListeners();
    handleTransactionChange('keys');
});


