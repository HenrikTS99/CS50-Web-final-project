document.addEventListener("DOMContentLoaded", function () {
  const sourceCheckBox = document.querySelector("#show-source-trades-checkbox");
  const notesCheckboxes = document.querySelectorAll(".notes-toggle");
  const tradeNotes = document.querySelectorAll(".trade-notes");

  if (sourceCheckBox) {
    sourceCheckBox.addEventListener("change", () =>
      toggleSourceTradeDisplay(sourceCheckBox)
    );
    setSourceTradeCheck(sourceCheckBox);
  }

  if (tradeNotes.length > 0) {
    notesCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        toggleNotes(checkbox.dataset.tradeId);
      });
    });
  }

  tradeNotes.forEach((tradeNote) => {
    tradeNote.addEventListener("click", () => {
      toggleNotes(tradeNote.dataset.tradeId);
      // Simulate the checkbox click to keep the checkbox state in sync with the notes display.
      const checkbox = document.getElementById(
        `notes-toggle-${tradeNote.dataset.tradeId}`
      );
      checkbox.checked = !checkbox.checked;
    });
  });
});

// Toggles the display of notes for a given trade.
function toggleNotes(tradeId) {
  const notes = document.getElementById(`trade-notes-${tradeId}`);
  notes.classList.toggle("expanded");
}

/**
 * Toggle the source trade display based on the checkbox state.
 * Redirects to the same page with the source_trades query parameter set to the checkbox state.
 */
function toggleSourceTradeDisplay(checkBox) {
  const newUrl = new URL(window.location.href);
  if (checkBox.checked) {
    newUrl.searchParams.set("source_trades", checkBox.checked);
    newUrl.pathname = '/trade_history'; // Set the path to the base URL
  } else {
    newUrl.searchParams.delete("source_trades");
  }
  window.location.href = newUrl.toString();
}

// Set the source trade checkbox to the correct state based on the URL.
function setSourceTradeCheck(checkBox) {
  const urlParams = new URLSearchParams(window.location.search);
  const SourceTradesBool = urlParams.get("source_trades") === "true";
  checkBox.checked = SourceTradesBool;
}
