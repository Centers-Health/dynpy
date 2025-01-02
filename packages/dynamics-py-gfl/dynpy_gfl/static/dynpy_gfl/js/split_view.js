const sidePanelLoad = new Event("sidePanelLoad", { bubbles: true });

const URLManager = () => {
  // Build the url for the ajax call.

  const buildUrlForSidePanelFetch = (rowId) => {
    url.searchParams.set("split_view_obj", rowId);
    url.searchParams.append("fetch_side_panel", true);
    return url;
  };
  const replaceBrowserUrl = () => {
    /**
     * Need to update the url in the browser to have the
     * split_view_obj param.
     * Remove the 'fetch_side_panel' so that when page refreshes
     * it won't fetch the side panel.
     * Remove 'close_side_panel' so that when the page refreshes the panel
     *is open.
     */
    url.searchParams.delete("fetch_side_panel");
    url.searchParams.delete("close_side_panel");

    history.replaceState({}, "", url);
  };
  const addIsClosedToUrl = () => {
    url.searchParams.set("close_side_panel", true);
    history.replaceState({}, "", url);
  };
  return {
    url: url,
    replaceBrowserUrl: replaceBrowserUrl,
    addCloseSidePanelToUrl: addIsClosedToUrl,
    buildUrlForSidePanelFetch: buildUrlForSidePanelFetch,
  };
};

const RowManager = (row) => {
  const id = row.getAttribute("id").replace("gfl_row_", "");
  const templateId = `side_panel_template_${id}`;

  const createTemplateElement = (html) => {
    const template = document.createElement("template");
    template.id = templateId;
    template.innerHTML = html;
    document.body.appendChild(template);
    return template;
  };

  const getTemplate = () => {
    const template = document.getElementById(templateId);
    return template;
  };
  const highlightRow = () => {
    row.classList.add("row-active");
  };
  return {
    id: id,
    templateIsInDOM: document.getElementById(templateId) != null,
    getTemplate: getTemplate,
    createTemplateElement: createTemplateElement,
    highlightRow: highlightRow,
  };
};

const SidePanelManager = () => {
  const sidePanel = document.getElementById("side_panel");
  const sidePanelWrapper = document.getElementById("side_panel_wrapper");
  const table = document.getElementById("gfl_table_wrapper");
  const resizer = document.getElementById("table_panel_divider");
  const urlManager = URLManager();
  const DEFAULT_SIDE_PANEL_TEXT = "Select a row to view / edit details";
  const ITEM_NOT_IN_LIST_TEXT =
    "The previously selected row is no longer in the list";

  const closePanel = () => {
    sidePanelWrapper.classList.add("d-none");
    resizer.classList.add("d-none");
    table.style.setProperty("--table-width", "100%");
    urlManager.addCloseSidePanelToUrl();
    setCloseSidePanelFilterValue();
  };

  const setCloseBtnHandler = () => {
    const closeBtn = document.getElementById("close_panel_btn");
    if (closeBtn) {
      closeBtn.addEventListener("click", closePanel);
    }
  };

  // Close the side panel if the user presses the escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closePanel();
    }
  });

  const setSplitViewObjectFilterValue = (id) => {
    /**
     * Set input value in the filter form so that when
     * the page is filtered it will populate the side
     * panel.
     */
    const input = document.getElementById("split_view_obj");
    input.setAttribute("value", id);
  };
  const setCloseSidePanelFilterValue = () => {
    const input = document.getElementById("close_side_panel");
    const close_side_panel = urlManager.url.searchParams.get(
      "close_side_panel"
    );
    input.setAttribute("value", close_side_panel);
  };
  const reinitializeTooltips = () => {
    $('[data-toggle="tooltip"]').tooltip();
  };

  const runScripts = () => {
    scripts = sidePanelWrapper.querySelectorAll("script");
    // Run scripts
    sidePanelWrapper.querySelectorAll("script").forEach((script) => {
      if (!script.src) new Function(script.text)();
      else {
        fetch(script.src).then((response) => {
          return response.text().then((text) => {
            new Function(text)();
          });
        });
      }
    });
  };

  const showTemplateInSidePanel = (template) => {
    sidePanel.innerHTML = "";
    sidePanel.appendChild(template.content.cloneNode(true));
  };

  const setTableWidth = () => {
    userPreferences = JSON.parse(localStorage.getItem("user-preferences"));
    const tableWidth = userPreferences?.tableWidth
      ? userPreferences.tableWidth
      : 70;
    const sidePanelWidth = 100 - tableWidth;
    table.style.setProperty("--table-width", `${tableWidth}%`);
    sidePanelWrapper.style.setProperty(
      "--side-panel-width",
      `${sidePanelWidth}%`
    );
  };

  const showSidePanel = () => {
    sidePanelWrapper.classList.remove("d-none");
    resizer.classList.remove("d-none");
    setTableWidth();
    setCloseSidePanelFilterValue();
  };

  const processSidePanel = (template, openSidePanel) => {
    if (openSidePanel) showSidePanel();
    showTemplateInSidePanel(template);
    runScripts();
    setCloseBtnHandler();
    reinitializeTooltips();
    // fire this event here since process is called both in the fetch and in refresh
    sidePanel.dispatchEvent(sidePanelLoad);
  };

  const getSidePanelLoaderTemplate = () => {
    // Gets the loader that is displayed while the html is being fetched
    const loaderStyle = "spinner";
    sidePanel.innerHTML = getLoaderInstance(loaderStyle);
  };

  const fetchSidePanel = (url, rowManger, openSidePanel) => {
    fetch(url)
      .then((response) => {
        if (!response.ok) throw new Error();
        return response.text();
      })
      .then((data) => {
        processSidePanel(rowManger.createTemplateElement(data), openSidePanel);
        return data;
      })
      .catch((err) => {
        sidePanel.innerHTML = getLoadingErrorInstance();
        console.error(err);
      });
  };
  const refreshState = (
    row,
    ignoreCache = false,
    sidePanelShouldOpen = true
  ) => {
    const rowManger = RowManager(row);
    const url = urlManager.buildUrlForSidePanelFetch(rowManger.id);
    const sidePanel = document.getElementById("side_panel_wrapper");
    const sidePanelWasClosed = sidePanel.classList.contains("d-none");
    const openSidePanel = sidePanelShouldOpen || !sidePanelWasClosed;

    if (rowManger.templateIsInDOM && !ignoreCache) {
      processSidePanel(rowManger.getTemplate(), openSidePanel);
    } else {
      getSidePanelLoaderTemplate();
      fetchSidePanel(url, rowManger, openSidePanel);
    }
    rowManger.highlightRow();
    urlManager.replaceBrowserUrl();
    setSplitViewObjectFilterValue(rowManger.id);
  };
  const initialize = () => {
    setCloseBtnHandler();
    if (urlManager.url.searchParams.get("close_side_panel") == "true") {
      closePanel();
    }

    if (sidePanel && !sidePanelWrapper.classList.contains("d-none")) {
      setTableWidth();
      const rowInUrl = "gfl_row_" + url.searchParams.get("split_view_obj");
      const rows = document.querySelectorAll(".split-view-row");
      let rowInTable;
      rows.forEach((row) => {
        if (row.id === rowInUrl) {
          rowInTable = row;
        }
      });
      if (rowInTable) {
        refreshState(rowInTable);
      } else {
        sidePanel.innerHTML = `
                  <div class="text-center my-5">
          ${
            rowInUrl
              ? `<p class="alert alert-danger h5">${ITEM_NOT_IN_LIST_TEXT}</p>`
              : ""
          }
                      <p class="h4">${DEFAULT_SIDE_PANEL_TEXT}</p>
                  </div>
                  `;
      }
    }
  };
  return {
    initialize: initialize,
    refreshState: refreshState,
  };
};
const unhighlightAllRows = () => {
  const rows = document.querySelectorAll(".split-view-row");
  rows.forEach((row) => {
    row.classList.remove("row-active");
  });
};

const setupSplitView = () => {
  const sidePanelManager = SidePanelManager();
  sidePanelManager.initialize();
  const rows = document.querySelectorAll(".split-view-row");
  const shouldIgnoreCache = document
    .getElementById("ignore_side_panel_cache_value")
    .hasAttribute("ignore");
  rows.forEach((row) => {
    row.addEventListener("click", (e) => {
      // Allow clickable elements in spit view rows that will not open the side panel
      const optOutElem = e.target.closest(".js-side-panel-opt-out");
      let sidePanelShouldOpen = true;
      if (optOutElem) {
        sidePanelShouldOpen = false;
      }
      unhighlightAllRows();

      sidePanelManager.refreshState(
        row,
        shouldIgnoreCache,
        sidePanelShouldOpen
      );
    });
  });
};

const tablePanelResizeManager = () => {
  const tablePanelDivider = document.getElementById("table_panel_divider");
  const table = document.getElementById("gfl_table_wrapper");
  const sidePanel = document.getElementById("side_panel_wrapper");
  const body = document.querySelector("body");

  let cursorPosition = 0;
  let tableWidth = 0;

  // Handle the mousedown event that's triggered when user drags the divider
  const resizingStartedHandler = function (e) {
    body.classList.add("resizing");
    table.style.setProperty("transition", "none");
    // Get the current mouse position
    cursorPosition = e.clientX;
    tableWidth = table.getBoundingClientRect().width;

    document.addEventListener("mousemove", resizingInProgressHandler);
    document.addEventListener("mouseup", resizingFinishedHandler);
  };

  const resizingInProgressHandler = function (e) {
    e.preventDefault();
    // How far the mouse has been moved
    const amountMoved = e.clientX - cursorPosition;
    const newTableWidth =
      ((tableWidth + amountMoved) * 100) /
      tablePanelDivider.parentNode.getBoundingClientRect().width;

    const sidePanelClosed = sidePanel.classList.contains("d-none");

    // Don't allow them to make the side panel too small or too big or to resize it if it's closed
    if (10 < newTableWidth && newTableWidth < 80 && !sidePanelClosed) {
      table.style.setProperty("--table-width", `${newTableWidth}%`);
      const sidePanelWidth = 100 - newTableWidth;
      sidePanel.style.setProperty("--side-panel-width", `${sidePanelWidth}%`);
      localStorage.setItem(
        "user-preferences",
        JSON.stringify({
          tableWidth: newTableWidth,
        })
      );
    }
  };

  const resizingFinishedHandler = function () {
    body.classList.remove("resizing");
    table.style.setProperty("transition", "width .3s");
    document.removeEventListener("mousemove", resizingInProgressHandler);
    document.removeEventListener("mouseup", resizingFinishedHandler);
  };

  const initialize = () => {
    tablePanelDivider.addEventListener("mousedown", resizingStartedHandler);
  };

  return {
    initialize: initialize,
  };
};

window.addEventListener("load", () => {
  setupSplitView();
  tablePanelResizeManager().initialize();
});

nonFilterParams.push("split_view_obj", "fetch_side_panel", "close_side_panel");
