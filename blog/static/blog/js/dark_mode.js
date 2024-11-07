document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('dark-mode-toggle');
    const darkModeStylesheet = document.createElement('link');
    darkModeStylesheet.rel = 'stylesheet';
    darkModeStylesheet.href = '{% static "blog/dark_mode.css" %}';
    darkModeStylesheet.id = 'dark-mode-stylesheet';

    toggleButton.addEventListener('click', function () {
        if (document.getElementById('dark-mode-stylesheet')) {
            document.getElementById('dark-mode-stylesheet').remove();
        } else {
            document.head.appendChild(darkModeStylesheet);
        }
    });
});