document.addEventListener('DOMContentLoaded', function() {
    const checkBox = document.querySelector('#show-source-trades-checkbox');
    checkBox.addEventListener('change', toggleSourceTradeDisplay);
    setSourceTradeCheck() 
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

function toggleNotes(tradeId) {
    const notes = document.getElementById(`trade-notes-${tradeId}`);
    notes.classList.toggle('expanded');
}

// Set the source trade checkbox to the correct state based on the URL
function setSourceTradeCheck() {
    const urlParams = new URLSearchParams(window.location.search);
    const SourceTradesBool = urlParams.get('source_trades') === 'true';
    document.querySelector('#show-source-trades-checkbox').checked = SourceTradesBool;
}
