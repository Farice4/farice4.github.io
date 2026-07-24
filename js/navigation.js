(function() {
    var toggle = document.querySelector('#nav-toggle');
    var navigation = document.querySelector('#site-nav');
    var header = document.querySelector('.site-header');

    if (!toggle || !navigation || !header) {
        return;
    }

    function setOpen(isOpen) {
        toggle.setAttribute('aria-expanded', String(isOpen));
        toggle.setAttribute('aria-label', isOpen ? '关闭导航菜单' : '打开导航菜单');
        navigation.classList.toggle('is-open', isOpen);
    }

    toggle.addEventListener('click', function(event) {
        event.stopPropagation();
        setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });

    document.addEventListener('click', function(event) {
        if (!header.contains(event.target)) {
            setOpen(false);
        }
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            setOpen(false);
            toggle.focus();
        }
    });

    navigation.addEventListener('click', function(event) {
        if (event.target.closest('a')) {
            setOpen(false);
        }
    });
}());
