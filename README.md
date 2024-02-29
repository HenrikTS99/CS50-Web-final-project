# TF2Folio

## Overview

TF2Folio is a Django web application designed to log and track trades and profits from trading items from Team Fortress 2 (TF2). This application is designed to assist TF2 traders in managing their trading activities by enabling them to log their trades, keep track of their inventory and transactions, and automatically calculate profits from these trades when possible.

The application is built with Django for the backend, and JavaScript and SCSS for the frontend. It is containerized using Docker and uses postgres as the database.

This is my final project for the 'CS50's Web Programming with Python and JavaScript' course. It therefore follows the requirements specified in the [CS50 Capstone Project Guidelines](https://cs50.harvard.edu/web/2020/projects/final/capstone/).

## Quick Overview of Team Fortress 2 Trading

### Team Fortress 2
Team fortress 2 (TF2) is a multiplayer video game released by Valve in 2007. The game continues to thrive, with an active trading community. Within TF2, players can acquire a diverse range of items, including cosmetics and weapons, which are mostly used to customize their in-game characters. These items can be obtained through trading with other users via the Steam platform. Some of these items hold real life value, with the most expensive and rare items fetching prices of tens of thousands of dollars.

### Items
In TF2, items can come in many different qualities and can have many different attributes applied to them. These qualities and attributes are crucial for determining their value within the game. 
While these qualities and attributes are important for gameplay and trading, understanding what they mean isn't necessary to understand the project. The item registration form displays the most crucial attributes and qualities.
<details>
    <summary>Click to view item form</summary>
    <img src="https://gyazo.com/d20a5bfa9ad34d25f6b20bf9ed02a89a.png" alt="Item form">
</details>  

### Different Currencies
TF2 Trading can use many different currencies. The most Common being TF2 Keys, Refined Metal, Cash, and Steam wallet funds. In this project, I utilize Keys, Cash (also referred to as Paypal within the project), and Steam funds. These currencies are often referred to as 'pure'. When an item is bought or sold for 'pure', it typically means that it was exchanged for a currency, and not for other items.

### TF2 Keys
TF2 Keys are in-game tools that can be used to open loot cases in the game, but they also serve as currency for trading. They function as cash in the game and are typically the default currency, including in this project. At the time of writing this, one key is worth approximately:
* [62 Refined Metal](https://backpack.tf/classifieds?item=Mann+Co.+Supply+Crate+Key&quality=6&tradable=1&craftable=1&australium=-1&killstreak_tier=0)
* [1.6 USD in cash](https://marketplace.tf/items/tf2/5021;6) (also referred to as Paypal in the project)
* [2.15 USD in Steam funds](https://steamcommunity.com/market/listings/440/Mann%20Co.%20Supply%20Crate%20Key)

### Cash
Cash is what it sounds like, real-life money. In this project, cash is referred to as Paypal, since money transactions in trading is often done using Paypal. The price of keys in cash typically fluctuates between [1.6-2 Dollars](https://marketplace.tf/items/tf2/5021;6) per key (varying depending on the platform or marketplace).

### Steam Funds
Valve have their own marketplace for selling TF2 items and other items on Steam, known as the [Steam Community Market](https://steamcommunity.com/market/) (SCM). Here, users can buy and sell items, for a 15% sellers fee.  
Steam funds can only be utilized within the Steam Community Market or the Steam store itself. Therefore, Steam funds doesn't hold as much value as real cash, and items on the SCM is often more expensive compared to purchasing them with cash directly. For instance, TF2 Keys cost around 2.15 USD on the SCM, compared to around 1.6 if bought directly with cash. If one were to attempt converting Steam funds into cash, by purchasing a TF2 Key for 2.15 and then selling it for cash, they would end up with around 1.6 USD, in this case Steam funds is worth around 25% less than real cash.


## Purpose of The Project
This project was developed to simplify the process of tracking trades and profits in TF2 trading. 
The main goal is to provide an easy way to get an overview of trades and profits made from TF2 trading. It can be challenging to keep track of what you sold an item for, what you received from a trade, and what the potential profit made could be, especially when TF2 items are often traded for other items rather than selling it for a currency.

### Trade Tracking
<details>
    <summary>Here's an example of how one item sold can lead to receiveing multiple other items</summary>
    <img src="https://gyazo.com/a0ba260c25650399fb5c0c916f746fd3.png" alt="Item selling for other items">
</details>  
<br>
Imagine selling an item, but not remembering how you aquired it. With this application, you can access any trades involving that item by simply clicking on it. 
Tracing the item's trade history not only reveals its origin and the trades it has been involved in, but also helps you discover the origin of the previous item in the chain. So, if you're curious about where the item originated from and perhaps where those items also came from, you can follow the trail to reach the origin item.

<details>
    <summary>Example of following the item trade history trail</summary>
    <img src="https://gyazo.com/5eccbcf03b32e311af25a9060a891afd.gif" alt="Following item trade history trail">
</details>  
<br>

### Profit Calculations
The application can also calculate profits even when different currencies and transaction methods are used. This is particularly useful when dealing with transactions in various currencies and transaction methods. Here are two simple examples: 

<details>
    <summary>Example of item bought for EUR steam funds and sold for keys</summary>
    <img src="https://gyazo.com/0874818e7bf6793ebe658f97d02f7425.png" alt="Profit calculation example">
</details>

<details>
    <summary>Example of item bought for the same amount in the same currency, but in diffrent transaction methods (SCM funds and cash)</summary>
    <img src="https://gyazo.com/b88ec755a3f07960e1c4bfa1d8474085.png" alt="Profit calculation example">
</details>  
<br>

### Currency and Transaction Method Conversions
In the last example, we can see the transactions are done in the same currencies and for the same amount. However, because Steam Community Market funds and cash do not hold the same value, as explained earlier under `Different Currencies`, we still end up with a profit of about 1.23 Keys, equivalent to around 2 dollars.


## Distinctiveness and Complexity

TF2Folio stands out from the other projects in the course due to its unique focus on Team Fortress 2 item trading. Some of the projects distinctive componments are:

### Item Registation
 * TF2Folio includes Forms for generating TF2 items, with many various qualities to them. It can generate a image for these items if avaible using an API.
<details>
  <summary>Click to view example</summary>
  <img src="https://i.gyazo.com/20a235bc98934c3a9ef289601aec74b9.gif" alt="Dynamic Trade Display">
</details>  

### Interactive Trade Registration
 The application features a highly interactive and complex trade registration page. Key features include:

**Dynamic Trade Display:** 
* Trade display showing what items are being traded.
* Transaction method details, including image, amount, and if applicable, currency.
* If 'TF2 Items' is selected as transaction method, the transaction method details are hidden.
* Selection menu for adding items with dynamic updates.

<details>
    <summary>Click to view example</summary>
    <img src="https://gyazo.com/86f4316ba2a04ae12ad22d61c0fe7670.gif" alt="Dynamic Trade Display">
</details>
<br>

**Dynamic Trade Register Form:**
* Select Sale/Purchase transaction type, and dynamically update the trade display to show the changes
* Form dynamically adjusts based on the selected transaction method.
* Default currency aligns with user's market settings.
* If any errors occur when submitting the form, they will be displayed on the page.

<details>
    <summary>Click to view example</summary>
    <img src="https://gyazo.com/9dc81c84bbe4a3dcda02f154864b3224.gif" alt="Dynamic Trade Register Form">
</details>  


### Trade Profit Calculation

 The project includes a page to view information of all registered trades. Trades can display profit if applicabble. One of the most complex aspects of the project is how profit is calculated. 
 To calculate the profit for an item, the following guidelines apply:

 * **Source Trade Identification:** Trades involving the sale of an item previously purchased for pure (Cash or TF2 Keys) are categorized as 'source trades' within the project's database and codebase.

* **Recursive Item Sales:** All items received from the source trade must be sold, including items received from selling these received items. This recursive process ensures that the profit calculation considers all items involved in the trade chain.

* **Normalization of Transaction Methods:** Since there is several transaction methods (TF2 keys, Steam funds, Paypal funds / Normal cash), the project must normalize these values into one unified currency before calculating profit. For example, if an item is sold for $10 via PayPal but was originally purchased for 4 TF2 Keys, the system first converts the sale price to TF2 Keys before calculating the profit in keys. The default transaction method is always the sale price method.

* **Profit Calculation:** Once all items from the source trade and its subsequent transactions are sold, the profit is calculated by subtracting the purchase price of the item sold in the source trade, from its sale price. 

<details>
    <summary>Here is a simplified visual example of this process</summary>
    <a href="tf2folio/static/tf2folio/images/profit calculation example.png" target="_blank">
        <img src="tf2folio/static/tf2folio/images/profit calculation example.png" alt="Profit Calculation Example">
    </a>
        <details>
            <summary>Image text</summary>
            <ol>
                <li>Item is bought for 25 keys</li>
                <li>Item is sold for 3 items and 15 keys; this trade is now the source trade.</li>
                <li>All items received from the source trade are sold, each for different transaction methods.</li>
                <li>If any received item is sold for another item, the new item must also be sold before calculating profit.</li>
                <li>Upon selling an item for pure (cash or keys), the sale price is added to the item. Additionally, the sale value of this item is added to the sale price of the third item.</li>
                <li>Once all received items have a sale price, it combines all the values together, including the trade transaction value (15 Keys). If the values involve different transaction methods, they are converted to keys before combining them together.</li>
                <li>Now it can add the combined sale price to the sold item. If the sold item also has a purchase price, the transaction method is normalized, and the profit is calculated. The calculated profit is saved to the item and displayed on the trade.</li>
            </ol>
        </details>
</details> 


## Files & Directories

### Project Root Directory

- `.github/workflows/`: Contains the 'django.yml' GitHub Actions workflow file. This workflow automate running docker and tests on push.
- `capstone/`: Django app for project-wide settings and configurations. Contains files like settings.py and urls.py.

- `tf2folio/`: Main application directory.
    - `data/`: Directory containing JSON files.
        - `particle_effects_mapping.json`: JSON file including all particle effects IDs and names as key-value pairs.
        - `war_paints.json`: JSON file containing a list of all war paints in Team Fortress 2.
        - `weapon_skin.json`: JSON file containing a list of all weapon skins in Team Fortress 2.
    - `static/tf2folio/`: Directory for static files for tf2folio-
        - `images/`: Directory containing Images used in the app.
        - `particles/`: Directory containing images of all the unusual particle effects in Team Fortress 2, with the ID at the beginning of the file names.
        - `new-item.js`: JavaScript file containing functionality for the 'new item' form page, used in 'new-item.html'.
        - `new-trade.js`: JavaScript file containing functionality for the 'new trade' page, used in 'new-trade.html'.
        - `styles.scss`: SCSS file containing styling for the app.
        - `trade-history.js` JavaScript file containing functionality for the trade history page, used in 'trade-history.html'.
    - `templates/tf2folio/`: Directory containing HTML templates for the TF2folio application. Templates include Django forms and template scripting.
    - `templatetags/` Directory containing custom template tags and filters for tf2folio.
        - `trade_history_filter.py` Python file containing template tags and filters used in 'trade-template.html' and 'transaction-method-template.html'.
    - `forms.py`: Contains all application forms.
    - `models.py`: Defines application models and related functions.
    - `tests.py`: Contains automated tests executed on each push.
    - `urls.py`: Contains all URL paths for the tf2folio application.
    - `utils.py`: Defines utility functions, primarily used to support functionality in views.py.
    - `views.py`: Contains all view functions for handling requests and responses.
- `gitignore`: Ignored files for git.
- `docker-compose.yml`: YAML file defining services for Docker containers. Configures a PostgreSQL database service (db) and a web service (web) for the application.
- `Dockerfile`: Defines instructions for building a Docker image for the application.
- `requirements.txt`: A text file with the Python packages required to run the application.


## Database Structure
The application utilizes five Django models for the database structure, each serving a specific function in managing user data, item information, transactions and values. These models are:

### User
The `User` model is a custom model that extends Django's built-in `AbstractUser` model. This model is used to store user data, including the user's items and transactions.

**Fields**

- `items`: A many-to-many relationship field linking users to their owned items. This field stores the items owned by each user.  
- `transactions`: A many-to-many relationship field linking users to their transactions. This field stores the transactions associated with each user.

### UserMarketSettings
`UserMarketSettings` is a model for storing a user's market settings, such as key prices and default currencies. 

**Fields**
- `user`: One-to-One relationship field with the user that `UserMarketSettings``belongs to.
- `default_scm_currency`: The user's default currency for Steam Community Market transactions. Default value is EUR.
- `default_paypal_currency`: The user's default currency for Paypal or cash transactions. Default value is USD.
- `scm_key_price_dollars`: The user's price of keys on the Steam Community Market in dollars. Default value is 2.15.
- `paypal_key_price_dollars`: The user's price of keys in USD. Default value is 1.7

### Item
The `Item` model stores an item along with its various qualities and attributes. It also tracks the item's purchase price, sale price, and profit value.

**Fields**
- `owner`: ForeignKey that links the `Item` to its owner.
- `item_name`: Name of the Item itself, excluding qualities and attributes.
- `item_title`: Display title of the item. Includes all relevant qualities and attributes.
- `quality`: Quality of the item. All nine quality options are in the `Item` model.
- `craftable`: Boolean field indicating whether the item is craftable. Default value is True.
- `australium`: Boolean field indicating whether the item is Australium. Default value is False.
- `texture_name`: Name of the items warpaint or skin texture.
- `wear`: Wear of the item. All five wear options are in the `Item` model.
- `particle_effect`: Particle effect or 'Unusual Effect' of the item.
- `particle_id`: Particle ID of the `particle_effect`.
- `killstreak`: Killstreak tier of the item . All three killstreak tier choices are in the `Ìtem` model.
- `sold`: Boolean field indicating whether the item has been sold. Default value is False.
- `image_url`: URL field for the image URL of the item.
- `purchase_price`: One-to-One field of a `Value` object representing the item's purchase price.
- `sale_price`: One-to-One field of a `Value` object representing the item's sale price.
- `profit_value`: One-to-One field of a `Value` object representing how much profit was made by buying and selling the item.

### Value
The `Value` model is used to store the value of an item or a transaction. For items, it can store the item's purchase price, sale price and profit made. For transactions, it can store how much 'pure' (cash or keys) was in the trade.

**Fields**
- `item`: ForeginKey that links the `Value` to an item.
- `transaction`: ForeginKey that links the `Value` to a transaction.
- `transaction_method`: The transaction method used, either 'keys', 'scm_funds' or 'paypal' (cash).
- `currency`: Stores the currency code. Empty if `transaction_method` is keys.
- `amount`: The amount.

### Transacion
The `Transaction` model stores data about transactions logged by users themselves. It keeps track of the items sold and received in each trade, along with the amount of value (in keys or cash) involved.

**Fields**
- `owner`: ForeignKey linking the `Transaction` to the user who logged the transaction.
- `transaction_value`: One-to-One field of a `Value` object representing the amount of keys or cash involved in the transaction.
- `transaction_type`: Indicates whether the transaction was a sale or a purchase.
- `items_sold`: Many-to-many field containing all items sold in the transaction.
- `items_bought`: Many-to-many field containing all items received in the transaction.
- `description`: Description of the transaction, if provided. This description can be viewed in the trade display.
- `date`: The date when the transaction was logged.
- `source_trade`: Boolean field indicating if the trade was a source trade. Source trades involve the sale of an item previously purchased for pure (Cash or TF2 Keys), enabling the calculation of profit on the item sold within this transaction.


## How to Run the Application

### Prerequisites

Before you begin, make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Installation with docker

1. Clone the repository: `git clone https://github.com/HenrikTS99/CS50-Web-final-project.git`
2. Navigate to the project directory: `cd CS50-Web-final-project`
3. Build and run the Docker image: `docker compose up -d`
4. Access the application in your web browser at `localhost:8000` or [`127.0.0.1:8000`](http://127.0.0.1:8000)

### How to create a superuser

1. Find the docker container (web container) ID by running `docker ps`
2. Run this command when docker is up: `docker exec -it <container_id> python manage.py createsuperuser`


## API's used

[**Steam Image API**](https://steamapis.com/docs/images#item): This API is used in the project to get item images. the API uses item images from Steam Community Market, therefore the API cannot generate images for items that cannot be sold on Steam Community Market.

[**Steam Market API**](https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid=1): This API is utilized to get the current cheapest sell order for Keys from the Steam Community Market in USD. The return value is cached to avoid being rate limited.


[**Exchange Rate API**](https://www.exchangerate-api.com/): This API is utilized in the project to convert one currency to another.
Example: `https://api.exchangerate-api.com/v4/latest/{to_currency}`, where `{to_currency}` is the currency we want to convert to. 
The API returns a JSON object containing exchange rates for all currencies relative to `{to_currency}`. To access a specific currency in the JSON object, we can do `data['rates'][from_currency]`.
