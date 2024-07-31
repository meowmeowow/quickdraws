document.addEventListener("DOMContentLoaded", function() {
    var input = document.querySelector('input[name=rtl-example]');

    if (input) {
        new Tagify(input, {
            whitelist: [
                { value: "Nude"},
                { value: "Clothed"},
                { value: "Male"},
                { value: "Female"},
                { value: "Non-Binary"},
            ],
            dropdown: {
                mapValueTo: 'full',
                classname: 'tagify__dropdown--rtl-example',
                enabled: 0,
                RTL: true,
                escapeHTML: false 
            }
        });
    }
});
