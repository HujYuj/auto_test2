!function(a){"function"==typeof define&&define.amd?define(["jquery"],a):"object"==typeof module&&module.exports?module.exports=function(b,c){return void 0===c&&(c="undefined"!=typeof window?require("jquery"):require("jquery")(b)),a(c),c}:a(jQuery)}(function(a){"use strict";function b(b){var f=[c,d,e],g=b.keyCode;-1!==f.indexOf(g)&&(g===c?(a(b.target).trigger("mousedown"),a(b.target).trigger("mouseup")):(b.preventDefault(),b.stopPropagation()))}var c=32,d=38,e=40;a(document).on("keydown.wf.spinner.keyboard",".spinbox .spinbox-up",b).on("keydown.wf.spinner.keyboard",".spinbox .spinbox-down",b)});