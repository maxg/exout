// select the URL for easy copying
var selection = window.getSelection();
var range = document.createRange();
range.selectNodeContents(document.getElementById('url'));
selection.removeAllRanges();
selection.addRange(range);
