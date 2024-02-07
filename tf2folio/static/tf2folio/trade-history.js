document.addEventListener('DOMContentLoaded', function() {
    const sourceCheckBox = document.querySelector('#show-source-trades-checkbox');
    const notesCheckboxes = document.querySelectorAll('.notes-toggle');
    const tradeNotes = document.querySelectorAll('.trade-notes');

    sourceCheckBox.addEventListener('change', () => toggleSourceTradeDisplay(sourceCheckBox));

    notesCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            toggleNotes(checkbox.dataset.tradeId);
        }
    )});

    tradeNotes.forEach(tradeNote => {
        tradeNote.addEventListener('click', () => {
            toggleNotes(tradeNote.dataset.tradeId);
            const checkbox = document.getElementById(`notes-toggle-${tradeNote.dataset.tradeId}`);
            checkbox.checked = !checkbox.checked;
        }
    )});

    setSourceTradeCheck(sourceCheckBox);
});


function toggleNotes(tradeId) {
    const notes = document.getElementById(`trade-notes-${tradeId}`);
    notes.classList.toggle('expanded');
}


function toggleSourceTradeDisplay(checkBox) {
    const newUrl = new URL(window.location.href);
    if (checkBox.checked) {
        newUrl.searchParams.set('source_trades', checkBox.checked);
    } else {
        newUrl.searchParams.delete('source_trades');
    }
    window.location.href = newUrl.toString();
}


// Set the source trade checkbox to the correct state based on the URL
function setSourceTradeCheck(checkBox) {
    const urlParams = new URLSearchParams(window.location.search);
    const SourceTradesBool = urlParams.get('source_trades') === 'true';
    checkBox.checked = SourceTradesBool;
}
