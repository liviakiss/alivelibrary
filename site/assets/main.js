// ALIVE Library — minimal, calm interactions only.
(function () {
  "use strict";

  // Thin reading-progress bar (Golden Hour) tied to scroll depth.
  var bar = document.getElementById("progress");
  if (bar) {
    var update = function () {
      var doc = document.documentElement;
      var max = doc.scrollHeight - doc.clientHeight;
      var pct = max > 0 ? (doc.scrollTop || document.body.scrollTop) / max : 0;
      bar.style.width = (pct * 100).toFixed(2) + "%";
    };
    document.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  }
})();
