!function(a){"function"==typeof define&&define.amd?define(["jquery","./keyboard/keyboard-core","./scrollbar"],a):"object"==typeof module&&module.exports?module.exports=function(b,c){return void 0===c&&(c="undefined"!=typeof window?require("jquery"):require("jquery")(b)),a(c,require("./keyboard/keyboard-core"),require("./scrollbar")),c}:a(jQuery)}(function(a){"use strict";function b(b){var e=a(b.target),f=a(this),g=f.parent(),h=g.find(".n-flyout-container"),i=g.data("direction");f.hasClass("n-drawer-tabs")?h.is(":visible")?e.closest("li").hasClass("tab-selected")&&c(g,i):d(g,i):f.hasClass("n-flyout-activity-area-tabs")?h.is(":visible")?e.closest("li").hasClass("selected")&&c(g,i):d(g,i):h.is(":visible")?c(g,i):d(g,i)}function c(a,b){var c=a.find(".n-flyout-container"),d=c.outerHeight(),e=c.outerWidth();switch(b){case"top":c.parent(".n-flyout").animate({bottom:-d},400,function(){c.hide()});break;case"bottom":c.parent(".n-flyout").animate({top:-d},400,function(){c.hide()});break;case"left":c.parent(".n-flyout").animate({right:-e},400,function(){c.hide()});break;case"right":c.parent(".n-flyout").animate({left:-e},400,function(){c.hide()})}a.attr("data-expand","false"),a.hasClass("n-drawer")&&(a.find(".drawer-toggle-down").removeClass("drawer-toggle-down").addClass("drawer-toggle-up"),a.find(".drawer-shadow").fadeOut(400))}function d(a,b){var c=a.find(".n-flyout-container");switch(c.hasClass("n-flyout-activity-area")||c.show(),b){case"top":c.parent(".n-flyout").animate({bottom:0},400);break;case"bottom":c.parent(".n-flyout").animate({top:0},400);break;case"left":c.parent(".n-flyout").animate({right:0},400);break;case"right":c.parent(".n-flyout").animate({left:0},400)}a.attr("data-expand","true"),a.hasClass("n-taskpad")?c.find(".n-search-input").focus():a.hasClass("n-drawer")?(a.find(".drawer-toggle-up").removeClass("drawer-toggle-up").addClass("drawer-toggle-down"),a.find(".drawer-shadow").fadeIn(400)):a.find(".n-flyout-activity-area .n-flyout-foot").length>0?setTimeout(function(){c.find(".form-control").focus()},50):(c.find("a:first").focus(),c.find("li").removeClass("selected"))}a.fn.nFlyout=function(){return new e(this)};var e=function(b){var d=a(b);if(d.data("initialized")!==!0){var e=d.find(".n-flyout-container"),f=d.data("direction");switch(f||(f="right",d.data("direction","right")),f){case"top":d.css("bottom",-e.outerHeight()+"px");break;case"bottom":d.css("top",-e.outerHeight()+"px");break;case"left":d.css("right",-e.outerWidth()+"px");break;case"right":d.css("left",-e.outerWidth()+"px");var g=d.find(".n-flyout-open"),h=g.outerHeight();g.css("left",e.outerWidth()+1+"px"),g.css("top",Math.ceil((e.outerHeight()-h)/2)+"px")}a(".scrollbars").scrollbars(),e.hide(),d.on("keydown","*:focus",function(b){if(27===b.keyCode){var d=a(this).parents(".n-flyout"),e=d.data("direction");c(d,e)}}),d.data("initialized",!0)}};a(function(){a("body").click(function(b){a(".n-flyout").each(function(){var d=a(this),e=a(b.target).closest(".n-flyout");if(0===e||d[0]!==e[0]){var f=d.find(".n-flyout-container");if(f.is(":visible")){var g=d.data("direction");c(d,g)}}})}),a(".n-flyout").each(function(){a(this).nFlyout()}),a(".n-flyout-activity-area-tabs").on("keydown","*:focus",function(b){if(27===b.keyCode){var d=a(".n-flyout"),e=d.data("direction");c(d,e)}})}),a(document).on("click.wf.flyout",".n-flyout .n-flyout-menu li",function(){a("li").removeClass("selected"),a(this).toggleClass("selected")}),a(document).on("click.wf.flyout",".n-flyout .n-flyout-open",b).on("keydown.wf.flyout.keyboard",".n-flyout-menu",a.wfKBCore.commonKeyboardHandler)});