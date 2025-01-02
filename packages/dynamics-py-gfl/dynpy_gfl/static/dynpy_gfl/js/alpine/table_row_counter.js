document.addEventListener("alpine:init", () => {
  Alpine.store("tableRowCounter", {
    total: 0,
    updateRowCount() {
      this.total = Array.from(
        document.querySelectorAll("#gfl_table tbody tr")
      ).length;
    },
    observeTableRows() {
      const observer = new MutationObserver((mutations) => {
        this.updateRowCount();
        mutations.forEach((mutation) => {
          if (
            mutation.type === "childList" &&
            mutation.removedNodes.length > 0
          ) {
            mutation.removedNodes.forEach((node) => {
              if (node.nodeName === "TR") {
                window.dispatchEvent(new CustomEvent("table-row-removed"));
              }
            });
          }
        });
      });

      observer.observe(document.querySelector("#gfl_table_wrapper"), {
        childList: true,
        subtree: true,
      });
    },
  });
});

function initTableRowCounter() {
  Alpine.store("tableRowCounter").updateRowCount();
  Alpine.store("tableRowCounter").observeTableRows();
}
