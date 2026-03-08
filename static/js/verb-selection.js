document.addEventListener("DOMContentLoaded", function() {
    const selectEl = document.getElementById('verb-select');
    if (!selectEl) return;

    // Берем URL из атрибута data-lookup-url, который мы пропишем в HTML
    const lookupUrl = selectEl.dataset.lookupUrl;

    new TomSelect(selectEl, {
        valueField: 'id',
        labelField: 'text',
        searchField: 'text',
        plugins: ['remove_button'],
        persist: false,
        maxOptions: 50,
        loadThrottle: 300,

        onItemAdd: function() {
            this.setTextboxValue('');
            this.refreshOptions();
        },

        load: function(query, callback) {
            if (!query.length) return callback();

            // Используем динамический URL
            const url = `${lookupUrl}?q=${encodeURIComponent(query)}`;

            fetch(url)
                .then(response => response.json())
                .then(json => {
                    callback(json.results);
                }).catch(() => {
                    callback();
                });
        },
        render: {
            option: function(item, escape) {
                return `<div>${escape(item.text)}</div>`;
            },
            item: function(item, escape) {
                return `<div>${escape(item.text)}</div>`;
            }
        }
    });
});