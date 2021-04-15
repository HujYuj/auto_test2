var downloadIFrameId;
var paraValuePattern = "[A-Za-z0-9\\._]*";
$.ajaxSetup({ 
  timeout: 30 * 1000
});

function initMessageDialog() {
	initMsgBox();
}

function disableTab(pTabId) {
	$("#"+ pTabId).attr("disabled","disabled");
}

function enableTab(pTabId) {
	$("#"+ pTabId).removeAttr("disabled");
}

function initMsgBox() {
	$("#dialog").dialog({ 
        autoOpen: false, 
        modal: true, 
        height: "auto", 
        width:400, 
        resizable: true, 
        buttons: { 
            "Ok": function() {
                $(this).dialog("close"); 
            } 
        }
    });
}

function showMsg(msg) {
	$("#dialog").html(msg);
	$("#dialog").dialog("open");
}

function initConfirmBox(okCallback, cancleCallback) {
	$("#confirmDialog").dialog({ 
        resizable: false,
        autoOpen: false,
        height: "auto",
        width: 400,
        modal: true,
        draggable: false,
        buttons: { 
            "Ok": function() {
                $(this).dialog("close"); 
                if(okCallback) {
                    okCallback();
                }
            },
            Cancel: function() {
                $( this ).dialog( "close" );
                if(cancleCallback) {
                    cancleCallback();
                }
            }
        }
    });
}

function showConfirm(msg) {
	$("#confirmDialog").html(msg);
	$("#confirmDialog").dialog("open");
}




function cursorDefault() {
	$(".line").css("cursor","auto");
}

function cursorHand() {
	$(".line").css("cursor","pointer");
}

function forbidenKeyBoard()
{
	$(document).keydown(function(event){ 
	    if ((event.altKey)&&   
	      ((event.keyCode==37)||   //屏蔽 Alt+ 方向键 ←   
	       (event.keyCode==39)))   //屏蔽 Alt+ 方向键 →   
	   {   
	       //event.returnValue=false;   
	       return false;  
	   }   
	   /* if(event.keyCode==8){  
	        return false; //屏蔽退格删除键    
	    }  */
	    // F1
	    if(event.keyCode==112){
	    	var win = window.open("help.jsp","_blank","location=no,toolbar=no,width=1024px,height=768px,center=yes,scrollbars=yes");
	    	if(win == null)	{
	    		showMsg(Tips.prototype.WIN_OPEN_FAIL);
	    	}
	    	return false; 
    	}  
	    if(event.keyCode==116){  
	        return false; //屏蔽F5刷新键   
	    }  
	    if((event.ctrlKey) && (event.keyCode==82)){  
	        return false; //屏蔽alt+R   
	    }  
	});
}

function forbidenKeyBoardForInput(id)
{	
	
	$(id).keydown(function(event){  
	    if ((event.altKey)&&   
	      ((event.keyCode==37)||   //屏蔽 Alt+ 方向键 ←   
	       (event.keyCode==39)))   //屏蔽 Alt+ 方向键 →   
	   {   
	       event.returnValue=false;   
	       return false;  
	   }   
	   /* if(event.keyCode==8){  
	        return false; //屏蔽退格删除键    
	    }  */
	    // F1
	    if(event.keyCode==112){
	    	var win = window.open("help.jsp","_blank","location=no,toolbar=no,width=1024px,height=768px,center=yes,scrollbars=yes");
	    	if(win == null)	{
	    		showMsg(Tips.prototype.WIN_OPEN_FAIL);
	    	}
	    	return false; 
    	}  
	    if(event.keyCode==116){  
	        return false; //屏蔽F5刷新键   
	    }  
	    if((event.ctrlKey) && (event.keyCode==82)){  
	        return false; //屏蔽alt+R   
	    }  
	});
}


//Added for TAD309#2.Show error message needed by user on TAD GUI. Wang Fuqiang 2016.08.09
function parseTADRuntimeExceptionText(pText) {
    var exceptionText;
    if (pText && pText.length > 0) {
        var patternStr = "automation.ttcn.exception.TADRuntimeException:";
        var firstLine = pText.split("\n")[0];
        var patternIndex = firstLine.indexOf(patternStr);
        if (firstLine &&  patternIndex > -1) {
            exceptionText = firstLine.substring(patternIndex +  patternStr.length);
        }
    }
	return exceptionText;
}

function hideMsg() {
	$("#dialog").dialog("close");
}

String.prototype.trim = function()
{
     return this.replace(/(^\s*)|(\s*$)/g, "");
};

String.prototype.ltrim = function()
{
     return this.replace(/(^\s*)/g, "");
};

String.prototype.rtrim = function()
{
     return this.replace(/(\s*$)/g, "");
};

function postAjaxRequest(pUrl, pData, pMsgs, pFun) {
	$.ajax({
		type : "POST",
		url : pUrl,
		data : pData,
		beforeSend : function() {
            if(pMsgs != null){
                showMsg(pMsgs[Tips.prototype.INDEX_BEFORE]);
            }
		},

		success : function(data) {
			if(pFun) {
				hideMsg();
				pFun(data);
			} else {
                if(pMsgs != null){
                    showMsg(pMsgs[Tips.prototype.INDEX_SUCCESS]);
                }
			}
		},
		
		error : function(jqXHR, textStatus, errorThrown) { //Updated for TAD309#2.Show error message needed by user on TAD GUI. Wang Fuqiang 2016.08.09
            var _responseText = jqXHR.responseText;
            var _exceptionText = parseTADRuntimeExceptionText(_responseText);
            if (_exceptionText) {
                showMsg(_exceptionText);
            } else {
                if(pMsgs != null){
                    showMsg(pMsgs[Tips.prototype.INDEX_ERROR]);
                }
            }
		},
		
		timeout : function(data) {
            if(pMsgs != null){
                showMsg(pMsgs[Tips.prototype.INDEX_TIMEOUT]);
            }
		}
	});
}

function DoAjax($url, $type, $data, $sucFunc, $errFunc ,isAsync) {

	$.ajax({
		async : (isAsync == undefined) ? (true) : (isAsync),
		url : $url,
		type : $type,
		data : $data,
		success : $sucFunc,
		error : $errFunc
	});

}

function initDownloadButton(pButtonId, pUrl, gHistory) {
	var downloadButton = new Button("#" + pButtonId);
    downloadButton.setState(true);
	downloadButton.bind(function() {
        var isSureDownload = false;
        var isModified = isChanged(gHistory);
        if(isModified) {
            isSureDownload = confirmDownload();
        } else {
            isSureDownload = true;
        }
        
        if (isSureDownload) {
            if (isModified) {
                gHistory.clear();
            }
            downloadFile(pUrl);
            
        }
	});
}

function downloadFile(pUrl) {//use <iframe> instead of <a>, because <a> redirects the page which makes JS variables not available.
    if (downloadIFrameId) {
        $( '#' + downloadIFrameId ).remove();
    }
    downloadIFrameId = new Date().getTime();
    $("body").append("<iframe id='" + downloadIFrameId + "' src='" + pUrl+ "' style='display: none;' ></iframe>");
}

function newSingleWin(pUrl, pWinName) {
	var win = window.open(pUrl, pWinName, "location=no,toolbar=no,/**width=1024px,height=768px,*/center=yes,scrollbars=auto");
	if(win == null)	{
		showMsg(Tips.prototype.WIN_OPEN_FAIL);
	}
	return win;
}

function newWin(pUrl) {
	var win = window.open(pUrl, "_blank", "location=no,toolbar=no,/**width=1024px,height=768px,*/center=yes,scrollbars=auto");
	if(win == null)	{
		showMsg(Tips.prototype.WIN_OPEN_FAIL);
	}
	return win;
}

function getBase() {
	return $("base").attr("href");
}

function setBase(pBase) {
	$("base").attr("href", pBase);
}

function clearBase () {
	$("base").attr("href", "");
}

function clearButtonFocusStyles() {
    var uiButtonSelector = '.ui-button';
    $(uiButtonSelector).mouseup(function() {
        $(this).removeClass('ui-state-focus ui-state-hover ui-state-active');
    });
    
}

function  getRealUrl (pUrl) {
	//var db_form_obj = getForm2DBObj();
	//var json_data = JSON.stringify(pDBObject);
    var baseUrl = getBase();
	var realUrl = (baseUrl && baseUrl.length > 0) ? (baseUrl + pUrl) : pUrl;
	return realUrl;
}

function  getContext () {
    var path = "/"
    var pathName = window.location.pathname;
    
    if (pathName.length > 1) {
        var secondSlashIndex = pathName.substring(1).indexOf("/");
        if (secondSlashIndex > 0) {
            path = pathName.substring(0, secondSlashIndex + 1);
        }
    }
	return path;
}

function  getContextPath (pProtocol) {
    var path = ""
    var host = window.location.host;
    var pathName = window.location.pathname;
    
    if (pProtocol) {
        path = pProtocol
    } else {
        path = window.location.protocol;
    }
    
    var dotIndex = pathName.indexOf(".");
    if (dotIndex > 0) {
        pathName = pathName.substring(0, pathName.lastIndexOf("/")) + "/";
    }
    
    path += "://" +  host + pathName;

	return path;
}

function  getWsAbsoluteUrl (pRelativeUrl) {
    var cxt = getContextPath("ws");
	
	return cxt + pRelativeUrl;
}

function  getAbsoluteUrl (pProtocol, pRelativeUrl) {
    var cxt = getContextPath(pProtocol);
	
	return cxt + pRelativeUrl;
}

//Updated for TAD691#Add script editor web page in TAD GUI (edit/export/import/floating prompt). Wang Fuqiang 2016.03.09
//Updated for TAD302#1.Optimize resizing logic to make calculation more accurate. Wang Fuqiang 2016.03.08
//Added for CR 145304ESPE02#9.Add logic of adjusting  body size automatically based on browser window size. Wang Fuqiang 2014.8.8
function resizeContentWrapperHeight(pCallback) {
    if (pCallback && typeof pCallback == 'function') {
        pCallback();
    }
    var contentWrapper = $("#content-wrapper");
    if (contentWrapper.length < 1) {
        contentWrapper = $(".content-wrapper");
    }
    contentWrapper.css("height", "");

    var bodyOuterHeight = $("body").outerHeight(true);
    //var windowHeight = $(window).height(); //it returns inaccurate heigth when browser restores from maximum.
    var windowHeight = window.innerHeight;
    var bodyOuterHeightGap = windowHeight - bodyOuterHeight;
    
    var bodyInnerHeight = $("body").height();
    var bodyHeadHeight = $(".header").length > 0 ? $(".header").outerHeight(true) : 0;
    var bodyFootHeight = $("footer").length > 0 ? $("footer").outerHeight(true) : 0;
    var containerHeight = contentWrapper.parent().outerHeight(true);
    var containerHeightGap = bodyInnerHeight - bodyHeadHeight - bodyFootHeight - containerHeight;
    
    var contentWrapperHeight = contentWrapper.height(); 
    
    var contentWrapperNewHeight = contentWrapperHeight;
    if (containerHeightGap > 0 && bodyOuterHeightGap > 0) {
        contentWrapperNewHeight = contentWrapperHeight + containerHeightGap + bodyOuterHeightGap;
        contentWrapper.height(contentWrapperNewHeight);
    } else if (containerHeightGap > 0) {
        contentWrapperNewHeight = contentWrapperHeight + containerHeightGap;
        contentWrapper.height(contentWrapperNewHeight);
    } else if (bodyOuterHeightGap > 0) {
        contentWrapperNewHeight = contentWrapperHeight + bodyOuterHeightGap;
        contentWrapper.height(contentWrapperNewHeight);
    }
    
    
}

//Added for CR 145304ESPE02#9.Add logic of adjusting  body size automatically based on browser window size. Wang Fuqiang 2014.8.8
function initWindowResize() {
    $(window).resize(resizeContentWrapperHeight);
}

function bindBeforeUnloadLister(pCallback) {
    $(window).bind('beforeunload', pCallback);
}

function bindLoadLister(pCallback) {
    $(window).bind('load', pCallback);
}

function isChanged(pHistory) {
    //console.debug("target:" + event.target);
    if(pHistory && pHistory.size() > 0) {
		return true;
	} else {
        return false;
    }
}

function confirmRefresh() {
    return confirm(Tips.prototype.NOT_SAVED_CHANGES + "\n\n" + Tips.prototype.SURE_REFRESH);
}

function confirmDownload() {
    return confirm(Tips.prototype.NOT_SAVED_CHANGES + "\n\n" + Tips.prototype.SURE_DOWNLOAD);
}


function disableDocumentDefaultRightButtonAction() {
    $(document).vsncontext();
}

function initFloatFix(pTarget, pParent) {
    setTimeout(function(){ // Delay for some milliseconds to wait for loading all GUI components in order to ensure the accuracy of the size. 
        $(pTarget).floatFix(pParent); //Added for CR 146109ESPE02. Wang Fuqiang 2014.8.18
    },Key.prototype.DELAY_TIME_IN_MS);
}


//Added for TAD696#1.Update template based on LCT comparing result. Wang Fuqiang 2015.10.26
function getJQueryCount(pSelector) {
    return $(pSelector).length;;
}

//Added for TAD696#1.Update template based on LCT comparing result. Wang Fuqiang 2015.10.26
function getJQueryIdS(pSelector) {
	var items = $(pSelector);
	var addIDs = new Array();
	items.each(function(i) {
		addIDs.push($(this).parent().parent().attr('id'));
	}); 
    return addIDs;
}

//Added for TAD696#1.Update template based on LCT comparing result. Wang Fuqiang 2015.10.26
function disableButton(pButton) {
	pButton.setState(false);
}

//Added for TAD696#1.Update template based on LCT comparing result. Wang Fuqiang 2015.10.26
function enableButton(pButton) {
	pButton.setState(true);
}

//Added for TAD696#1.Update template based on LCT comparing result. Wang Fuqiang 2015.11.23
function trimMoreSeparators(pString, pSeparator) {
	var _trimmed = pString;
    var _pattern = new RegExp(pSeparator + "{2,}", "g");
    _trimmed = pString.replace(_pattern, pSeparator);
    if (_trimmed.indexOf(pSeparator) == 0) {
        _trimmed = _trimmed.substring(1);
    }
    if (_trimmed.lastIndexOf(pSeparator) == _trimmed.length - 1) {
        _trimmed = _trimmed.substring(0, _trimmed.length - 1);
    }
    return _trimmed;
}

function getParamStringFromUrl(pUrl, pParam) {
    var paraStr = null;
    if(pUrl && pParam) {
        var equalSign = "=";
        var pattern = pParam.concat(equalSign, paraValuePattern); 
        var re = new RegExp(pattern, "g"); //   /wildcard=[A-Za-z0-9\\._]*/g;
        var match = re.exec(pUrl);
        if (match) {
            paraStr = match[0];
        }
	}
    return paraStr;
}

function parseValue(pParaStr, pSeparator) {
    var parsedVal = null;
    
    if(pParaStr && pSeparator) {
        var equalIndex = pParaStr.indexOf(pSeparator);
        if (equalIndex == pParaStr.length - 1) {
            parsedVal = "";
        } else {
            parsedVal = pParaStr.substring(equalIndex + 1);
        }
	}
    return parsedVal;
}

function getParamFromUrl(pUrl, pParam) {
    var paramVal = null;
    
    var paraStr = getParamStringFromUrl(pUrl, pParam)
    if(paraStr) {
        var equalSign = "=";
        paramVal = parseValue(paraStr, equalSign);
	}
    return paramVal;
}

function getParamOneInAllFromUrl(pUrl, pParam) {
    var paramVal = null;
    if(pUrl && pParam) {
        var equalSign = "=";
        var pattern = pParam.concat(equalSign, paraValuePattern); 
        var re = new RegExp(pattern, "g"); //   /wildcard=[A-Za-z0-9\\._]+=?/g;
        var match = re.exec(pUrl);
        if (match) {
            var paraStr = match[0];
            var equalIndex = paraStr.indexOf(equalSign);
            paramVal = paraStr.substring(equalIndex + 1);
        }
	}
    return paramVal;
}


function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function wait(ms) {
    var start = new Date().getTime();
    var end = start;
    while(end < start + ms) {
        end = new Date().getTime();
    }
}

function updateCookie(pCookieName, pNewValue) {
    var cookie = $.cookie(pCookieName);
    if (pNewValue && (!cookie || cookie != pNewValue)) {
        $.cookie(pCookieName, pNewValue, { expires: 7, path: '/' });
    }
}

function getCookie(pCookieName) {
    return $.cookie(pCookieName);
}

function parseHtmlErrorMessage(pResponseText) {
    var $html = $($.parseHTML(pResponseText));
    var title = "";
    var message = "";
    for (var i = 0; i < $html.length; i++) {
        currentElement = $html[i];
        if (currentElement.tagName === "TITLE") {
            title = currentElement.innerText;
        } else if (currentElement.tagName === "P") {
            message = currentElement.innerText;
        }
    }
    return title + ":" + message;
}







