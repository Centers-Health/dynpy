class AppSwitcher extends HTMLElement {
	constructor() {
		super();
		const template = document.getElementById("app-switcher");
		this.appendChild(template.content.cloneNode(true));

		const onSuccess = (data) => {
			this._apps = data.data.appLinks;
			this.render();
		};

		const onError = (error) => {
			console.log(error);
			// if the graph is down, set this._apps to empty list so that this.apps.filter()
			// will not throw a js error (inside the render())
			this._apps = [];
		};

		const searchQuery = `
            query AppLinks {
                    appLinks {
                        url
                        permission
                        label
                        color
                        abbreviation
                    }
                }
            `;
		const connector = GraphConnector();
		connector.execute(searchQuery, {}, onSuccess, onError);

		this.menu = this.querySelector(".app-switcher-menu");
		document.body.appendChild(this.menu);

		this.button = this.querySelector(".hamburger");
		this.button.onclick = (e) => {
			e.stopPropagation();
			this.open = !this.open;
		};

		window.addEventListener("click", () => {
			this.open = false;
		});
	}

	static get observedAttributes() {
		return ["hidden", "open", "apps"];
	}

	attributeChangedCallback(name, oldVal, newVal) {
		if (oldVal === newVal) return;
		this.render();
	}
	set open(open) {
		this._open = open;
		this.setAttribute("open", open);
	}
	get open() {
		return this._open;
	}
	set hidden(hidden) {
		this._hidden = hidden;
		this.setAttribute("hidden", hidden);
	}
	get hidden() {
		return this._hidden;
	}
	set apps(apps) {
		this._apps = apps;
		this.setAttribute("apps", apps);
	}
	get apps() {
		return this._apps;
	}

	renderApp(app) {
		return `
        <div class="app-switcher-app">
            <a href="${app.url}">
                <div
                    class="app-switcher-icon ${
											window.location.pathname.includes(app.url.split("?")[0])
												? "active"
												: ""
										}"
                    style="background:${app.color}"
                >
                    ${app.abbreviation}
                </div>
                ${
									app.label
										? `<div class="app-switcher-label">${app.label}</div>`
										: ""
								}
            </a>
        </div>
    `;
	}

	render() {
		if (!this.open) {
			this.menu.classList.remove("open");
			this.button.classList.remove("is-active");
		} else {
			this.menu.classList.add("open");
			this.button.classList.add("is-active");
		}

		const isAppSwitcherApp = (currentValue) => {
			return currentValue.label.toLowerCase() !== "contracts";
		};

		const noAppsDisplay = '<p class="text-muted">No apps loaded</p>';

		this.menu.innerHTML = this.apps
			? this.apps
					.filter(isAppSwitcherApp)
					.map((app) => this.renderApp(app))
					.join("")
			: noAppsDisplay;
	}
}
window.customElements.define("app-switcher", AppSwitcher);
