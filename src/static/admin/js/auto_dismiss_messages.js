/* Auto-dismiss Unfold toast messages after 5 seconds */
(function () {
    function dismissMessages() {
        document.querySelectorAll('ul.flex.flex-col.gap-4.mb-6').forEach(function (el) {
            if (el.dataset.autoDismiss) return;
            el.dataset.autoDismiss = '1';
            setTimeout(function () {
                el.style.transition = 'opacity 0.4s ease';
                el.style.opacity = '0';
                setTimeout(function () { el.remove(); }, 400);
            }, 5000);
        });
    }

    document.addEventListener('DOMContentLoaded', dismissMessages);
    document.addEventListener('htmx:afterSwap', dismissMessages);
    document.addEventListener('htmx:afterSettle', dismissMessages);
})();
