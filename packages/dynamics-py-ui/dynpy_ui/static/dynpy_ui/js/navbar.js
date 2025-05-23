// Handle submenu toggle click. (Based on https://stackoverflow.com/a/45755948/11278892)
$(".navbar .dropdown-menu a.dropdown-toggle").on("click", function (e) {
	// Close other submenus in this dropdown before opening a new submenu
	if (!$(this).next().hasClass("show")) {
		$(this).parents(".dropdown-menu").first().find(".show").removeClass("show");
	}
	// Toggle the submenu
	const $subMenu = $(this).next(".dropdown-menu");
	$subMenu.toggleClass("show");

	// When a top-level dropdown is closed, close all of the submenus as well
	$(this)
		.parents("li.nav-item.dropdown.show")
		.on("hidden.bs.dropdown", (e) => {
			$(".dropdown-submenu .show").removeClass("show");
		});
	return false;
});
