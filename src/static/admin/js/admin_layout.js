/* ═══════════════════════════════════════════════════════════════════════
   Shared admin two-column layout JS
   Wraps adjacent col-l + col-r fieldsets into flex row containers
   ═══════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
    // ── Two-column fieldset layout ──
    document.querySelectorAll('fieldset.col-l').forEach(function (left) {
        var right = left.nextElementSibling;
        if (!right || !right.matches('fieldset.col-r')) return;

        var wrapper = document.createElement('div');
        wrapper.className = 'col-row-wrapper';
        left.parentNode.insertBefore(wrapper, left);
        wrapper.appendChild(left);
        wrapper.appendChild(right);
    });

    // ── Boolean switches grid (.switches-grid) ──
    // Find checkbox fields inside .switches-grid fieldsets and wrap them in a 2-col grid
    document.querySelectorAll('fieldset.switches-grid').forEach(function (fs) {
        var checkboxRows = [];
        fs.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
            var row = cb.closest('.mb-4, .form-row, .flex.flex-col > div');
            if (row && checkboxRows.indexOf(row) === -1) {
                checkboxRows.push(row);
            }
        });
        if (checkboxRows.length < 2) return;

        var grid = document.createElement('div');
        grid.className = 'switches-grid-inner';
        var originalParent = checkboxRows[0].parentNode;
        originalParent.insertBefore(grid, checkboxRows[0]);
        checkboxRows.forEach(function (row) {
            row.style.marginBottom = '0';
            grid.appendChild(row);
        });

        // Clean up empty containers left behind after moving rows
        if (originalParent.children.length === 1 && originalParent.children[0] === grid) {
            originalParent.parentNode.insertBefore(grid, originalParent);
            originalParent.parentNode.removeChild(originalParent);
        }

        // Remove any empty sibling containers that remain after extracting checkboxes
        var allContainers = fs.querySelectorAll(':scope > div > div');
        allContainers.forEach(function (el) {
            if (el !== grid && el.children.length === 0 && el.textContent.trim() === '') {
                el.remove();
            }
        });
    });

    // ── Generic 2-column field grid (.fields-2col) ──
    // Uses the same robust approach as switches-grid: find inputs/selects/readonly
    // fields, walk up to the .mb-4 wrapper, then arrange into a 2-col grid.
    document.querySelectorAll('fieldset.fields-2col').forEach(function (fs) {
        var fieldRows = [];
        fs.querySelectorAll('input, select, textarea, .readonly, [id^="id_"], img, p').forEach(function (el) {
            var row = el.closest('.mb-4, .form-row');
            if (row && fieldRows.indexOf(row) === -1 && fs.contains(row)) {
                fieldRows.push(row);
            }
        });
        if (fieldRows.length < 2) return;

        var grid = document.createElement('div');
        grid.className = 'fields-2col-grid';
        var originalParent = fieldRows[0].parentNode;
        originalParent.insertBefore(grid, fieldRows[0]);
        fieldRows.forEach(function (row) { grid.appendChild(row); });

        // Clean up empty containers
        if (originalParent.children.length === 1 && originalParent.children[0] === grid) {
            originalParent.parentNode.insertBefore(grid, originalParent);
            originalParent.parentNode.removeChild(originalParent);
        }
    });

    // ── Match right-column single-textarea height to left column ──
    setTimeout(function () {
        document.querySelectorAll('.col-row-wrapper').forEach(function (wrapper) {
            var left = wrapper.querySelector('fieldset.col-l');
            var right = wrapper.querySelector('fieldset.col-r');
            if (!left || !right) return;
            var textareas = right.querySelectorAll('textarea');
            if (textareas.length !== 1) return;
            var leftH = left.getBoundingClientRect().height;
            var rightH = right.getBoundingClientRect().height;
            var taH = textareas[0].getBoundingClientRect().height;
            var extraH = leftH - rightH;
            if (extraH > 4) {
                textareas[0].style.minHeight = Math.round(taH + extraH) + 'px';
            }
        });
    }, 50);
});
