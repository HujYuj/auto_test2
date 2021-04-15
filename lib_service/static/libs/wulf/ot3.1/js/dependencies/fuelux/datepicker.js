!function(a){"function"==typeof define&&define.amd?define(["jquery"],a):"object"==typeof exports?module.exports=a(require("jquery"),require("moment")):a(jQuery)}(function(a){var b="Invalid Date",c="moment.js is not available so you cannot use this function",d=[],e=!1,f=a.fn.datepicker,g=!1,h=function(){var a,b;for(g=!0,a=0,b=d.length;b>a;a++)d[a].init.call(d[a].scope);d=[]};"function"==typeof define&&define.amd?require(["moment"],function(a){e=a,h()},function(a){var b=a.requireModules&&a.requireModules[0];"moment"===b&&h()}):h();var i=function(b,c){this.$element=a(b),this.options=a.extend(!0,{},a.fn.datepicker.defaults,c),this.$calendar=this.$element.find(".datepicker-calendar"),this.$days=this.$calendar.find(".datepicker-calendar-days"),this.$header=this.$calendar.find(".datepicker-calendar-header"),this.$headerTitle=this.$header.find(".title"),this.$input=this.$element.find("input"),this.$wheels=this.$element.find(".datepicker-wheels"),this.$wheelsMonth=this.$element.find(".datepicker-wheels-month"),this.$wheelsYear=this.$element.find(".datepicker-wheels-year"),this.artificialScrolling=!1,this.formatDate=this.options.formatDate||this.formatDate,this.inputValue=null,this.moment=!1,this.momentFormat=null,this.parseDate=this.options.parseDate||this.parseDate,this.preventBlurHide=!1,this.restricted=this.options.restricted||[],this.restrictedParsed=[],this.restrictedText=this.options.restrictedText,this.sameYearOnly=this.options.sameYearOnly,this.selectedDate=null,this.yearRestriction=null,this.$calendar.find(".datepicker-today").on("click.fu.datepicker",a.proxy(this.todayClicked,this)),this.$days.on("click.fu.datepicker","tr td button",a.proxy(this.dateClicked,this)),this.$element.find(".dropdown-menu").on("mousedown.fu.datepicker",a.proxy(this.dropdownMousedown,this)),this.$header.find(".next").on("click.fu.datepicker",a.proxy(this.next,this)),this.$header.find(".prev").on("click.fu.datepicker",a.proxy(this.prev,this)),this.$headerTitle.on("click.fu.datepicker",a.proxy(this.titleClicked,this)),this.$input.on("blur.fu.datepicker",a.proxy(this.inputBlurred,this)),this.$input.on("focus.fu.datepicker",a.proxy(this.inputFocused,this)),this.$wheels.find(".datepicker-wheels-back").on("click.fu.datepicker",a.proxy(this.backClicked,this)),this.$wheels.find(".datepicker-wheels-select").on("click.fu.datepicker",a.proxy(this.selectClicked,this)),this.$wheelsMonth.on("click.fu.datepicker","ul button",a.proxy(this.monthClicked,this)),this.$wheelsYear.on("click.fu.datepicker","ul button",a.proxy(this.yearClicked,this)),this.$wheelsYear.find("ul").on("scroll.fu.datepicker",a.proxy(this.onYearScroll,this));var f=function(){this.checkForMomentJS()&&(e=e||window.moment,this.moment=!0,this.momentFormat=this.options.momentConfig.format,this.setCulture(this.options.momentConfig.culture),e.locale=e.locale||e.lang),this.setRestrictedDates(this.restricted),this.setDate(this.options.date)||(this.$input.val(""),this.inputValue=this.$input.val()),this.sameYearOnly&&(this.yearRestriction=this.selectedDate?this.selectedDate.getFullYear():(new Date).getFullYear())};g?f.call(this):d.push({init:f,scope:this})};i.prototype={constructor:i,backClicked:function(){this.changeView("calendar")},changeView:function(a,b){"wheels"===a?(this.$calendar.hide().attr("aria-hidden","true"),this.$wheels.show().removeAttr("aria-hidden",""),b&&this.renderWheel(b)):(this.$wheels.hide().attr("aria-hidden","true"),this.$calendar.show().removeAttr("aria-hidden",""),b&&this.renderMonth(b))},checkForMomentJS:function(){return(a.isFunction(window.moment)||"undefined"!=typeof e&&a.isFunction(e))&&a.isPlainObject(this.options.momentConfig)&&"string"==typeof this.options.momentConfig.culture&&"string"==typeof this.options.momentConfig.format?!0:!1},dateClicked:function(b){var c,d=a(b.currentTarget).parents("td:first");d.hasClass("restricted")||(this.$days.find("td.selected").removeClass("selected"),d.addClass("selected"),c=new Date(d.attr("data-year"),d.attr("data-month"),d.attr("data-date")),this.selectedDate=c,this.$input.val(this.formatDate(c)),this.inputValue=this.$input.val(),this.$input.focus(),this.$element.trigger("dateClicked.fu.datepicker",c))},destroy:function(){return this.$element.remove(),this.$days.find("tbody").empty(),this.$wheelsYear.find("ul").empty(),this.$element[0].outerHTML},disable:function(){this.$element.addClass("disabled"),this.$element.find("input, button").attr("disabled","disabled"),this.$element.find(".input-group-btn").removeClass("open")},dropdownMousedown:function(){var a=this;this.preventBlurHide=!0,setTimeout(function(){a.preventBlurHide=!1},0)},enable:function(){this.$element.removeClass("disabled"),this.$element.find("input, button").removeAttr("disabled")},formatDate:function(a){var b=function(a){var b="0"+a;return b.substr(b.length-2)};return this.moment?e(a).format(this.momentFormat):b(a.getMonth()+1)+"/"+b(a.getDate())+"/"+a.getFullYear()},getCulture:function(){if(this.moment)return e.locale();throw c},getDate:function(){return this.selectedDate?this.selectedDate:new Date(NaN)},getFormat:function(){if(this.moment)return this.momentFormat;throw c},getFormattedDate:function(){return this.selectedDate?this.formatDate(this.selectedDate):b},getRestrictedDates:function(){return this.restricted},inputBlurred:function(a){var b,c=this.$input.val();c!==this.inputValue&&(b=this.setDate(c),null===b?this.$element.trigger("inputParsingFailed.fu.datepicker",c):b===!1?this.$element.trigger("inputRestrictedDate.fu.datepicker",b):this.$element.trigger("changed.fu.datepicker",b)),this.preventBlurHide||this.$element.find(".input-group-btn").removeClass("open")},inputFocused:function(a){this.$element.find(".input-group-btn").addClass("open")},isInvalidDate:function(a){var c=a.toString();return c===b||"NaN"===c?!0:!1},isRestricted:function(a,b,c){var d,e,f,g,h=this.restrictedParsed;if(this.sameYearOnly&&null!==this.yearRestriction&&c!==this.yearRestriction)return!0;for(d=0,f=h.length;f>d;d++)if(e=h[d].from,g=h[d].to,(c>e.year||c===e.year&&b>e.month||c===e.year&&b===e.month&&a>=e.date)&&(c<g.year||c===g.year&&b<g.month||c===g.year&&b===g.month&&a<=g.date))return!0;return!1},monthClicked:function(b){this.$wheelsMonth.find(".selected").removeClass("selected"),a(b.currentTarget).parent().addClass("selected")},next:function(){var a=this.$headerTitle.attr("data-month"),b=this.$headerTitle.attr("data-year");if(a++,a>11){if(this.sameYearOnly)return;a=0,b++}this.renderMonth(new Date(b,a,1))},onYearScroll:function(b){if(!this.artificialScrolling){var c,d,e=a(b.currentTarget),f="border-box"===e.css("box-sizing")?e.outerHeight():e.height(),g=e.get(0).scrollHeight,h=e.scrollTop(),i=f/(g-h)*100,j=h/g*100;if(5>j){for(d=parseInt(e.find("li:first").attr("data-year"),10),c=d-1;c>d-11;c--)e.prepend('<li data-year="'+c+'"><button type="button">'+c+"</button></li>");this.artificialScrolling=!0,e.scrollTop(e.get(0).scrollHeight-g+h),this.artificialScrolling=!1}else if(i>90)for(d=parseInt(e.find("li:last").attr("data-year"),10),c=d+1;d+11>c;c++)e.append('<li data-year="'+c+'"><button type="button">'+c+"</button></li>")}},parseDate:function(a){var b,c,d,f,g,h,i,j=this,k=new Date(NaN);if(a){if(this.moment)return f=function(a){var b=e(a,j.momentFormat);return!0===b.isValid()?b.toDate():k},d=function(a){var b=e(new Date(a));return!0===b.isValid()?b.toDate():k},g=function(a,b,c){var d=b(a);return j.isInvalidDate(d)?(d=c(d),j.isInvalidDate(d)?k:d):d},"string"==typeof a?g(a,f,d):g(a,d,f);if("string"==typeof a){if(b=new Date(Date.parse(a)),!this.isInvalidDate(b))return b;if(a=a.split("T")[0],c=/^\s*(\d{4})-(\d\d)-(\d\d)\s*$/,i=c.exec(a),i&&(h=parseInt(i[2],10),b=new Date(i[1],h-1,i[3]),h===b.getMonth()+1))return b}else if(b=new Date(a),!this.isInvalidDate(b))return b}return new Date(NaN)},prev:function(){var a=this.$headerTitle.attr("data-month"),b=this.$headerTitle.attr("data-year");if(a--,0>a){if(this.sameYearOnly)return;a=11,b--}this.renderMonth(new Date(b,a,1))},renderMonth:function(b){b=b||new Date;var c,d,e,f,g,h,i,j,k,l,m,n=new Date(b.getFullYear(),b.getMonth(),1).getDay(),o=new Date(b.getFullYear(),b.getMonth()+1,0).getDate(),p=new Date(b.getFullYear(),b.getMonth(),0).getDate(),q=this.$headerTitle.find(".month"),r=b.getMonth(),s=new Date,t=s.getDate(),u=s.getMonth(),v=s.getFullYear(),w=this.selectedDate,x=this.$days.find("tbody"),y=b.getFullYear();for(w&&(w={date:w.getDate(),month:w.getMonth(),year:w.getFullYear()}),q.find(".current").removeClass("current"),q.find('span[data-month="'+r+'"]').addClass("current"),this.$headerTitle.find(".year").text(y),this.$headerTitle.attr({"data-month":r,"data-year":y}),x.empty(),0!==n?(c=p-n+1,i=-1):(c=1,i=0),h=35-n>=o?5:6,f=0;h>f;f++){for(m=a("<tr></tr>"),g=0;7>g;g++)l=a("<td></td>"),-1===i?(l.addClass("last-month"),j!==i&&l.addClass("first")):1===i&&(l.addClass("next-month"),j!==i&&l.addClass("first")),d=r+i,e=y,0>d?(d=11,e--):d>11&&(d=0,e++),l.attr({"data-date":c,"data-month":d,"data-year":e}),e===v&&d===u&&c===t?l.addClass("current-day"):(v>e||e===v&&u>d||e===v&&d===u&&t>c)&&(l.addClass("past"),this.options.allowPastDates||l.addClass("restricted").attr("title",this.restrictedText)),this.isRestricted(c,d,e)&&l.addClass("restricted").attr("title",this.restrictedText),w&&e===w.year&&d===w.month&&c===w.date&&l.addClass("selected"),l.hasClass("restricted")?l.html('<span><b class="datepicker-date">'+c+"</b></span>"):l.html('<span><button type="button" class="datepicker-date">'+c+"</button></span>"),c++,k=j,j=i,-1===i&&c>p?(c=1,i=0,k!==i&&l.addClass("last")):0===i&&c>o&&(c=1,i=1,k!==i&&l.addClass("last")),f===h-1&&6===g&&l.addClass("last"),m.append(l);x.append(m)}},renderWheel:function(a){var b,c,d,e=a.getMonth(),f=this.$wheelsMonth.find("ul"),g=a.getFullYear(),h=this.$wheelsYear.find("ul");for(this.sameYearOnly?(this.$wheelsMonth.addClass("full"),this.$wheelsYear.addClass("hidden")):(this.$wheelsMonth.removeClass("full"),this.$wheelsYear.removeClass("hide hidden")),f.find(".selected").removeClass("selected"),c=f.find('li[data-month="'+e+'"]'),c.addClass("selected"),f.scrollTop(f.scrollTop()+(c.position().top-f.outerHeight()/2-c.outerHeight(!0)/2)),h.empty(),b=g-10;g+11>b;b++)h.append('<li data-year="'+b+'"><button type="button">'+b+"</button></li>");d=h.find('li[data-year="'+g+'"]'),d.addClass("selected"),this.artificialScrolling=!0,h.scrollTop(h.scrollTop()+(d.position().top-h.outerHeight()/2-d.outerHeight(!0)/2)),this.artificialScrolling=!1,c.find("button").focus()},selectClicked:function(){var a=this.$wheelsMonth.find(".selected").attr("data-month"),b=this.$wheelsYear.find(".selected").attr("data-year");this.changeView("calendar",new Date(b,a,1))},setCulture:function(a){if(!a)return!1;if(!this.moment)throw c;e.locale(a)},setDate:function(a){var b=this.parseDate(a);return this.isInvalidDate(b)?(this.selectedDate=null,this.renderMonth()):this.isRestricted(b.getDate(),b.getMonth(),b.getFullYear())?(this.selectedDate=!1,this.renderMonth()):(this.selectedDate=b,this.renderMonth(b),this.$input.val(this.formatDate(b))),this.inputValue=this.$input.val(),this.selectedDate},setFormat:function(a){if(!a)return!1;if(!this.moment)throw c;this.momentFormat=a},setRestrictedDates:function(a){var b,c,d=[],e=this,f=function(a){return a===-(1/0)?{date:-(1/0),month:-(1/0),year:-(1/0)}:a===1/0?{date:1/0,month:1/0,year:1/0}:(a=e.parseDate(a),{date:a.getDate(),month:a.getMonth(),year:a.getFullYear()})};for(this.restricted=a,b=0,c=a.length;c>b;b++)d.push({from:f(a[b].from),to:f(a[b].to)});this.restrictedParsed=d},titleClicked:function(a){this.changeView("wheels",new Date(this.$headerTitle.attr("data-year"),this.$headerTitle.attr("data-month"),1))},todayClicked:function(a){var b=new Date;(b.getMonth()+""!==this.$headerTitle.attr("data-month")||b.getFullYear()+""!==this.$headerTitle.attr("data-year"))&&this.renderMonth(b)},yearClicked:function(b){this.$wheelsYear.find(".selected").removeClass("selected"),a(b.currentTarget).parent().addClass("selected")}},a.fn.datepicker=function(b){var c,d=Array.prototype.slice.call(arguments,1),e=this.each(function(){var e=a(this),f=e.data("fu.datepicker"),g="object"==typeof b&&b;f||e.data("fu.datepicker",f=new i(this,g)),"string"==typeof b&&(c=f[b].apply(f,d))});return void 0===c?e:c},a.fn.datepicker.defaults={allowPastDates:!1,date:new Date,formatDate:null,momentConfig:{culture:"en",format:"L"},parseDate:null,restricted:[],restrictedText:"Restricted",sameYearOnly:!1},a.fn.datepicker.Constructor=i,a.fn.datepicker.noConflict=function(){return a.fn.datepicker=f,this},a(document).on("mousedown.fu.datepicker.data-api","[data-initialize=datepicker]",function(b){var c=a(b.target).closest(".datepicker");c.data("datepicker")||c.datepicker(c.data())}),a(document).on("click.fu.datepicker.data-api",".datepicker .dropdown-menu",function(b){var c=a(b.target);(!c.is(".datepicker-date")||c.closest(".restricted").length)&&b.stopPropagation()}),a(document).on("click.fu.datepicker.data-api",".datepicker input",function(a){a.stopPropagation()}),a(function(){a("[data-initialize=datepicker]").each(function(){var b=a(this);b.data("datepicker")||b.datepicker(b.data())})})});