(function(window) {
    window.LFS = window.LFS || {};
    window.LFS.slugify = function(str) {
        return str
          .toString()               // ensure it's a string
          .normalize("NFD")         // split umlauts into base characters + diacritical marks
          .replace(/[\u0300-\u036f]/g, "") // remove diacritical marks
          .toLowerCase()            // convert to lowercase
          .trim()                   // remove whitespace from start/end
          .replace(/[^a-z0-9]+/g, "-") // convert special characters to "-"
          .replace(/^-+|-+$/g, "");   // remove leading/trailing "-"
    };
})(window);