!function(a){"function"==typeof define&&define.amd?define(["jquery"],a):"object"==typeof module&&module.exports?module.exports=function(b,c){return void 0===c&&(c="undefined"!=typeof window?require("jquery"):require("jquery")(b)),a(c),c}:a(jQuery)}(function(a){"use strict";var b=function(b,c){c=a.extend({handle:"",cursor:"move"},c);var d=this;b=a(b),d.init=function(){function a(a){f=k.css("z-index"),g=k.outerHeight(),h=k.outerWidth(),i=k.offset().top+g-a.pageY,j=k.offset().left+h-a.pageX,k.css("z-index",1e3),document.documentElement.addEventListener("mousemove",d,!1),document.documentElement.addEventListener("mouseup",e,!1)}function d(a){var b=a.pageY+i-g,c=a.pageX+j-h;-20>b&&(b=-20),b>window.innerHeight-g/2&&(b=window.innerHeight-g/2),.8*-g>c&&(c=.8*-g),c>window.innerWidth-g/2&&(c=window.innerWidth-g/2),k.offset({top:b,left:c}),a.preventDefault()}function e(){k.removeClass("draggable").css("z-index",f),document.documentElement.removeEventListener("mousemove",d,!1),document.documentElement.removeEventListener("mouseup",e,!1)}b.css("cursor",c.cursor);var f,g,h,i,j,k=b.parent().addClass("draggable");b.get(0).addEventListener("mousedown",a,!1)},d.init()},c=function(){var c=a(this),d={},e="true"===c.attr("data-drag")||"True"===c.attr("data-drag");return e?c.data("wf.dragable",new b(this,d)):void 0},d={dragElements:"div",dataDragAttr:"*[data-drag]"},e=function(b){b=b||d.dragElements;var e=b instanceof a?b:a(b);e.filter(d.dataDragAttr).each(c)},f=a.fn.dragable;a.fn.dragable=function(c){c=c||{};var d=function(){return a(this).data("wf.dragable",new b(this,c))};return a(this).each(d),this},a.fn.dragable.noConflict=function(){return a.fn.dragable=f,this},a(document).ready(function(){e("div")})});