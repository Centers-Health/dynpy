/*
    How to use: see note in dynpy_cas/templates/dynpy_cas/includes/resident_global_search.html
*/

((window) => {
  ////////////////////////////////////////////////////////////////////////
  //                               UTILS                                //
  ////////////////////////////////////////////////////////////////////////
  const LIMIT = 30; // Batch size for fetching residents

  // A utility function that allows
  // using the html`...` literal tag for
  // better formatting and highlighting
  const html = (strings, ...keys) =>
    strings[0] +
    keys
      .map(
        (key, i) => (Array.isArray(key) ? key.join("") : key) + strings[i + 1]
      )
      .join("");

  const createElementFromString = (html) => {
    const template = document.createElement("template");
    template.innerHTML = html;
    return template.content.cloneNode(true);
  };

  const debounce = (fn, delay) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn(...args), delay);
    };
  };

  ////////////////////////////////////////////////////////////////////////
  //                           Global Search                            //
  ////////////////////////////////////////////////////////////////////////
  class ResidentGlobalSearch extends HTMLElement {
    constructor() {
      const template = document.createElement("template");

      template.innerHTML = html`
        <style>
          .wc-resident-global-search {
            /* root vars */
            --border-radius: 0.375rem;
            --v-padding: 3%;
          }
          .wc-resident-global-search * {
            box-sizing: border-box;
          }
          .wc-resident-global-search .highlight {
            background: yellow;
            color: black;
            font-weight: 800;
          }
          .wc-resident-global-search .wc-rgs-container {
            --width: 100%;
            --height: 100%;
            top: 0;
            left: 0;
            position: fixed;
            width: var(--width);
            height: var(--height);
            background: var(--primary);
            color: white;
            z-index: 1030;
            padding: var(--v-padding) 7%;
            transition: 0.3s all ease-in-out;
            opacity: 1;
          }
          .wc-resident-global-search .list-group-item {
            margin: 0.09rem;
            border-radius: var(--border-radius);
            margin: calc(0.5em / 2) 0.09rem;
          }
          .wc-resident-global-search .list-group-item.selected {
            /* TODO: uncomment this to enable selected row */
            /* background: #cab8e2; */
          }
          .wc-resident-global-search input {
            width: 100%;
            padding: 20px;
            font-size: 35px;
            outline: none;
            border: none;
            text-align: center;
            color: var(--dark);
            font-weight: 500;
            border-radius: var(--border-radius) var(--border-radius) 0 0;
          }
          .wc-resident-global-search .wrapper {
            margin: 10px;
          }
          .wc-resident-global-search .wc-rgs-dropdown-wrapper {
            border-radius: 0 0 var(--border-radius) var(--border-radius);
            overflow: hidden;
          }
          .wc-resident-global-search .wc-rgs-dropdown {
            min-height: 2em;
            max-height: 72vh; /* magic number */
            overflow-y: auto;
            color: initial;
            background: #eee;
            border-radius: 0 0 var(--border-radius) var(--border-radius);
            padding: 0.5em;
            padding-bottom: 2em;
          }
          .wc-resident-global-search .list-group::-webkit-scrollbar {
            width: 8px;
          }
          .wc-rgs-close-icon {
            /* The close icon */
            position: fixed;
            top: 0.5em;
            right: 0.5em;
            font-size: 3em;
            color: var(--light);
            cursor: pointer;
          }
          /* Track */
          .wc-resident-global-search .list-group::-webkit-scrollbar-track {
            box-shadow: inset 0 0 5px grey;
            padding-bottom: var(--border-radius);
          }
          /* Handle */
          .wc-resident-global-search .list-group::-webkit-scrollbar-thumb {
            background: var(--dark);
            border-radius: 10px;
          }
          /* Handle on hover */
          .wc-resident-global-search
            .list-group::-webkit-scrollbar-thumb:hover {
            background: #222;
          }
          .wc-resident-global-search .hidden {
            display: none;
            transform: scale(1.1);
            opacity: 0;
          }
          .rgs-btn {
            border: 1px solid #ccc;
          }
          .rgs-btn:hover {
            box-shadow: inset 2px 2px 5px #ccc;
          }
        </style>
        <div class="wc-resident-global-search wrapper text-left">
          <button class="px-3 btn bg-transparent text-muted openBtn rgs-btn">
            <i class="fa fa-search"></i> Jump to a Resident
          </button>
          <div class="wc-rgs-container">
            <div class="h1 text-center pb-3">Global Resident Search</div>
            <i class="fa fa-times wc-rgs-close-icon"></i>
            <input
              type="text"
              placeholder="Search a resident by first, last name, or resident number..."
            />
            <div class="wc-rgs-dropdown-wrapper">
              <ul class="wc-rgs-dropdown list-group"></ul>
            </div>
          </div>
        </div>
      `;

      // Instantiation
      super();
      this.appendChild(template.content.cloneNode(true));

      // Init State
      this.state = {
        // Internal State
        open: false,

        // Fetching state
        search: "",
        loading: false,
        results: [],
        fetchCount: 0,
        fetchStart: 0,
        canFetchMore: true,

        // App Links
        apps: [],

        //handle selected row
        selectedResult: 0,
      };

      // components
      this.input = this.querySelector("input");
      this.container = this.querySelector(".wc-rgs-container");
      this.openBtn = this.querySelector(".openBtn");
      this.dropdown = this.querySelector(".wc-rgs-dropdown");

      // Event Listeners
      this.container.addEventListener("click", () => {
        this.setState({ open: false });
        this.render();
      });
      this.input.addEventListener("input", this.handleInput);
      this.input.addEventListener("click", this.noOp);
      this.container.addEventListener("keydown", this.handleKeyPresses);
      this.dropdown.addEventListener("click", this.noOp);
      this.dropdown.addEventListener("scroll", this.handleInfiniteScroll);
      this.openBtn.addEventListener("click", this.handleButtonToggle);
      window.addEventListener("keydown", this.handleWindowKeyPresses);

      this.render();
    }

    // helper for readability
    noOp = (e) => e.stopPropagation();

    setState = (state) => {
      let newState = {};
      let tempState = typeof state === "function" ? state(this.state) : state;

      Array.isArray(tempState)
        ? (newState = [...this.state, ...tempState])
        : typeof tempState === "object"
          ? (newState = { ...this.state, ...tempState })
          : (newState = tempState);

      this.state = newState;
    };

    fetchResidentList = debounce((search) => {
      this.setState({
        fetchCount: this.state.fetchCount + 1,
        fetchStart: 0,
      });
      this.fetchAppLinks((data) => {
        this.setState({
          apps: data.data.appLinks,
        });
      });
      this.fetchResults(search, 0, (res) => {
        const queryResults = res.data.globalResidentsSearch;
        if (parseInt(queryResults.count) === this.state.fetchCount) {
          this.setState({
            loading: false,
            results: queryResults.residents,
            fetchStart: this.state.fetchStart + LIMIT,
          });
          this.render();
        }
      });
    }, 200);

    fetchMoreResidents = () => {
      this.setState({
        fetchCount: this.state.fetchCount + 1,
        canFetchMore: false,
        selectedResult: 0, // reset the selected result
      });
      this.fetchResults(this.state.search, this.state.fetchStart, (res) => {
        const queryResults = res.data.globalResidentsSearch;
        if (parseInt(queryResults.count) === this.state.fetchCount) {
          // this.setState({ results: this.state.results.push(res.residents) });
          // NOTE: don't refresh state as that will cause the whole box to rerender
          queryResults.residents.forEach((resident) =>
            this.dropdown.appendChild(
              createElementFromString(this.renderSearchItem(resident, false))
            )
          );
          this.setState({
            canFetchMore: true,
            fetchStart: this.state.fetchStart + LIMIT,
          });
        }
      });
    };

    fetchResults = (search, start, callback) => {
      const searchQuery = `
                  query GlobalResidentsSearch($searchTerm: String!, $count: Int, $pagination: OffsetPaginationInput) {
                      globalResidentsSearch(searchTerm: $searchTerm, count: $count, pagination: $pagination) {
                          count
                          residents {
                              name
                              facility {
                                  name
                                  id
                              }
                              links {
                                  name
                                  url
                              }
                              residentNumber
                              emrResidentId
                              dob
                              ssn
                              recentAdmissionDate
                          }
                      }
                  }
                `;
      const variables = {
        searchTerm: search,
        count: this.state.fetchCount,
        pagination: {
          limit: LIMIT,
          offset: start,
        },
      };
      const connector = GraphConnector();
      connector.execute(searchQuery, variables, callback);
    };

    fetchAppLinks = (callback) => {
      const searchQuery = `
                  query AppLinks {
                          appLinks{
                              url
                              permission
                              label
                              color
                              abbreviation
                          }
                      }
                  `;
      const connector = GraphConnector();
      connector.execute(searchQuery, {}, callback);
    };

    handleInput = (e) => {
      if (e.target.value.length > 0) {
        this.setState({
          loading: true,
          search: e.target.value,
          selectedResult: 0, // reset the selected result
        });
        this.fetchResidentList(this.state.search);
      } else {
        this.setState({
          results: [],
          search: e.target.value,
          loading: false,
        });
      }
      this.render();
    };

    handleKeyPresses = (e) => {
      const BKSP = "Backspace";
      const ESCP = "Escape";
      const UP = "ArrowUp";
      const DOWN = "ArrowDown";
      const key = e.key;
      const { search } = this.state;
      if ((key === BKSP && search === "") || key === ESCP) {
        e.preventDefault();
        this.handleButtonToggle(e);
      } else if (key === UP) {
        e.preventDefault();
        this.setState({
          selectedResult: Math.max(this.state.selectedResult - 1, 0),
        });
      } else if (key === DOWN) {
        e.preventDefault();
        this.setState({
          selectedResult: Math.min(
            this.state.selectedResult + 1,
            this.state.results.length - 1
          ),
        });
      }
    };

    handleWindowKeyPresses = (e) => {
      const ctrlKeyClicked = e.ctrlKey;
      const spaceKeyClicked = e.key === " ";

      if (ctrlKeyClicked && spaceKeyClicked) {
        this.handleButtonToggle(e);
      }
    };

    handleButtonToggle = (e) => {
      if (!this.state.open) {
        if (typeof plausible === "function") {
          plausible("NewOmniSearch");
        }
      }
      this.setState({ open: !this.state.open, search: "", results: [] });
      this.render();
    };

    handleInfiniteScroll = () => {
      if (
        this.dropdown.scrollTop + this.dropdown.clientHeight + 500 >=
        this.dropdown.scrollHeight &&
        this.state.canFetchMore
      ) {
        this.fetchMoreResidents();
      }
    };

    renderSearchItem = (
      {
        name,
        facility,
        links,
        residentNumber,
        emrResidentId,
        dob,
        ssn,
        recentAdmissionDate,
      },
      selected
    ) => html`
      <li class="${selected === true ? "selected" : ""} list-group-item">
        <div class="row no-gutters">
          <div class="col-12 col-md-6 col-lg-4">
            <div class="h3 text-primary">
              <i class="fa fa-user-circle" aria-hidden="true"></i>
              ${name}
            </div>
            <div>NCS Number: <b>${residentNumber}</b></div>
            <div>
              EMR ID: <b>${emrResidentId}</b>
            </div>
          </div>
          <div class="col-12 col-md-6 col-lg-3">
            <div class="h3 text-secondary">
              <i class="fa fa-building" aria-hidden="true"></i>
              ${facility.name}
            </div>
            <div>Facility Id: <b>${facility.id}</b></div>
          </div>
          <div class="col-12 col-md-6 col-lg">
            <div>DOB: <b>${dob}</b></div>
            <div class="blurred-wrapper">
              SSN: <b class="blurred-text">${ssn}</b>
            </div>
            <div>
              <span class="text-nowrap"> Admit Date: </span>
              <b>${recentAdmissionDate}</b>
            </div>
          </div>
          <div class="col-12 col-md-6 col-lg">
            ${links.map(({ url, name }) => {
      const { apps } = this.state;
      const app = apps.find((app) => app.label === name);
      return html`
                <div
                  class="app-switcher-app-small d-inline-block mb-3"
                  data-toggle="tooltip"
                  data-placement="top"
                  title="Go to ${name} profile"
                >
                  <a href="${url}">
                    <div
                      class="app-switcher-icon app-switcher-icon-small ${window.location.pathname.includes(
        url.split("?")[0]
      )
          ? "active"
          : ""}"
                      style="background:${app.color}"
                    >
                      ${app.abbreviation}
                    </div>
                  </a>
                </div>
              `;
    })}
          </div>
        </div>
      </li>
    `;

    render() {
      const { search, open, results, loading, selectedResult } = this.state;
      this.input.value = search;
      if (open) {
        this.container.classList.remove("hidden");
        this.openBtn.classList.add("hidden");
        this.input.focus();
      } else {
        this.container.classList.add("hidden");
        this.openBtn.classList.remove("hidden");
      }

      this.dropdown.innerHTML =
        search === ""
          ? ""
          : loading
            ? html`
              <li class="list-group-item h5">
                <i class="fa fa-spinner fa-pulse fa-fw"></i>
                Loading...
              </li>
            `
            : results.length === 0
              ? html` <li class="list-group-item h5">No Results.</li>`
              : results
                .map((resident, index) =>
                  this.renderSearchItem(resident, index === selectedResult)
                )
                .join("");

      const selectedRow = this.dropdown.querySelector(".selected");
      if (selectedRow) {
        selectedRow.scrollIntoView({
          inline: "center",
          block: "center",
        });
      }
    }
  }
  window.customElements.define("resident-global-search", ResidentGlobalSearch);
})(window);
