// select the URL for easy copying
var selection = window.getSelection();
var range = document.createRange();
var elt = document.getElementById('selected') || document.getElementById('url');
range.selectNodeContents(elt);
selection.removeAllRanges();
selection.addRange(range);
