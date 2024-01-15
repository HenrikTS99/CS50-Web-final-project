
function toggleSourceTradeDisplay() {
    const checkBox = document.querySelector('#show-source-trades-checkbox');
    var trades = document.getElementsByClassName('trade');
    for (var i = 0; i < trades.length; i++) {
        if (checkBox.checked & trades[i].getAttribute('data-source-trade') == 'False') {

            trades[i].style.display = "none";
        } else {
            trades[i].style.display = "block";
        }
    }
}