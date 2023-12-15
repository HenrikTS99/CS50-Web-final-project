document.addEventListener('DOMContentLoaded', function() {
    const saleButton = document.querySelector('#sale');
    const buyButton = document.querySelector('#buy');
    const tradeRegisterForm = document.querySelector('#trade-register-form');
    const itemRegisterForm = document.querySelector('#item-register-form');
    const itemRegisterSection = document.querySelector('#item-register');
    const tradeRegisterSection = document.querySelector('#trade-register');
    const selectedItemsContainer = document.getElementById('selected-items');
    const itemsSoldDropdown = document.querySelector('#id_items_sold');
    const tradeSubmitButton = document.querySelector('#trade-submit-button');

    saleButton.addEventListener('click', () => sale_form());
    buyButton.addEventListener('click', () => buy_form());
    document.querySelector('#buy-form').style.display = 'none';
    transaction_type = 'sale';
    itemRegisterSection.style.display = 'none';
    
    itemsSoldDropdown.addEventListener('dblclick', addItemToSelectedItems);
    // add new item
    document.querySelector('#add-item').addEventListener('click', () => register_item());

    //Item submit button
    itemRegisterForm.addEventListener('submit', (event) => {
        console.log("Item submit button clicked");
        add_item(event)
    });

    //Trade submit button
    tradeRegisterForm.addEventListener('submit', (event) => {
            console.log("Trade submit button clicked");
            register_trade(event)
    });

    let selectedItems = new Set();

    function addItemToSelectedItems() {
        const selectedItemId = itemsSoldDropdown.value;
    
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
            selectedItemsContainer.insertAdjacentHTML('beforeend', data.item_html);
            itemsSoldDropdown.remove(itemsSoldDropdown.selectedIndex);
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

    function register_item() {
        tradeRegisterSection.style.display = 'none';
        itemRegisterSection.style.display = 'block';
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
            const itemsContainer = document.getElementById('selected-items');
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
        Array.from(selectedItemsContainer.children).forEach(item => {
            let itemId = item.getAttribute('data-item-id');
            itemIds.push(itemId);
        });

        console.log(itemIds);

        const formData = new FormData(tradeRegisterForm);
        // add transaction type
        formData.append('transaction_type', transaction_type);
        formData.append('itemIds', JSON.stringify(itemIds));
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