(function() {
    var article = document.querySelector('#post-content, #page-content');
    var progress = document.querySelector('.reading-progress span');
    var sourceToc = document.querySelector('#markdown-toc');
    var desktopToc = document.querySelector('.post-toc-desktop__content, .page-toc--desktop .page-toc__content');
    var mobileToc = document.querySelector('.post-toc-mobile__content, .page-toc--mobile .page-toc__content');
    var tocContainers = document.querySelectorAll('.post-toc-desktop, .post-toc-mobile, .page-toc');
    var contentLayout = document.querySelector('.post-shell, .page-layout');
    var ticking = false;

    if (!article) {
        return;
    }

    if (!sourceToc) {
        tocContainers.forEach(function(container) {
            container.hidden = true;
        });
        if (contentLayout) {
            contentLayout.classList.add('has-no-toc');
        }
    }

    function updateProgress() {
        var articleTop = article.getBoundingClientRect().top + window.scrollY;
        var articleHeight = article.offsetHeight - window.innerHeight;
        var progressValue = articleHeight > 0 ? (window.scrollY - articleTop) / articleHeight : 0;
        var percentage = Math.max(0, Math.min(1, progressValue)) * 100;
        if (progress) {
            progress.style.width = percentage + '%';
        }
        ticking = false;
    }

    function requestProgressUpdate() {
        if (!ticking) {
            requestAnimationFrame(updateProgress);
            ticking = true;
        }
    }

    function populateToc(target) {
        if (!sourceToc || !target) {
            return;
        }
        var clone = sourceToc.cloneNode(true);
        clone.removeAttribute('id');
        target.appendChild(clone);
    }

    populateToc(desktopToc);
    populateToc(mobileToc);

    var tocLinks = document.querySelectorAll('.post-toc-desktop a, .post-toc-mobile a, .page-toc__content a');
    var headings = article.querySelectorAll('h2[id], h3[id], h4[id]');

    if (headings.length && 'IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (!entry.isIntersecting) {
                    return;
                }
                tocLinks.forEach(function(link) {
                    link.classList.toggle('is-active', link.getAttribute('href') === '#' + entry.target.id);
                });
            });
        }, { rootMargin: '-18% 0px -68% 0px' });

        headings.forEach(function(heading) {
            observer.observe(heading);
        });
    }

    window.addEventListener('scroll', requestProgressUpdate, { passive: true });
    window.addEventListener('resize', requestProgressUpdate);
    updateProgress();
}());
