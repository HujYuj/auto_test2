!function(a){"function"==typeof define&&define.amd?define(["jquery","./keyboard/keyboard-core"],a):"object"==typeof module&&module.exports?module.exports=function(b,c){return void 0===c&&(c="undefined"!=typeof window?require("jquery"):require("jquery")(b)),a(c,require("./keyboard/keyboard-core")),c}:a(jQuery)}(function(a){"use strict";a.fn.extend({slideToggleVertical:function(b){var c=a(this),d=c.find(".icon"),e=b&&b.isOpen,f=c.parent().find(".panel-body"),g=b&&b.speed;g||(g=500),e||(e=!0),e?(a(f).css("display","block"),d.removeClass("icon-right").addClass("icon-down")):(a(f).css("display","none"),d.removeClass("icon-down").addClass("icon-right")),c.click(function(){f.slideToggle(g,function(){f.is(":visible")?d.removeClass("icon-right").addClass("icon-down"):d.removeClass("icon-down").addClass("icon-right")})})},slideToggleHorizontal:function(b){var c=b&&b.isLeftOpen,d=b&&b.leftWidth,e=a(this),f=e.parent(),g=f.parent().find(".panel-right"),h=f.find(".panel .panel-body"),i=e.parent().find(".panel"),j=e.find("span"),k="undefined"==typeof d?30:d,l="undefined"==typeof c?!0:c;l?(f.css({width:k+"%"}),g.css({width:"calc("+(100-k)+"% - 20px)","margin-left":"20px"}),f.addClass("panel-shadow"),f.find("div").each(function(){a(this).show()}),e.css({"border-top-left-radius":"0px","border-bottom-left-radius":"0px"}),g.addClass("open"),j.removeClass("icon-right").addClass("icon-left")):(f.css({width:"0"}),g.css({width:"calc(100% - 40px)","margin-left":"40px"}),a(i).find("div").each(function(){a(this).hide()}),f.removeClass("panel-shadow"),e.css({"border-top-left-radius":"7px","border-bottom-left-radius":"7px"}),j.removeClass("icon-left").addClass("icon-right")),e.click(function(){var b=a(this);if(h.is(":visible")){var c=f.width(),d=g.width();f.removeClass("panel-shadow"),f.animate({width:0},"show",function(){a(i).find("div").each(function(){a(this).hide()}),b.css({"border-top-left-radius":"7px","border-bottom-left-radius":"7px"}),j.removeClass("icon-left").addClass("icon-right")});var e=c+d-20;g.animate({width:e+"px","margin-left":"40px"})}else f.find("div").each(function(){a(this).show()}),g.css({width:"calc("+(100-k)+"% - 20px)","margin-left":"20px"}),f.animate({width:k+"%"},"show",function(){f.addClass("panel-shadow"),b.css({"border-top-left-radius":"0px","border-bottom-left-radius":"0px"})}),j.removeClass("icon-right").addClass("icon-left")})}});var b=38,c=40;a(document).on("keydown.wf.panel.keyboard",".panel-heading",{notSupport:[b,c]},a.wfKBCore.commonKeyboardHandler).on("keydown.wf.panel.keyboard",".panel-arrow",{notSupport:[b,c]},a.wfKBCore.commonKeyboardHandler),a(".panel-slide-vertical .panel-heading").each(function(){a(this).slideToggleVertical()})});