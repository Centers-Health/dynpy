const getLoaderInstance = (loaderStyle, customMessage = null) => {
	const loaderInstance = getTemplateInstanceById(`${loaderStyle}-loader`);
	if (customMessage)
		loaderInstance.querySelector("#loading-message").innerHTML = customMessage;
	return loaderInstance.innerHTML;
};

const getLoadingErrorInstance = (customMessage = null) => {
	loaderInstance = getTemplateInstanceById("loading-error");
	if (customMessage)
		loaderInstance.querySelector("#error-message").innerHTML = customMessage;
	return loaderInstance.innerHTML;
};

const getTemplateInstanceById = (templateId) => {
	const templateInstance = document.createElement("div");
	templateInstance.innerHTML = document
		.getElementById(templateId)
		.cloneNode(true).innerHTML;
	return templateInstance;
};
