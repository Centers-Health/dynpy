const GraphConnector = () => {
  if (!window._jsConfig) {
    console.error(
      "GRAPH CONNECTOR ERROR: No window._jsConfig. Need _jsConfig for the graph url."
    );
    return;
  }
  return {
    url: window._jsConfig.urls.graphql,
    execute: function (query, variables, onSuccessCallback, onErrorCallback) {
      fetch(this.url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          query: query,
          variables: variables,
        }),
      })
        .then((response) => {
          if (!response.ok) throw new Error();
          return response.json();
        })
        .then((data) => {
          onSuccessCallback(data);
        })
        .catch((err) => {
          onErrorCallback(err);
        });
    },
  };
};
