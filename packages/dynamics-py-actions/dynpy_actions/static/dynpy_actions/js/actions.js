//Action load event
const actionLoad = new Event("actionLoad", { bubbles: true });

$(document).ready(function () {
  //Load the action's forms asynchronously.
  setupActions();
  setFormsValidationHandler();
  openModalOnPageLoad();
});

const setupActions = (elem = document) => {
  const actionsLoaders = elem.querySelectorAll(`[data-js-load-action-form]`);

  const setupActionFunction = {
    target: setupTargetAction,
    inline: setupInlineAction,
    modal: setupModalAction,
  };

  actionsLoaders.forEach((actionLoader) => {
    let actionType = actionLoader.dataset.actionType;
    let actionDataset;
    let formWrapper;

    // Target data attrs live on the loader not the form wrapper
    if (actionType == "target") {
      actionDataset = { ...actionLoader.dataset };
      formWrapper = document.getElementById(
        `${actionDataset.action_action__target_elem_id}`
      );
    } else {
      const actionId = actionLoader.dataset.actionId;
      formWrapper = document.getElementById(`actions_wrapper_${actionId}`);
      actionDataset = { ...formWrapper.dataset };
      actionType = actionDataset.actionType;
    }

    const action = {
      actionType: actionType, // type of action i.e. 'Modal','Inline' etc.
      actionLoader: actionLoader, // the button that loads the form
      actionDataset: actionDataset, // data attributes on the action
      formWrapper: formWrapper, // placeholder where the form will be rendered
      setupActionFn: setupActionFunction[actionType],
    };

    action.setupActionFn(action);
  });
};

/* ------------------ Setup functions for each action type ------------------ */
function setupTargetAction(action) {
  // Set the display to none for the target (needed so slideDown() will work)
  action.formWrapper.style.display = "none";
  // Set other attrs needed
  action.actionLoader.style.cursor = "pointer";
  action.formWrapper.classList.add("action-wrapper");
  action.formWrapper.setAttribute(
    "data-action_action__name",
    action.actionDataset.action_action__name
  );

  action.actionLoader.addEventListener(
    action.actionDataset.action_action__target_trigger_on,
    () => {
      renderTargetForm(action);
    }
  );
}
function setupModalAction(action) {
  action.modalTargetManager = ModalTargetManager(action);
  action.actionLoader.addEventListener(
    "click",
    () => {
      if (action.modalTargetManager.modalTarget) {
        action.modalTargetManager.setModalSize();
        action.modalTargetManager.setModalTitle();
        action.modalTargetManager.setFormWrapper();
        action.formWrapper = action.modalTargetManager.getFormWrapper();
      }

      renderModalAndInlineForms(action);
    },
    action.modalTargetManager.modalTarget ? {} : { once: true }
  );
  action.formWrapper.addEventListener("actionLoad", (e) => {
    $(action.formWrapper.closest(".modal")).on("shown.bs.modal", function (e) {
      const visibleformElements = Array.from(
        e.target.querySelector("form").elements
      ).filter(
        (elem) =>
          window.getComputedStyle(elem).getPropertyValue("display") !== "none"
      );
      visibleformElements[0].focus();
    });
  });
}
function setupInlineAction(action) {
  renderModalAndInlineForms(action);
}
/* --------------------------- End setup functions -------------------------- */

/* --------------------------- Render Target forms -------------------------- */
const renderTargetForm = (action) => {
  const $formWrapper = $(action.formWrapper);

  // If no target on the page, raise error.
  if (!action.formWrapper) {
    console.error(
      `ACTION ERROR: Action Name - ${action.actionDataset.action_action__name}. Unable to render form for target id of ${action.actionDataset.action_action__target_elem_id}. Make sure there is an element with that id on the page.`
    );
    return;
  }
  getLoader(action);
  fetchHtml(action);
  $formWrapper.slideDown();
};

/* ---------------------- Render Modal and Inline forms --------------------- */

const renderModalAndInlineForms = (action) => {
  getLoader(action);
  fetchHtml(action);
};

/* ---------------------------- Helper Functions ---------------------------- */

const fetchHtml = (action) => {
  // Fetches the html of the form using an ajax call
  const url = getUrl(action.actionDataset);
  fetch(url)
    .then((response) => {
      if (!response.ok) throw new Error();
      return response.text();
    })
    .then((data) => {
      action.formWrapper.innerHTML = data;
      reloadWindowOnload(action.formWrapper);
    })
    .catch((err) => {
      const errorMessageAttribute = action.actionDataset["errorMessage"];
      const customErrorMessage =
        errorMessageAttribute && errorMessageAttribute.value;
      action.formWrapper.innerHTML = getLoadingErrorInstance(
        customErrorMessage
      );
      console.error(err);
    });
};
const getUrl = (actionDataset) => {
  // Builds the url for the ajax call.
  dataAttributesDict = {};
  for (let key in actionDataset) {
    if (key.startsWith("action_")) {
      dataAttributesDict[key] = actionDataset[key];
    }
  }
  const url = new URL(window.location);
  url.search = new URLSearchParams(dataAttributesDict);
  return url;
};
const getLoader = (action) => {
  // Gets the loader that is displayed while the html is being fetched
  const loaderStyle = action.actionDataset["loaderStyle"]
    ? action.actionDataset["loaderStyle"]
    : "spinner";
  const loadingMessageAttribute = action.actionDataset["loadingMessage"];
  const customLoadingMessage =
    loadingMessageAttribute && loadingMessageAttribute.value;

  action.formWrapper.innerHTML = getLoaderInstance(
    loaderStyle,
    customLoadingMessage
  );
};

/* -------------------------- End Helper Functions -------------------------- */

const reloadWindowOnload = (wrapper) => {
  // Call this function on load of an action.

  // bootstrap-ify the tooltips for forms loaded asynchronously
  $(wrapper).find('[data-toggle="tooltip"]').tooltip();

  const form = wrapper.querySelector("form");
  scripts = form.querySelectorAll("script");
  // Run scripts
  form.querySelectorAll("script").forEach((script) => {
    if (!script.src) new Function(script.text)();
    else {
      fetch(script.src).then((response) => {
        return response.text().then((text) => {
          new Function(text)();
        });
      });
    }
  });
  setFormOnchangeHandlers(form);
  setFormSubmissionHandlers(form);
  setFormValidationHandler(form);

  wrapper.dispatchEvent(actionLoad);
};

const openModalOnPageLoad = () => {
  let queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const hash = decodeURIComponent(urlParams.get("action_hash"));
  if (hash) {
    const action = document.querySelector(
      `[data-action_action__hash='${hash}'][data-action-type='modal']`
    );
    if (action) {
      action.closest(".modal").previousElementSibling.click();
    }
    // After loads the modal remove action_hash from the url
    urlParams.delete("action_hash");
    const url = new URL(window.location);
    url.search = urlParams;
    history.replaceState({}, "", url);
  }
};
const ModalTargetManager = (action) => {
  const modalTarget = document.getElementById(
    action.actionDataset.action_action__modal_target
  );
  let modalBody;
  if (modalTarget) {
    modalBody = modalTarget.querySelector(".modal-body");
  }
  const getFormWrapper = () => {
    const formWrapper = modalBody.querySelector("div");
    return formWrapper;
  };
  const setFormWrapper = () => {
    modalBody.innerHTML = action.formWrapper.outerHTML;
  };
  const setModalTitle = () => {
    const modalTitle = modalTarget.querySelector(".modal-title");

    modalTitle.innerHTML = decodeURIComponent(
      action.actionDataset.action_action__modal_title
    );
  };
  const setModalSize = () => {
    const modalDialog = modalTarget.querySelector(".modal-dialog");
    modalDialog.classList.remove("modal-sm", "modal-lg", "modal-xl");
    if (action.actionDataset.action_action__modal_size) {
      modalDialog.classList.add(action.actionDataset.action_action__modal_size);
    }
  };
  return {
    modalTarget: modalTarget,
    getFormWrapper: getFormWrapper,
    setFormWrapper: setFormWrapper,
    setModalTitle: setModalTitle,
    setModalSize: setModalSize,
  };
};
