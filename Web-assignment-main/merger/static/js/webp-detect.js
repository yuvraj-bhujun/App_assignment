// WebP detection - adds 'webp' or 'no-webp' class to html element
(function() {
  var webP = new Image();
  webP.onload = webP.onerror = function() {
    document.documentElement.className += (webP.height == 2) ? ' webp' : ' no-webp';
  };
  webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
})();
