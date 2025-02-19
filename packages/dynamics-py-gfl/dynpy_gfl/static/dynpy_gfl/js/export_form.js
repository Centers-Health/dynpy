(() => {
  document.getElementById("export_btn").addEventListener("click", (event) => {
    event.preventDefault();
    const btn = event.target;
    const form = btn.closest("form");
    const formData = new FormData(form);
    downloadFile(formData, btn);
  });

  const download = (url, filename) => {
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    return;
  };

  const downloadFile = (formData, btn) => {
    let filename = null;
    let trigger = null;

    // Disable button while file loads
    btn.disabled = true;
    document.body.style.cursor = "wait";

    fetch(window.location.href, {
      method: "post",
      body: formData,
    })
      .then((response) => {
        if (response.status == 401) return response.json();
        if (!response.ok) throw new Error();
        const header = response.headers.get("Content-Disposition");
        const filenameRegex = new RegExp('(?<=filename=").*?(?=")');

        trigger = response.headers.get("HX-Trigger");
        filename = header.match(filenameRegex)[0];

        return response.blob();
      })
      .then((data) => {
        if (data.error_message) throw new Error(data.error_message);
        return URL.createObjectURL(data);
      })
      .then((url) => {
        download(url, filename);
        URL.revokeObjectURL(url);
      })
      .catch((err) => {
        if (err.message) {
          bootbox.alert(err.message);
        } else {
          bootbox.alert(`An error occured. Unable to export the data.`);
        }
        console.error(err);
      })
      .finally(() => {
        if (trigger) {
          htmx.trigger(document.body, trigger);
        }
        // Re-enable button
        btn.disabled = false;
        document.body.style.cursor = "";
      });
  };
})();
