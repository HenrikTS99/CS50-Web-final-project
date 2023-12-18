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
        .then(response => response.json())
        .then(data => {
            console.log("Data sent sucsessfully", data);
            // Append the new item to the page

            itemsContainer = document.getElementById('selected-items');
            if (itemRegisterForm.classList.contains('recieved-item-form')) {
                itemsContainer = document.getElementById('recieved-items');
                itemRegisterForm.classList.remove('recieved-item-form');
            }
            itemsContainer.insertAdjacentHTML('beforeend', data.item_html);
        })
        .catch(error => {
            console.error('Error:', error);
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

        console.log(itemIds);
        console.log(itemRecievedIds);

        const formData = new FormData(event.target);
        // add transaction type
        formData.append('transaction_type', transaction_type);
        formData.append('itemIds', JSON.stringify(itemIds));
        formData.append('itemRecievedIds', JSON.stringify(itemRecievedIds));
        console.log(formData);
        fetch('/register_trade', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("Data sent sucsessfully", data);
            tradeRegisterSection.insertAdjacentHTML('afterbegin', data.transaction_html);
            console.log(data.transaction_html);
            window.location.href = data.redirect_url;
        })
        .catch(error => {
            console.error('Error:', error);
        })
    }
});