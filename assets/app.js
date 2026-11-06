/* Progressive enhancement only.
 *
 * Loaded inside a zero-height Streamlit component iframe, which is
 * same-origin with the app document, so it can touch window.parent.document.
 * Everything here is optional: the CSS already gives hover tilt, sheen and
 * entrance motion on its own. If this file never runs — a stricter browser,
 * a future Streamlit that sandboxes harder — the page is unchanged.
 *
 * It adds two things:
 *   1. pointer-tracked 3D tilt + sheen position on .ve-card
 *   2. a slow parallax drift on the aurora blobs
 *
 * No visibility is ever gated on this script. Content is visible without it.
 */
(function () {
  "use strict";

  var MAX_TILT = 7; // degrees
  var parentDoc;
  try {
    parentDoc = window.parent.document;
  } catch (err) {
    return; // cross-origin: silently stay with the CSS-only experience
  }
  if (!parentDoc || parentDoc === document) return;

  function bindTilt(root) {
    var cards = root.querySelectorAll(".ve-card");
    Array.prototype.forEach.call(cards, function (card) {
      if (card.dataset.veTilt === "1") return;
      card.dataset.veTilt = "1";

      function move(event) {
        var box = card.getBoundingClientRect();
        var px = (event.clientX - box.left) / box.width;
        var py = (event.clientY - box.top) / box.height;
        var clampedX = Math.min(Math.max(px, 0), 1);
        var clampedY = Math.min(Math.max(py, 0), 1);
        card.style.setProperty("--tilt-y", ((clampedX - 0.5) * 2 * MAX_TILT).toFixed(2) + "deg");
        card.style.setProperty("--tilt-x", ((0.5 - clampedY) * 2 * MAX_TILT).toFixed(2) + "deg");
        card.style.setProperty("--sheen-x", (clampedX * 100).toFixed(1) + "%");
        card.style.setProperty("--sheen-y", (clampedY * 100).toFixed(1) + "%");
      }

      function reset() {
        card.style.setProperty("--tilt-x", "0deg");
        card.style.setProperty("--tilt-y", "0deg");
      }

      card.addEventListener("pointermove", move);
      card.addEventListener("pointerleave", reset);
      card.addEventListener("blur", reset);
    });
  }

  function bindParallax(root) {
    var blobs = root.querySelectorAll(".ve-blob");
    if (!blobs.length) return;
    var target = { x: 0, y: 0 };
    var current = { x: 0, y: 0 };

    parentDoc.addEventListener(
      "pointermove",
      function (event) {
        target.x = event.clientX / window.parent.innerWidth - 0.5;
        target.y = event.clientY / window.parent.innerHeight - 0.5;
      },
      { passive: true }
    );

    (function tick() {
      current.x += (target.x - current.x) * 0.045;
      current.y += (target.y - current.y) * 0.045;
      Array.prototype.forEach.call(blobs, function (blob, index) {
        var depth = (index + 1) * 9;
        blob.style.translate =
          (current.x * depth).toFixed(1) + "px " + (current.y * depth).toFixed(1) + "px";
      });
      window.parent.requestAnimationFrame(tick);
    })();
  }

  function enhance() {
    bindTilt(parentDoc);
    bindParallax(parentDoc);
  }

  // The app re-renders on every interaction; new cards appear later.
  var attempts = 0;
  var timer = setInterval(function () {
    enhance();
    if (++attempts > 40) clearInterval(timer);
  }, 250);

  try {
    new MutationObserver(enhance).observe(parentDoc.body, {
      childList: true,
      subtree: true,
    });
  } catch (err) {
    /* observer unavailable: the interval above is enough */
  }
})();
