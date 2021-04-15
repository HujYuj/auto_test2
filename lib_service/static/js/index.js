var currentTab = "env";


var g_logChanged;
var websocketUrl = "";
var webSocketFullUrl = getAbsoluteUrl("http", websocketUrl);

var abilSlotSelect = null;
var abilOptPortSelect = null;
var tddSwitchSelect = null;
var rruSelect = null;
var rruOptPortSelect = null;
var numOfCarrierSelect = null;
var bwSelect = null;
var powerSelect = null;
var dlTmSelect = null;
var ulTmSelect = null;

var rfWebsocket = null;
var serialWebSocket = null;
var pingWebsocket = null;
var runnerTabs = null;
var webLogRowLimit = null;


var logContentId = "#logContent"
var serialLogContentId = "#serialLogContent"

var runBtn = null;
var runText = "Run";
var exeText = "Execute";
var stopText = "Stop";
var toTopBtn = null;
var toBottomBtn = null;

var viewLogBtn = null;
var viewLogText = "View REST Log";
var stopViewLogText = "Stop Viewing REST Log";
var pingText = "Ping";
var stopPingText = "Stop pinging";


function onChangeTab(type) {
    var layer = "Div";
    var li = "Li";
    if (currentTab != type) {
        if (type == "runner") {
            isMatched = isEnvMatched();
//              isMatched = true;
            if (isMatched) {
                $("#" + currentTab + layer).hide();
                $("#" + currentTab + li).removeClass('active');
                $("#" + type + layer).show();
                $("#" + type + li).addClass('active');
                
                currentTab = type;
                //$('#control').floatFix('#container');
                $('body').css('min-height', '1000px');
                resizeCallback();
            } else {
                showCheckEnvDialog();
            }
        } else if (type == "env") {
            $("#" + currentTab + layer).hide();
            $("#" + currentTab + li).removeClass('active');
            $("#" + type + layer).show();
            $("#" + type + li).addClass('active');
            
            currentTab = type;
            //$('#cctControls').floatFix('#container');
            $('body').css('min-height', '360px');
            resizeCallback();
        } else if (type == "debug") {
            $("#" + currentTab + layer).hide();
            $("#" + currentTab + li).removeClass('active');
            $("#" + type + layer).show();
            $("#" + type + li).addClass('active');
            
            currentTab = type;
            //$('#cctControls').floatFix('#container');
            $('body').css('min-height', '360px');
            resizeCallback();
        }
    }
}

$(document).ready(function() {
//    window.alert(webSocketFullUrl);
    initResizeForWindow();
    initComponents();
    initDebugComponents();
    initMsgBox();
    //initConfirmBox(running);
    //initConfirmBox(executing);
    bindLoadLister(resizeCallback);
    bindBeforeUnloadLister(beforeUnloadHandler);
    //initWebSocket();
    initAjaxForms();
    setCompomentInitStatus();
    setDebugCompomentInitStatus();
    initLoader();
    setupAutoupdate();
    resizeCallback();
});

function showCheckEnvDialog() {
    showMsg("Your BBU version does not match the required. Please re-check BBU version again.");
}

function showStartConfirm() {
    initConfirmBox(executing);
    showConfirm("Log content was changed. Are you sure to clear?");
}

function showStopConfirm() {
    initConfirmBox(stop);
    showConfirm("Are your sure to stop running?");
}

function showRunningXmlConfirm() {
    initConfirmBox(function() {
        clearLogs();
        $('#executingForm').submit();
    });
    showConfirm("Please reboot BBU and RRU manually first. Are you ready?");
}

function initLoader() {
    var loading = $("#modal").dialog({
        modal: true,
        dialogClass:'loading-dialog',
        draggable: false,
        width: '104px',
        autoOpen: false,
        open: function (pEvent, pUI) {
            $("#modal").height('99px');
            $(".loading-dialog").removeClass('ui-widget ui-widget-content');
        }
    });
    $(document).ajaxStart(function(){
        loading.dialog('open');
    }).ajaxStop(function(){
        loading.dialog('close');
    });
}


function setupAutoupdate() {
    updateDialog = new UpdateDialog("#updateDialogDiv", "#updateMessageDiv", "#updateForceConfirmDiv", 400, "#progressbar", "../autoupdate", "../autoupdate");
    updateDialog.setCheckVersionCallback(checkVersionCallback); 
    updateDialog.setOperationTimeout(60 * 1000);
    //scheduleAutoUpdate();
}

function scheduleAutoUpdate() {
    var isGoingOn = isUpdateGoingOn();
    if (!isGoingOn) {
        data = new Array();
        data.push("csrf_token=" + getToken())
        updateDialog.checkVersion(null, data);
    }
}

function initPingWebSocket() {
    pingWebsocket = new RfWebSocket(webSocketFullUrl, "ping_message");
    pingWebsocket.setMessageCallback(function(message) {
        $pingLogContent = $("#pingLogContent");
        $pingLogContent.empty();
        $pingLogContent.val(message);
    });
}


function connectPingWebsockect() {
    if (!pingWebsocket || !pingWebsocket.isConnected()) {
        initPingWebSocket();
    }
}

function closePingWebsocket() {
    if(pingWebsocket && pingWebsocket.isConnected) {
		pingWebsocket.close();
	}
}

function initSerialWebSocket(){
    serialWebSocket = new RfWebSocket(webSocketFullUrl, "serial_message");
    console.info("init serialwebsocket" + webSocketFullUrl)
    serialWebSocket.setMessageCallback(function(message) {
        console.info("message received:" + message)
        serialLogRowNumber = getSerialLogRowNumber();
        if (serialLogRowNumber > webLogRowLimit) {
            clearSerialLogs();
        }
        serialLogRowNumber++;
        appendSerialMessage(escapeHtml(message));
    });

}

function connectSerialWebSockect() {
    if (!serialWebSocket || !serialWebSocket.isConnected()) {
        initSerialWebSocket();
    }
}

function closeSerialWebSocket() {
    if(serialWebSocket && serialWebSocket.isConnected) {
		serialWebSocket.close();
	}
}

function initWebSocket() {
	//var rfWebsocket = new RfWebSocket(webSocketFullUrl);
    rfWebsocket = new RfWebSocket(webSocketFullUrl, "runner_message");
    console.info("init rfwebsocket" + webSocketFullUrl)
    rfWebsocket.setMessageCallback(function(message) {
        console.info("message received:" + message)
        if (message.startsWith("Done with return code")) {
            changeButtonText(runText)
            showMsg(message);
            $("#status").val("Stopped");
            closeWebsocket();
        } else {
            logRowNumber = getLogRowNumber();
            if (logRowNumber > webLogRowLimit) {
                clearLogs();
            }
            logRowNumber++;
            appendMessage(escapeHtml(message));
            $(logContentId).trigger("change");
        }
    });
}

function connectWebsockect() {
    if (!rfWebsocket || !rfWebsocket.isConnected()) {
        initWebSocket();
        //refreshLog();
    }
}

function closeWebsocket() {
    if(rfWebsocket && rfWebsocket.isConnected) {
		rfWebsocket.close();
	}
}

function appendMessage(message) {
    var $logContent = $(logContentId);
    if ($logContent.val().length > 0) {
        $logContent.prepend(message + "\n");
    } else {
        $logContent.prepend(message);
    }
}

function appendSerialMessage(message) {
    var $serialLogContent = $(serialLogContentId);
    if ($serialLogContent.val().length > 0) {
        $serialLogContent.prepend(message + "\n");
    } else {
        $serialLogContent.prepend(message);
    }
}


function appendMessage_(message) {
    var $logContent = $(logContentId);
    if ($logContent.val().length > 0) {
        $logContent.append("\n" + message);
    } else {
        $logContent.append(message);
    }
}

function setMessages(messages) {
    var $logContent = $(logContentId);
    $logContent.text(messages)
}

function setMessages_(messages) {
    var $logContent = $(logContentId);
    var messageA = messages.split("\n");
    for (var i = 0; i < messageA.length; i++) {
        appendMessage(messageA[i]);
    }
}


function setCompomentInitStatus() {
    var runner_type = $("#runner_type").val();
    if (runner_type != "") {
       tabNumber = -1;
       if (runner_type === "tm") {
           tabNumber = 0;
       } else if (runner_type === "l1call") {
           tabNumber = 1;
       } else if (runner_type === "bfcal") {
           tabNumber = 2;
       } else if (runner_type === "prach") {
           tabNumber = 3;
       }
       runnerTabs.setActiveTab(tabNumber);
    }
   
    var status = $("#status").val();
    if (status === "Running") {
        changeButtonText(stopText)
        initWebSocket()
        initSerialWebSocket()
    }
	triggerSelectChangeEvent();
    
    var ping_status = $("#ping_status").val();
    if (ping_status === "Running") {
        changePingButtonText(stopPingText)
        initPingWebSocket()
    }
}

function triggerSelectChangeEvent() {
	$("#setting select").each(function() {
        var value = $(this).attr("value");
        if (value.length > 0) {
            $(this).val(value).selectmenu("refresh").trigger("selectmenuchange");
        }
	});
}

function start() {
    if (g_logChanged) {
        showStartConfirm();
    } else {
        //running();
        executing();
    }
}

function running() {
    var url = $("#running_url").val();
    var csrfToken = $("#csrf_token").val();
    clearLogs();
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, runningSuccessCallback, failedCallback)
}

function runningSuccessCallback(response, textStatus, jqxhr) {
    successCallback(response, textStatus, jqxhr);
    clearLogs();
    changeButtonText(stopText);
}

function executing() {
    runnerType = $("#runner_type").val()
    if (runnerType === "l1call" || runnerType === "prach") {
        showRunningXmlConfirm();
    } else {
        clearLogs();
        $('#executingForm').submit();
    }
}

//function runningFailedCallback(jqxhr, textStatus, errorThrown) {
    //showMsg(textStatus);
//    failedCallback(jqxhr, textStatus, errorThrown);
//    changeButtonText(runText);
//}

function stop() {
    //var url = "/stop"
    var url = $("#stop_url").val()
    var type = "post"
    var csrfToken = $("#csrf_token").val();
    var paramData = {
		"csrf_token":csrfToken
	}
    DoAjax(url, type, paramData, stopSuccessCallback, failedCallback)
}

function stopSuccessCallback(response, textStatus, jqxhr) {
    successCallback(response, textStatus, jqxhr);
    changeButtonText(runText);
    closeWebsocket();
}

function beforeUnloadHandler(event) {
    closeWebsocket();
    if(g_logChanged) {
		return "Log content was changed.";
	}
}

function clickCheckVersion() {
    var isGoingOn = isUpdateGoingOn();
    if (!isGoingOn) {
        data = new Array();
        data.push("csrf_token=" + getToken())
        updateDialog.setDialogShown(true);
        updateDialog.checkVersion(UpdateDialog.prototype.AUTO_UPDATE_TYPE_MANUAL, data);
    } else {
        updateDialog.setDialogShown(true);
        updateDialog.setUpdateType(UpdateDialog.prototype.AUTO_UPDATE_TYPE_MANUAL);
    }
}

function getToken() {
    return $("#csrf_token").val();
}

function isUpdateGoingOn() {
    return updateDialog.isGoingOn();
}

function checkVersionCallback(pNewVersionAvailable, pLastestVersion) {
    updateSysVersionCookie(pNewVersionAvailable, pLastestVersion);
    updateIcon(pNewVersionAvailable);
}

function updateSysVersionCookie(pNewVersionAvailable, pLastestVersion) {
    var cookieKeyName = 'dut_control_auto_update';
    var cookie = $.cookie(cookieKeyName);
    if (pNewVersionAvailable && (!cookie || cookie != pLastestVersion)) {
        updateDialog.setDialogShown(true);
        $.cookie(cookieKeyName, pLastestVersion, { expires: 7, path: getContext() });
    } else if (updateDialog.getUpdateType() == UpdateDialog.prototype.AUTO_UPDATE_TYPE_AUTO) {
        updateDialog.setDialogShown(false);
    }
}

function updateIcon(pNewVersionAvailable) {
    var updateBtn = $(' #update ');
    if (pNewVersionAvailable) {
        updateBtn.addClass("newUpdate");
    } else {
        updateBtn.removeClass("newUpdate");
    }
}

function changeButtonText(btnText) {
    if (btnText === stopText) {
        runBtn.setText(stopText);
        runBtn.setPrimaryIcon("stopBtn");
        disableComponents("runBtn");
    } else if (btnText === runText) {
        runBtn.setText(runText);
        runBtn.setPrimaryIcon("autorunBtn");
        enableComponents("runBtn");
    }
}

function changeViewLogBtnText(btnText) {
    if (btnText === stopViewLogText) {
        viewLogBtn.setText(viewLogText);
        disableComponents("viewLogBtn");
    } else if (btnText === viewLogText) {
        viewLogBtn.setText(stopViewLogText);
        enableComponents("viewLogBtn");
    }
}


function changePingButtonText(btnText) {
    pingBtn.setText(btnText);
}


function disableComponents(source) {
    $("#setting select").selectmenu('disable');
    $("#runnerTabs input").prop( "disabled", true );
    $( ".control input" ).checkboxradio({
      disabled: true
    });
    if (source == "runBtn") {
        viewLogBtn.disable();
    } else if (source == "viewLogBtn"){
        runBtn.disable();
    }
    runnerTabs.disableAllTabs();
    disableTab("debugLi");

}

function enableComponents(source) {
    $("#setting select").selectmenu('enable');
    $("#runnerTabs input").prop( "disabled", false );
    $( ".control input" ).checkboxradio({
      disabled: false
    });
    if (source == "runBtn") {
        viewLogBtn.enable();
    } else if (source == "viewLogBtn"){
        runBtn.enable();
    }
    runnerTabs.enableAllTabs();
    enableTab("debugLi");

}

function initAjaxForms() {
    var executingFormOptions = { 
        success: function(response, textStatus, jqxhr, formData) {
                    if (response["type"] === "error") {
                        showMsg(response["message"]);
                        changeButtonText(runText);
                    } else if (response["type"] === "success") {
                        connectWebsockect();
                        connectSerialWebSockect();
                        showMsg(response["message"]);
                        changeButtonText(stopText);
                        resizeCallback(); 
                    }
                    
                }, 
        error: function(jqxhr, textStatus, errorThrown, formData) {
                    failedCallback(jqxhr, textStatus, errorThrown);
                } 
    }; 
    
    // bind form using 'ajaxForm' 
    $('#executingForm').ajaxForm(executingFormOptions);
}

function onRunnerTabChange(pNewTab) {
    runnerType = "";
    if (pNewTab === "TM Test") {
        runnerType = "tm"
    } else if (pNewTab === "L1 Call Test") {
        runnerType = "l1call"
    } else if (pNewTab === "BF Cal Test") {
        runnerType = "bfcal"
    } else if (pNewTab === "Prach Test") {
        runnerType = "prach"
    }
    $("#runner_type").val(runnerType);
    resizeCallback();
}

function initComponents() {
    webLogRowLimit = parseInt($("#web_log_row_limit").val());
    $( ".controlgroup-vertical" ).controlgroup();
    //$('legend').css('width', null);
    envTabs = new RfTab("#envTabs", false);
    runnerTabs = new RfTab("#runnerTabs", false);
    runnerTabs.setActivateCallback(onRunnerTabChange);

    
    $("#setting select").selectmenu();
    
    $('#case_type').on('selectmenuchange', function() {
        var numOfCarrier = $(this).val();
        var $twoCarrier = $("#2ndCarrier");
        if (numOfCarrier === "1CC") {
            $twoCarrier.hide();
        } else {
            $twoCarrier.show();
        }
    });
    $('#auto_generate').on('selectmenuchange', function() {
        var type = $(this).val();
        if (type === "auto") {
            showSetting();
            resizeCallback();
        } else {
            hideSetting();
            resizeCallback();
        }
    });
    
    $("#runnerTabs input").addClass("ui-autocomplete-input");
    
    $( ".control input" ).checkboxradio();
    
    var $logContent = $(logContentId);
    var $serialLogContent = $(serialLogContentId)
    //$logContent.on('change keyup paste', function() {
    $logContent.on('change', function() {    
        g_logChanged = true;
        //$(this).scrollTop($(this)[0].scrollHeight);
    });
    /**
	saveBtn = new Button("#saveBtn");
    saveBtn.setPrimaryIcon("saveBtn");
    saveBtn.setState(true);
	saveBtn.bind(function(event) {
        event.preventDefault();
        $('#settingForm').submit();
	});
    **/

	runBtn = new Button("#runBtn");
    runBtn.setPrimaryIcon("autorunBtn");
    runBtn.setState(true);
	runBtn.bind(function(event) {
        event.preventDefault();
        var text = runBtn.getText().trim();
        if (text === runText) {
            start();
        } else if (text === stopText) {
            //stop();
            showStopConfirm()
        }
	});

	toTopBtn = new Button("#toTopBtn");
    toTopBtn.setPrimaryIcon("toTopBtn");
    toTopBtn.setState(true);
	toTopBtn.bind(function(event) {
        event.preventDefault();
        var $logContent = $(logContentId);
        $logContent.scrollTop(0);
	});

	toBottomBtn = new Button("#toBottomBtn");
    toBottomBtn.setPrimaryIcon("toBottomBtn");
    toBottomBtn.setState(true);
	toBottomBtn.bind(function(event) {
        event.preventDefault();
        var $logContent = $(logContentId);
        $logContent.scrollTop($logContent[0].scrollHeight);
	});

	viewLogBtn = new Button("#viewLogBtn");
    viewLogBtn.setPrimaryIcon("searchBtn");
    viewLogBtn.setState(true);
	viewLogBtn.bind(function(event) {
        event.preventDefault();
        var text = viewLogBtn.getText().trim();
        if (text === viewLogText) {
            changeViewLogBtnText(text)
            clearLogs();
            connectWebsockect();
            disableComponents("viewLogBtn");
        } else if (text === stopViewLogText) {
            changeViewLogBtnText(text)
            closeWebsocket();
            enableComponents("viewLogBtn");
        }
	});

	var uiButtonSelector = '.ui-button';
    $(uiButtonSelector).unbind("mouseover");
    $(uiButtonSelector).off("mouseover");
    $(uiButtonSelector).mouseover(function() {
        //$(this).removeClass('ui-state-focus ui-state-hover ui-state-active');
        //console.info("moseover");
    });

	var refreshBtn = new Button("#refreshBtn");
    refreshBtn.setPrimaryIcon("refreshBtn");
    refreshBtn.setState(true);
	refreshBtn.bind(function(event) {
        event.preventDefault();
        refreshLog();
	});

	var downloadBtn = new Button("#downloadBtn");
    downloadBtn.setPrimaryIcon("downloadBtn");
    downloadBtn.setState(true);
	downloadBtn.bind(function(event) {
        event.preventDefault();
        remote_download();
	});

	var checkEnvBtn = new Button("#checkEnvBtn");
    checkEnvBtn.setPrimaryIcon("checkEnvBtn");
    checkEnvBtn.setState(true);
	checkEnvBtn.bind(function(event) {
        event.preventDefault();
        checkEnv();
	});
    
	pingBtn = new Button("#pingBtn");
    pingBtn.setPrimaryIcon("pingBtn");
    pingBtn.setState(true);
	pingBtn.bind(function(event) {
        event.preventDefault();
        var text = pingBtn.getText().trim();
        if (text === pingText) {
            startPing();
        } else if (text === stopPingText) {
            stopPing();
        }
	});
}

function startPing() {
    var url = $("#start_ping_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, startPingSuccessCallback, failedCallback)
}

function clearLogs() {
    $(logContentId).empty();
    logRowNumber = 0;
}

function clearSerialLogs() {
    $(serialLogContentId).empty();
    serialLogRowNumber = 0;
}

function getLogRowNumber() {
    var logText = $(logContentId).val();
    var lines = logText.split(/\r|\r\n|\n/);
    return lines.length
}

function getSerialLogRowNumber() {
    var serialLogText = $(serialLogContentId).val();
    var serialLines = serialLogText.split(/\r|\r\n|\n/);
    return serialLines.length
}

function startPingSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "success") {
        connectPingWebsockect();
        changePingButtonText(stopPingText);
    }
    showMsg(response["message"]);
}


function stopPing() {
    var url = $("#stop_ping_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, stopPingSuccessCallback, failedCallback)
}

function stopPingSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "success") {
        closePingWebsocket();
        changePingButtonText(pingText);
    }
    showMsg(response["message"]);
}


function checkEnv() {
    var url = $("#check_env_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, checkEnvSuccessCallback, failedCallback)
}

function checkEnvSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "success") {
        messageJson = JSON.parse(response["message"])
        $("#actualLonerVersion").html(messageJson.loner_version);
        $("#actualFSVersion").html(messageJson.ps_version);
        $("#tip").html(messageJson.tip);
        $("#is_matched").val(messageJson.is_matched);
        updateEnvVersionCookie(messageJson.loner_version, messageJson.ps_version)
    } else {
        showMsg(response["message"]);
    }
}

function updateEnvVersionCookie(pCheckedLonerVersion, pFSVersion) {
    var checkedLonerVersion =  $(pCheckedLonerVersion);
    var checkedFSVersion =  $(pFSVersion);
    updateCookie("checkedLonerVersion", checkedLonerVersion.html());
    updateCookie("checkedpFSVersion", checkedFSVersion.html());
}

function isEnvMatched_() {
    isMatched = $("#is_matched").val();
    return isMatched === "True";
}

function isEnvMatched() {
    requiredLonerVersion = $("#requiredLonerVersion").html();
    requiredFSVersion = $("#requiredFSVersion").html();
    checkedLonerVersion = getCookie("checkedLonerVersion");
    checkedFSVersion = getCookie("checkedpFSVersion");
    
    return requiredLonerVersion === checkedLonerVersion && requiredFSVersion === checkedFSVersion;
}


function refreshLog() {
    var url = $("#refresh_url").val();
    var type = "GET"
    var csrfToken = $("#csrf_token").val();
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, refreshSuccessCallback, failedCallback)
}

function showSetting() {
    var $setting = $(".setting");
    var caseType = $('#case_type').val();
    if (caseType != "1CC") {
        $('#2ndCarrier').show();
    }
    $setting.show();
}

function hideSetting() {
    var $setting = $(".setting");
    var caseType = $('#case_type').val();
    if (caseType != "1CC") {
        $('#2ndCarrier').hide();
    }
    $setting.hide();
}

function refreshSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "success") {
        //$(logContentId).val(response["message"]); //this will cause no update of content when using append method
        clearLogs();
        setMessages(response["message"]);
        logRowNumber = getLogRowNumber();
        $(logContentId).trigger("change");
    } else if (type === "error") {
        showMsg(response["message"]);
    }
}

function successCallback(response, textStatus, jqxhr) {
    showMsg(response["message"]);
}

function failedCallback(jqxhr, textStatus, errorThrown) {
    if (jqxhr.readyState === 0 && textStatus === "error") {
        showMsg("Server not reachable.");
    } else if (jqxhr.readyState === 4){
        errorMessage = parseHtmlErrorMessage(jqxhr.responseText);
        showMsg(mappingErrors(errorMessage));
    } else {
        showMsg(textStatus);
    }
}

function mappingErrors(pOrigErrorMessage) {
    var errorMsgMapping = {
        "400 Bad Request:The CSRF session token is missing.": "Session timed out, please refresh the page.",
        "400 Bad Request:The CSRF token has expired.": "Session timed out, please refresh the page."
    };
    
    newMsg = errorMsgMapping[pOrigErrorMessage];
    if (!newMsg) {
        newMsg = pOrigErrorMessage;
    }
    return newMsg;
}

function downloadSuccessCallback(response, textStatus, jqxhr) {
    if (response["type"] === "error") {
        showMsg(response["message"]);
    } else {
        local_download("", response);
    }
}

function remote_download() {
    var url = $("#download_url").val();
    var type = "GET"
    var csrfToken = $("#csrf_token").val();
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, downloadSuccessCallback, failedCallback)
}

function local_download(filename, text) {
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    pom.setAttribute('download', filename);

    if (document.createEvent) {
        var event = document.createEvent('MouseEvents');
        event.initEvent('click', true, true);
        pom.dispatchEvent(event);
    } else {
        pom.click();
    }
}
function resizeCallback() {
    resizeContentWrapperHeight(cleanTaHeight);
    resizeTextArea();
}

function initResizeForWindow() {
    $(window).resize(resizeCallback);
}

function cleanTaHeight() {
    var $ta = $( logContentId );
    var $tas = $( serialLogContentId);
    $ta.css("height", "");
    $tas.css("height", "");
}

function resizeTextArea() {
    var $ta = $( logContentId );
    var $tas = $( serialLogContentId );
    $ta.css("height", "");
    $tas.css("height", "");
    var $wrapper = $( ".content-wrapper" );
    var wrapperWidth = $wrapper.width();
    var wrapperHeight = $wrapper.height();
    var settingHeight = $( "#setting" ).outerHeight(true);
    var controlHeight = $( "#control" ).outerHeight(true);
    var taContainerHeight = $( "#logContentDiv" ).outerHeight(true);
    var tasContainerHeight = $( "#serialLogContentDiv ").outerHeight(true);
    var taHeight = $ta.height();
    var tasHeight = $tas.height();
    var gap = wrapperHeight - settingHeight - controlHeight - taContainerHeight;
    if (gap > 0) {
        $ta.height( gap + taHeight);
    }
    var sgap = wrapperHeight - settingHeight - controlHeight - tasContainerHeight;
    if (sgap > 0) {
        $tas.height( gap + tasHeight);
    }
    $ta.css("width", wrapperWidth);
    $tas.css("width", wrapperWidth);
}



