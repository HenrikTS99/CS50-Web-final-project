document.addEventListener('DOMContentLoaded', function() {
    const saleButton = document.querySelector('#sale');
    const buyButton = document.querySelector('#buy');
    const saleForm = document.querySelector('#sale-form');
    const buyForm = document.querySelector('#buy-form');
    const itemRegisterForm = document.querySelector('#item-register-form');
    const itemRegisterSection = document.querySelector('#item-register');
    const tradeRegisterSection = document.querySelector('#trade-register');
    const selectedItemsContainer = document.getElementById('selected-items');
    const recievedItemsContainer = document.getElementById('recieved-items');
    const itemsSoldDropdown = document.querySelector('#id_items_sold');
    const itemsBoughtDropdown = document.querySelector('#id_items_bought');
    const tradeSubmitButton = document.querySelector('#trade-submit-button');
    const transactionMethodDropdowns = document.querySelectorAll('.transaction-method');
    

    saleButton.addEventListener('click', () => sale_form());
    buyButton.addEventListener('click', () => buy_form());
    document.querySelector('#buy-form').style.display = 'none';
    transaction_type = 'sale';
    itemRegisterSection.style.display = 'none';

    itemsSoldDropdown.addEventListener('dblclick', (event) => {
        addItemToSelectedItems(event, 'sold')
    });
    document.querySelectorAll('[name="items_bought"]').forEach(item_selection => {
        item_selection.addEventListener('dblclick', (event) => {
            addItemToSelectedItems(event, 'bought')
        });
    });

    transactionMethodDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', () => {
            handleTransactionChange(dropdown.value);
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
                itemsBoughtDropdown.remove(itemsBoughtDropdown.selectedIndex);
            } else {
                selectedItemsContainer.insertAdjacentHTML('beforeend', data.item_html);
                itemsSoldDropdown.remove(itemsSoldDropdown.selectedIndex);
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
        })
    }

    function sale_form() {
        transaction_type = 'sale';
        saleButton.className = 'btn btn-sm btn-primary'
        buyButton.className = 'btn btn-sm btn-outline-primary';
        document.querySelector('#sale-form').style.display = 'block';
        document.querySelector('#buy-form').style.display = 'none';
    }

    function buy_form() {
        transaction_type = 'buy';
        buyButton.className = 'btn btn-sm btn-primary';
        saleButton.className = 'btn btn-sm btn-outline-primary';
        document.querySelector('#sale-form').style.display = 'none';
        document.querySelector('#buy-form').style.display = 'block';
    }

    function register_item(button) {
        console.log(button);
        tradeRegisterSection.style.display = 'none';
        itemRegisterSection.style.display = 'block';
        if (button.id == 'add-recieved-item') {
            itemRegisterForm.className += ' recieved-item-form';
            console.log(button.id);
        }
    }

    function add_item(event) {
        event.preventDefault();
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
        const currencyLabels = document.querySelectorAll(".currency-label");
        const defaultSCMCurrency = document.querySelector('#default-scm-currency').value;
        const defaultPaypalCurrency = document.querySelector('#default-paypal-currency').value;

        function setDisplayAndValue(displayValue, fieldValue = '') {
            amountFields.forEach((field, index) => {
                field.style.display = displayValue;
                amountLabels[index].style.display = displayValue;
                field.value = fieldValue;
                currencyFields[index].style.display = displayValue;
                currencyLabels[index].style.display = displayValue;
                currencyFields[index].value = fieldValue;
                transactionMethodDropdowns[index].value = transactionMethod;
            });
        }

        if (transactionMethod == 'paypal' || transactionMethod == 'scm_funds') {
            setDisplayAndValue('block');
            if (transactionMethod == 'paypal') {
                currencyFields.forEach(field => {
                    field.value = defaultPaypalCurrency;
                });
            } else if (transactionMethod == 'scm_funds') {
                currencyFields.forEach(field => {
                    field.value = defaultSCMCurrency;
                });
            }
        } else if (transactionMethod == 'keys') {
            setDisplayAndValue('block');
            currencyFields.forEach(field => {
                field.style.display = 'none';
            });
        } else if (transactionMethod == 'items') {
            // Item value dosent have transactionMethod items, default to keys
            setDisplayAndValue('none');
            document.querySelector('#id_item_value-0-transaction_method').value = 'keys';
            document.getElementById('id_item_value-0-amount').style.display = 'block';
            document.querySelector("label[for='id_item_value-0-amount']").style.display = 'block';
        }
    }
    // Start with the first transaction method dropdown
    handleTransactionChange(transactionMethodDropdowns[0].value);
});


