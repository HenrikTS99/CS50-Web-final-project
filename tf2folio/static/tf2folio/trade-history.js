document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const SourceTradesBool = urlParams.get('source_trades') === 'true';
    document.querySelector('#show-source-trades-checkbox').checked = SourceTradesBool;
});

function toggleSourceTradeDisplay() {
    const checkBox = document.querySelector('#show-source-trades-checkbox');
    var newUrl = new URL(window.location.href);
    if (checkBox.checked) {
        newUrl.searchParams.set('source_trades', checkBox.checked);
    } else {
        newUrl.searchParams.delete('source_trades');
    }
    window.location.href = newUrl.toString();
}

