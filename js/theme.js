(function() {
    var storageKey = 'farice-theme';
    var root = document.documentElement;
    var toggle = document.querySelector('#theme-toggle');
    var themeColor = document.querySelector('#theme-color');
    var mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    function getStoredTheme() {
        try {
            return localStorage.getItem(storageKey);
        } catch (error) {
            return null;
        }
    }

    function updateToggle(theme) {
        if (!toggle) {
            return;
        }
        var isDark = theme === 'dark';
        toggle.setAttribute('aria-pressed', String(isDark));
        toggle.setAttribute('aria-label', isDark ? '切换浅色模式' : '切换深色模式');
        toggle.title = isDark ? '切换浅色模式' : '切换深色模式';
    }

    function updateGiscus(theme) {
        var frame = document.querySelector('iframe.giscus-frame');
        if (!frame || !frame.contentWindow) {
            return;
        }
        frame.contentWindow.postMessage({
            giscus: {
                setConfig: {
                    theme: theme
                }
            }
        }, 'https://giscus.app');
    }

    function applyTheme(theme, source) {
        root.dataset.theme = theme;
        root.dataset.themeSource = source;
        if (themeColor) {
            themeColor.content = theme === 'dark' ? '#101426' : '#edf1fa';
        }
        updateToggle(theme);
        updateGiscus(theme);
    }

    function persistTheme(theme) {
        try {
            localStorage.setItem(storageKey, theme);
        } catch (error) {
            return;
        }
    }

    applyTheme(root.dataset.theme || (mediaQuery.matches ? 'dark' : 'light'), getStoredTheme() ? 'user' : 'system');

    if (toggle) {
        toggle.addEventListener('click', function() {
            var nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
            persistTheme(nextTheme);
            applyTheme(nextTheme, 'user');
        });
    }

    mediaQuery.addEventListener('change', function(event) {
        if (!getStoredTheme()) {
            applyTheme(event.matches ? 'dark' : 'light', 'system');
        }
    });

    window.addEventListener('message', function(event) {
        if (event.origin === 'https://giscus.app') {
            updateGiscus(root.dataset.theme || 'light');
        }
    });
}());
