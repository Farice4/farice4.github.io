(function() {
    var backToTop = document.querySelector('.back-to-top');

    if (!backToTop) {
        return;
    }

    function updateBackToTop() {
        backToTop.classList.toggle('is-visible', window.scrollY > 320);
    }

    window.addEventListener('scroll', updateBackToTop, { passive: true });
    updateBackToTop();
}());
