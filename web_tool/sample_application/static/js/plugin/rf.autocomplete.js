//  Copyright (c)2020 by NOKIA
//-----------------------------------------------------------------------------------
//  Filename            : tad.autocomplete.js
//-----------------------------------------------------------------------------------
//  Project             : TAD
//  Language            : ECAMScript V3
//  Author              : Wang Fuqiang, 23575
//  Date                : 27.01.2016
//-----------------------------------------------------------------------------------
//  Contains the javascript code used for auto-complete for textarea.



(function($, window, document, undefined) {
	$(function() {
		var calculator = {
			// key styles
			primaryStyles: ['fontFamily', 'fontSize', 'fontWeight', 'fontVariant', 'fontStyle',
				'paddingLeft', 'paddingTop', 'paddingBottom', 'paddingRight',
				'marginLeft', 'marginTop', 'marginBottom', 'marginRight',
				'borderLeftColor', 'borderTopColor', 'borderBottomColor', 'borderRightColor',
				'borderLeftStyle', 'borderTopStyle', 'borderBottomStyle', 'borderRightStyle',
				'borderLeftWidth', 'borderTopWidth', 'borderBottomWidth', 'borderRightWidth',
				'line-height', 'outline'],

			specificStyle: {
				'word-wrap': 'break-word',
				'overflow-x': 'hidden',
				'overflow-y': 'auto'
			},

			simulator : $('<div id="textarea_simulator" contenteditable="true"/>').css({
				position: 'absolute',
				top: 0,
				left: 0,
				visibility: 'hidden'
			}).appendTo(document.body),

			toHtml : function(text) {
				return text.replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g, '<br>')
					.replace(/(\s)/g,'<span style="white-space:pre-wrap;">$1</span>');
			},
			// calculate position
			getCaretPosition: function() {
				var cal = calculator, self = _ta, element = self[0], elementOffset = self.offset();

				// IE has easy way to get caret offset position
				if (/msie/.test(navigator.userAgent.toLowerCase())) {
					// must get focus first
					element.focus();
					var range = document.selection.createRange();
					return {
						left: range.boundingLeft - elementOffset.left,
						top: parseInt(range.boundingTop) - elementOffset.top + element.scrollTop
							+ document.documentElement.scrollTop + parseInt(self.getComputedStyle("fontSize"))
					};
				}
				cal.simulator.empty();
				// clone primary styles to imitate textarea
				$.each(cal.primaryStyles, function(index, styleName) {
					self.cloneStyle(cal.simulator, styleName);
				});

				// caculate width and height
				cal.simulator.css($.extend({
					'width': self.width(),
					'height': self.height()
				}, cal.specificStyle));

				var value = self.val(), cursorPosition = self.getCursorPosition();
				var beforeText = value.substring(0, cursorPosition),
					afterText = value.substring(cursorPosition);

				var before = $('<span class="before"/>').html(cal.toHtml(beforeText)),
					focus = $('<span class="focus"/>'),
					after = $('<span class="after"/>').html(cal.toHtml(afterText));

				cal.simulator.append(before).append(focus).append(after);
				var focusOffset = focus.offset(), simulatorOffset = cal.simulator.offset();
				// alert(focusOffset.left  + ',' +  simulatorOffset.left + ',' + element.scrollLeft);
				return {
					top: focusOffset.top - simulatorOffset.top - element.scrollTop
						// calculate and add the font height except Firefox
						+ (/firefox/.test(navigator.userAgent.toLowerCase()) ? 0 : parseInt(self.getComputedStyle("fontSize"))),
					left: focus[0].offsetLeft -  cal.simulator[0].offsetLeft - element.scrollLeft
				};
			}
		};
        
        var _ta, _wordSearchUrl, _writeLineStart, _writeLineEnd;
		$.fn.extend({
			getComputedStyle: function(styleName) {
				if (this.length == 0) return;
				var thiz = _ta[0];
				var result = this.css(styleName);
				result = result || (/msie/.test(navigator.userAgent.toLowerCase()) ?
					thiz.currentStyle[styleName]:
					document.defaultView.getComputedStyle(thiz, null)[styleName]);
				return result;
			},
			// easy clone method
			cloneStyle: function(target, styleName) {
				var styleVal = this.getComputedStyle(styleName);
				if (!!styleVal) {
					$(target).css(styleName, styleVal);
				}
			},
			cloneAllStyle: function(target, style) {
				var thiz = _ta[0];
				for (var styleName in thiz.style) {
					var val = thiz.style[styleName];
					typeof val == 'string' || typeof val == 'number'
						? this.cloneStyle(target, styleName)
						: NaN;
				}
			},
			getCursorPosition : function() {
				var thiz = _ta[0], result = 0;
				if ('selectionStart' in thiz) {
					result = thiz.selectionStart;
				} else if('selection' in document) {
					var range = document.selection.createRange();
					if (parseInt($.browser.version) > 6) {
						thiz.focus();
						var length = document.selection.createRange().text.length;
						range.moveStart('character', - thiz.value.length);
						result = range.text.length - length;
					} else {
						var bodyRange = document.body.createTextRange();
						bodyRange.moveToElementText(thiz);
						for (; bodyRange.compareEndPoints("StartToStart", range) < 0; result++)
							bodyRange.moveStart('character', 1);
						for (var i = 0; i <= result; i ++){
							if (thiz.value.charAt(i) == '\n')
								result++;
						}
						var enterCount = thiz.value.split('\n').length - 1;
						result -= enterCount;
						return result;
					}
				}
				return result;
			},
			tadAutocomplete : function(pWordSearchUrl) {
                _ta = this;
                _wordSearchUrl = pWordSearchUrl;
                // initial
                this.autocomplete({
                    //source: _this._sourceCallback,
                    source: $.fn.autoCompleteSource,
                    select: function( event, ui ) {
                        var ta = event.target;
                        $.fn.onUserSelected(ta, ui);
                        event.stopPropagation();
                        event.preventDefault();
                        return false;
                    },
                    focus: function( event, ui ) { //stopping replacing the text field's value with the value of the focused item
                        return false;
                    },
                    open: function( event, ui ) {
                        $.fn.initLineStartEnd();
                        var ta = event.target;
                        var pos = $.fn.getCaretPosition();
                        $(".ui-autocomplete:visible").css({
                            //left:ta.offsetLeft + pos.left,
                            top:ta.offsetTop + pos.top + 22
                        });
                    },
                    autoFocus: true
                });
			},
			autoCompleteSource : function (request, response) {
                var currentLineContent = $.fn.getCurrentLine();
               
                //var wordSearchUrl = this.wordSearchUrl;
                $.ajax({
                    url : _wordSearchUrl,
                    data : {
                        q: currentLineContent
                    }, 
                    success: function(data) {
                        var trimmedData = data.trim();
                        if (trimmedData.length > 0) {
                            var dataA = trimmedData.split("\n");
                            if (dataA.length > 0) {
                                response(dataA);
                            }
                        } else {
                            response(trimmedData);
                        }
                    }
                });
			},
			onUserSelected : function (pTextArea, pData) {
                var currentValue = $(pTextArea).val();
                var seletedText = pData.item.value;

                var prefix = currentValue.substr(0,_writeLineStart);
                var sufix = currentValue.substr(_writeLineEnd);
                var scrollTop = pTextArea.scrollTop;
                pTextArea.value = prefix + seletedText + sufix;
                $(pTextArea).focus();
                pTextArea.selectionStart = _writeLineStart + seletedText.length;  
                pTextArea.selectionEnd = _writeLineStart + seletedText.length;  
                pTextArea.scrollTop = scrollTop;  
			},
			getCurrentLine : function () {
                var allContent = _ta.val();
                var lineStart = this.getLineStart();
                var lineEnd = this.getLineEnd();
                return allContent.substr(lineStart, lineEnd - lineStart);
			},
			getLineStart : function () {
                var ta = _ta[0];
                var taVal = ta.value;
                var pos = this.getCursorPosition();
                var lastReturnIndex = taVal.lastIndexOf('\n', pos - 1);
                var lineStart = lastReturnIndex > -1 ? lastReturnIndex + 1 : 0;
                return lineStart;
			},
			getLineEnd : function () {
                var ta = _ta[0];
                var taVal = ta.value;
                var pos = this.getCursorPosition();
                var firstReturnIndex = taVal.indexOf('\n', pos);
                var lineEnd = firstReturnIndex > -1 ? firstReturnIndex : taVal.length;
                return lineEnd;
			},
			initLineStartEnd : function () {
                _writeLineStart = this.getLineStart();
                _writeLineEnd = this.getLineEnd();
			},
			getCaretPosition: calculator.getCaretPosition
		});
	});
})(jQuery, window, document);

