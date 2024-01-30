document.addEventListener('DOMContentLoaded', function() {
    const saleButton = document.querySelector('#sale');
    const buyButton = document.querySelector('#buy');
    const saleForm = document.querySelector('#sale-form');
    const buyForm = document.querySelector('#buy-form');
    const transactionTitles = document.querySelectorAll('.transaction-titles *');
    const itemRegisterForm = document.querySelector('#item-register-form');
    const itemRegisterSection = document.querySelector('#item-register');
    const tradeRegisterSection = document.querySelector('#trade-register');
    const tradeDisplaySection = document.querySelector('.trade-display-container');
    const selectedItemsContainer = document.getElementById('selected-items');
    const recievedItemsContainer = document.getElementById('recieved-items');
    const itemsSoldDropdown = document.querySelector('#id_items_sold');
    const itemsBoughtDropdown = document.querySelector('#id_items_bought');
    const tradeSubmitButton = document.querySelector('#trade-submit-button');
    const transactionMethodRadioButtons = document.querySelectorAll('input[name="transaction_method"]');
    const transactionMethodRadioButtons2 = document.querySelectorAll('input[name="transaction_method-2"]');
    

    saleButton.addEventListener('click', () => {
        transaction_type = 'sale';
        toggleForm();
    });

    buyButton.addEventListener('click', () => {
        transaction_type = 'buy';
        toggleForm();
        clearRecievedItems();
    });

    
    document.querySelector('#buy-form').style.display = 'none';
    transaction_type = 'sale';
    itemRegisterSection.style.display = 'none';

    itemsSoldDropdown.addEventListener('dblclick', (event) => {
        addItemToSelectedItems(event, 'sold')
    });

    selectedItemsContainer.addEventListener('dblclick', (event) => {
        if (event.target.closest('.item-box')) {
            getTargetItem(event);
        }
    });

    recievedItemsContainer.addEventListener('dblclick', (event) => {
        if (event.target.closest('.item-box')) {
            getTargetItem(event);
        }
    });

    document.querySelectorAll('[name="items_bought"]').forEach(item_selection => {
        item_selection.addEventListener('dblclick', (event) => {
            addItemToSelectedItems(event, 'bought')
        });
    });

    transactionMethodRadioButtons.forEach((radioButton, index) => {
        radioButton.addEventListener('change', () => {
            handleTransactionChange(radioButton.value);
            if (radioButton.value != 'items') {
                transactionMethodRadioButtons2[index].checked = radioButton.checked;
            }
        });
    });

    transactionMethodRadioButtons2.forEach((radioButton, index) => {
        radioButton.addEventListener('change', () => {
            handleTransactionChange(radioButton.value);
            transactionMethodRadioButtons[index].checked = radioButton.checked;
        });
    });


    // add new item
    document.querySelectorAll('.add-item').forEach(button => {
        button.addEventListener('click', () => register_item(button));
    });

    //Item submit button
    itemRegisterForm.addEventListener('submit', (event) => {
        console.log("Item submit button clicked");
        add_item(event)
    });

    //Trade submit button
    saleForm.addEventListener('submit', (event) => {
            console.log("Sale submit button clicked");
            register_trade(event)
    });
    buyForm.addEventListener('submit', (event) => {
        console.log("Buy submit button clicked");
        register_trade(event)
    });

    let selectedItems = new Set();

    function addItemToSelectedItems(event, item_type) {
        console.log(event.target)
        const selectedItemId = event.target.value;
    
        // Check if the item is already selected
        if (selectedItems.has(selectedItemId)) {
            alert('Item already selected!');
            return;
        }

        selectedItems.add(selectedItemId);

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
                recievedItemsContainer.insertAdjacentHTML('beforeend', data.item_html);
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

    function getTargetItem(event) {
        let itemElement = event.target.closest('.item-box');
        removeItemFromSelection(itemElement);
    }

    function clearRecievedItems() {
        Array.from(recievedItemsContainer.children).forEach(item => {
            removeItemFromSelection(item);
        });
    }

    function removeItemFromSelection(itemElement) {
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
        saleButton.className = (transaction_type == 'sale') ? 'btn btn-primary' : 'btn btn-outline-primary';
        buyButton.className = (transaction_type == 'buy') ? 'btn btn-primary' : 'btn btn-outline-primary';
        saleForm.style.display = (transaction_type == 'sale') ? 'block' : 'none';
        buyForm.style.display = (transaction_type == 'buy') ? 'block' : 'none';
        // Change titles and hide recieved items selection
        document.querySelector('.items-recieved-selection').style.display = (transaction_type == 'sale') ? 'block' : 'none';
        document.querySelector('#sold-selection-title').textContent = (transaction_type == 'sale') ? 'Add sold item' : 'Add bought item';
        transactionTitles[0].textContent = (transaction_type == 'sale') ? 'Sold' : 'Bought';
        transactionTitles[1].textContent = (transaction_type == 'sale') ? 'Recieved' : 'Paid';
    }

    function register_item(button) {
        tradeDisplaySection.style.display = 'none';
        tradeRegisterSection.style.display = 'none';
        itemRegisterSection.style.display = 'block';
        if (button.id == 'add-recieved-item') {
            itemRegisterForm.className += ' recieved-item-form';
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

            itemsContainer = document.getElementById('selected-items');
            if (itemRegisterForm.classList.contains('recieved-item-form')) {
                itemsContainer = document.getElementById('recieved-items');
                itemRegisterForm.classList.remove('recieved-item-form');
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
        itemRecievedIds = [];
        Array.from(selectedItemsContainer.children).forEach(item => {
            let itemId = item.getAttribute('data-item-id');
            itemIds.push(itemId);
        });
        Array.from(recievedItemsContainer.children).forEach(item => {
            let itemId = item.getAttribute('data-item-id');
            itemRecievedIds.push(itemId);
        });

        const formData = new FormData(event.target);
        // add transaction type
        formData.append('transaction_type', transaction_type);
        if (transaction_type == 'buy') {
            formData.append('transaction_method', formData.get('transaction_method-2'));
            formData.delete('transaction_method-2');
        }
        formData.append('itemIds', JSON.stringify(itemIds));
        formData.append('itemRecievedIds', JSON.stringify(itemRecievedIds));
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
            console.log("Data sent sucsessfully", data);
            tradeRegisterSection.insertAdjacentHTML('afterbegin', data.transaction_html);
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


    function handleTransactionChange(transactionMethod) {
        const amountFields = document.querySelectorAll('.amount-field');
        const amountLabels = document.querySelectorAll(".amount-label");
        const currencyFields = document.querySelectorAll('.currency-field');
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

        function setCurrencyDisplayAndValue(displayValue) {
            currencyFields.forEach((field, index) => {
                field.style.display = 'none';
                currencyLabels[index].style.display = displayValue;
            });
        }

        if (transactionMethod == 'paypal' || transactionMethod == 'scm_funds') {
            setDisplayAndValue('block');
            const defaultCurrency = transactionMethod == 'paypal' ? defaultPaypalCurrency : defaultSCMCurrency;
            currencyFields.forEach(field => {
                field.value = defaultCurrency;
            });
        } else if (transactionMethod == 'keys') {
            setDisplayAndValue('block');
            setCurrencyDisplayAndValue('none');
        
        } else if (transactionMethod == 'items') {
            // If 'items' selected, default option 2 to 'keys'
            setDisplayAndValue('none');
            const keysRadioButton2 = [...transactionMethodRadioButtons2].find(radioButton2 => radioButton2.value == 'keys');
            if (keysRadioButton2) {
                keysRadioButton2.checked = true;
                if (amountFields[1] && amountLabels[1]) {
                    amountFields[1].style.display = 'block';
                    amountLabels[1].style.display = 'block';
                }
            }
        }
    }
    // Start with the first transaction method dropdown
    handleTransactionChange('keys');
});


