document.addEventListener("alpine:init", () => {
	Alpine.store("tableRowCounter", {
		total: 0,
		updateRowCount() {
			this.total = Array.from(document.querySelectorAll(".js-gfl-item")).length;
		},
		observeTableRows() {
			const observer = new MutationObserver((mutations) => {
				this.updateRowCount();
				for (const mutation of mutations) {
					if (
						mutation.type === "childList" &&
						mutation.removedNodes.length > 0
					) {
						for (const node of mutation.removedNodes) {
							const nodeId = node.id;
							const wasReplaced = !!document.getElementById(nodeId);
							if (
								node.classList &&
								node.classList.contains("js-gfl-item") &&
								!wasReplaced
							) {
								window.dispatchEvent(
									new CustomEvent("table-row-removed", {
										detail: { rowId: nodeId },
									}),
								);
							}
						}
					}
				}
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
