var carrierActivateWebsocket = null;
var iqCaptureWebsocket = null;
var blerCheckWebsocket = null;

var carrierActivateTabStatusId = "activation_status";
var iqCaptureTabStatusId = "capture_iq_status";
var blerCheckTabStatusId = "check_bler_status";
var runningStatus = "Running";
var stoppedStatus = "";

$activateCarrierLogContent = $("#activateCarrierLogContent");
$captureIOLogContent = $("#captureIOLogContent");
var debugTabs = null;
var runCarrierActivationBtn = null;
var startCaptureIQBtn = null;
var startCheckBlerBtn = null;
var debugStartText = "Start";
var debugStopText = "Stop";
var blerChart = null;
var carrierActivateTabName = "Carrier Activate";
var iqCaptureTabName = "IQ Data Capture";
var blerCheckTabName = "BLER Check";
var tabMapping = {
   "Carrier Activate" : "0",
   "IQ Data Capture" : "1",
   "BLER Check" : "2",
   "0": "Carrier Activate",
   "1": "IQ Data Capture", 
   "2": "BLER Check"
}

function getTabName(pTabIndex) {
    return tabMapping[pTabIndex.toString()];
}

function getTabIndex(pTabName) {
    return parseInt(tabMapping[pTabName]);
}

function initDebugComponents() {
    $("#activateCarrierDiv select").selectmenu();
    debugTabs = new RfTab("#debugTabs", false);
    debugTabs.setActivateCallback(debugTabActivateCallback);

	runCarrierActivationBtn = new Button("#runCarrierActivationBtn");
    runCarrierActivationBtn.setPrimaryIcon("activateBtn");
    runCarrierActivationBtn.setState(true);
	runCarrierActivationBtn.bind(function(event) {
        event.preventDefault();
        var text = runCarrierActivationBtn.getText().trim();
        if (text === debugStartText) {
            activateCarrer();
        } else if (text === debugStopText) {
            showStopCarrierActivateConfirm()
        }
	});

	startCaptureIQBtn = new Button("#startCaptureIQBtn");
    startCaptureIQBtn.setPrimaryIcon("captureBtn");
    startCaptureIQBtn.setState(true);
	startCaptureIQBtn.bind(function(event) {
        event.preventDefault();
        var text = startCaptureIQBtn.getText().trim();
        if (text === debugStartText) {
            captureIQ();
        } else if (text === debugStopText) {
            showStopIqCaptureConfirm()
        }
	});

	startCheckBlerBtn = new Button("#startCheckBlerBtn");
    startCheckBlerBtn.setPrimaryIcon("checkBtn");
    startCheckBlerBtn.setState(true);
	startCheckBlerBtn.bind(function(event) {
        event.preventDefault();
        var text = startCheckBlerBtn.getText().trim();
        if (text === debugStartText) {
            checkBler();
        } else if (text === debugStopText) {
            showStopCheckBlerConfirm()
        }
	});
    
    blerChart = new RfLineChart("#blerChart", "BLER", "#3e95cd", true, 50);
}

function debugTabActivateCallback() {
    resizeCallback();
}
function activateCarrer() {
    var activate_type = $("#activate_type").val();
    var carrier_number = $("#carrier_number").val();
    var url = $("#carrier_activation_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "activate_type": activate_type,
        "carrier_number": carrier_number,
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, activateCarrierSuccessCallback, failedCallback)
}

function activateCarrierSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "error") {
        changeState(debugStartText, carrierActivateTabName);
    } else if (type === "success") {
        setTabStatus(carrierActivateTabStatusId, runningStatus);
        connectCarrierActivateWebsockect();
        $activateCarrierLogContent.empty();
        changeState(debugStopText, carrierActivateTabName);
        resizeCallback(); 
    }
    showMsg(response["message"]);
}

function captureIQ() {
    var direction = $("#direction").val();
    var cell_number = $("#cell_number").val();
    var url = $("#capture_iq_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "direction": direction,
        "cell_number": cell_number,
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, captureIQSuccessCallback, failedCallback)
}

function captureIQSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "error") {
        changeState(debugStartText, iqCaptureTabName);
    } else if (type === "success") {
        connectIqCaptureWebsockect();
        $captureIOLogContent.empty();
        changeState(debugStopText, iqCaptureTabName);
        resizeCallback(); 
    }
    showMsg(response["message"]);
}

function checkBler() {
    var url = $("#check_bler_url").val();
    var csrfToken = $("#csrf_token").val();
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, checkBlerSuccessCallback, failedCallback)
}

function checkBlerSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "error") {
        changeState(debugStartText, blerCheckTabName);
    } else if (type === "success") {
        blerChart.clearData();
        connectBlerCheckWebsockect();
        changeState(debugStopText, blerCheckTabName);
        resizeCallback(); 
    }
    showMsg(response["message"]);
}

function showStopCarrierActivateConfirm() {
    initConfirmBox(stopCarrierActivate);
    showConfirm("Are your sure to stop running?");
}

function stopCarrierActivate() {
    var url = $("#stop_debug_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, stopCarrierActivateSuccessCallback, failedCallback)
}

function stopCarrierActivateSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "error") {
        changeState(debugStartText, carrierActivateTabName);
    } else if (type === "success") {
        closeCarrierActivateWebsocket();
        changeState(debugStartText, carrierActivateTabName);
        resizeCallback(); 
    }
    showMsg(response["message"]);
}

function showStopIqCaptureConfirm() {
    initConfirmBox(stopIqCapture);
    showConfirm("Are your sure to stop running?");
}

function stopIqCapture() {
    var url = $("#stop_debug_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, stopIqCaptureSuccessCallback, failedCallback)
}

function stopIqCaptureSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "error") {
        changeState(debugStartText, iqCaptureTabName);
    } else if (type === "success") {
        closeIqCaptureWebsocket();
        changeState(debugStartText, iqCaptureTabName);
        resizeCallback(); 
    }
    showMsg(response["message"]);
}

function showStopCheckBlerConfirm() {
    initConfirmBox(stopCheckBler);
    showConfirm("Are your sure to stop running?");
}

function stopCheckBler() {
    var url = $("#stop_check_bler_url").val();
    var csrfToken = $("#csrf_token").val();
    //$(logContentId).empty()
    var type = "post"
    var paramData = {
        "csrf_token": csrfToken
    }
    DoAjax(url, type, paramData, stopBlerCheckSuccessCallback, failedCallback)
}

function stopBlerCheckSuccessCallback(response, textStatus, jqxhr) {
    var type = response["type"];
    if (type === "error") {
        changeState(debugStartText, blerCheckTabName);
    } else if (type === "success") {
        closeBlerCheckWebsocket();
        changeState(debugStartText, blerCheckTabName);
        resizeCallback(); 
    }
    showMsg(response["message"]);
}

function isCarrierActivateTabRunning() {
    isActivationRunning = getTabStatus(carrierActivateTabStatusId) === runningStatus;
    return isActivationRunning;
}

function isIqCaptureTabRunning() {
    isCaptureIqRunning = getTabStatus(iqCaptureTabStatusId) === runningStatus;
    return isCaptureIqRunning;
}

function isBlerCheckTabRunning() {
    isCheckBlerRunning = getTabStatus(blerCheckTabStatusId) === runningStatus;
    return isCheckBlerRunning;
}

function isThereDebugTabRunning() {
    isActivationRunning = isCarrierActivateTabRunning();
    isCaptureIqRunning = isIqCaptureTabRunning();
    isCheckBlerRunning = isBlerCheckTabRunning();
    return isActivationRunning || isCaptureIqRunning || isCheckBlerRunning
}

function disableDebugComponents() {
    disableTab("runnerLi");

    currentDebugTab = getCurrentTab();
    currentBtn = runCarrierActivationBtn;
    currentBtnIcon = "activateBtn"
    var carrerActivateTabIndex = getTabIndex(carrierActivateTabName);
    var iqCaptureTabIndex = getTabIndex(iqCaptureTabName);
    var blerCheckTabIndex = getTabIndex(blerCheckTabName);
    if (currentDebugTab == carrierActivateTabName) {
        $("#carrierActivation select").selectmenu('disable');
        debugTabs.disableTab(iqCaptureTabIndex); //disable 'IQ Data Capture' tab
        debugTabs.disableTab(blerCheckTabIndex); //disable 'BLER Check' tab
    } else if (currentDebugTab == iqCaptureTabName) {
        debugTabs.disableTab(carrerActivateTabIndex); //disable 'Carrier Activate' tab
    } else if (currentDebugTab == blerCheckTabName) {
        debugTabs.disableTab(carrerActivateTabIndex); //disable 'Carrier Activate' tab
    }
}

function enableDebugComponents() {
    if (!isThereDebugTabRunning()) {
        enableTab("runnerLi");
    }

    currentDebugTab = carrierActivateTabName
    crrntDebugTab = getCurrentTab();
    if (crrntDebugTab.length > 0) {
        currentDebugTab = crrntDebugTab;
    }
    currentBtn = runCarrierActivationBtn;
    currentBtnIcon = "activateBtn"
    var carrerActivateTabIndex = getTabIndex(carrierActivateTabName);
    var iqCaptureTabIndex = getTabIndex(iqCaptureTabName);
    var blerCheckTabIndex = getTabIndex(blerCheckTabName);
    if (currentDebugTab == carrierActivateTabName) {
        $("#carrierActivation select").selectmenu('enable');
        debugTabs.enableTab(iqCaptureTabIndex); //enable 'IQ Data Capture' tab
        debugTabs.enableTab(blerCheckTabIndex); //enable 'BLER Check' tab
    } else if (currentDebugTab == iqCaptureTabName && !isBlerCheckTabRunning()) {
        debugTabs.enableTab(carrerActivateTabIndex); //enable 'Carrier Activate' tab
    } else if (currentDebugTab == blerCheckTabName && !isIqCaptureTabRunning()) {
        debugTabs.enableTab(carrerActivateTabIndex); //enable 'Carrier Activate' tab
    }
}

function getCurrentTab() {
    currentDebugTab = carrierActivateTabName
    returnedTab = debugTabs.getCurrentTab();
    if (returnedTab.length > 0) {
        currentDebugTab = returnedTab;
    }
    return currentDebugTab;
}

function changeState(btnText, tabName) {
    currentDebugTab = getCurrentTab();
    currentBtn = runCarrierActivationBtn;
    currentBtnIcon = "activateBtn"
    if (currentDebugTab != tabName) {
        var tabIndex = getTabIndex(tabName);
        debugTabs.setActiveTab(tabIndex);
        currentDebugTab = tabName;
    }
    if (currentDebugTab == carrierActivateTabName) {
        currentBtn = runCarrierActivationBtn;
        currentBtnIcon = "activateBtn"
    } else if (currentDebugTab == iqCaptureTabName) {
        currentBtn = startCaptureIQBtn;
        currentBtnIcon = "captureBtn"
    } else if (currentDebugTab == blerCheckTabName) {
        currentBtn = startCheckBlerBtn;
        currentBtnIcon = "checkBtn"
    }
    
    if (btnText === debugStopText) {
        changeRunningStatus(tabName, runningStatus);
        currentBtn.setText(debugStopText);
        currentBtn.setPrimaryIcon("stopBtn");
        disableDebugComponents();
    } else if (btnText === debugStartText) {
        changeRunningStatus(tabName, stoppedStatus);
        currentBtn.setText(debugStartText);
        currentBtn.setPrimaryIcon(currentBtnIcon);
        enableDebugComponents();
    }
}

function changeRunningStatus(pTabName, pStatus) {
    if (pTabName == carrierActivateTabName) {
        setTabStatus(carrierActivateTabStatusId, pStatus);
    } else if (pTabName == iqCaptureTabName) {
        setTabStatus(iqCaptureTabStatusId, pStatus);
    } else if (pTabName == blerCheckTabName) {
        setTabStatus(blerCheckTabStatusId, pStatus);
    }
}

function activateCarrierWSCallback(message) {
    if (message.startsWith("Done with return code")) {
        changeState(debugStartText, carrierActivateTabName)
        showMsg(message);
        closeCarrierActivateWebsocket();
    } else {
        appendDebugMessage($activateCarrierLogContent, escapeHtml(message));
    }
}

function captureIqWSCallback(message) {
    if (message.startsWith("Done with return code")) {
        changeState(debugStartText, iqCaptureTabName)
        showMsg(message);
        closeIqCaptureWebsocket();
    } else {
        appendDebugMessage($captureIOLogContent, escapeHtml(message));
    }
}

function checkBlerWSCallback(response) {
    var type = response["type"];
    var message = response["message"]
    if (type === "error") {
        showMsg(message);
    } else if (type === "os_error") {
        changeState(debugStartText, blerCheckTabName)
        showMsg(message);
        closeBlerCheckWebsocket();
    } else if (type === "success") {
        blerChart.addData(message)
    }
}

function appendDebugMessage(pTa, pMessage) {
    if (pTa.val().length > 0) {
        pTa.prepend("\n" + pMessage);
    } else {
        pTa.prepend(pMessage);
    }
}

function initCarrierActivateWebSocket() {
    debugWebsocket = new RfWebSocket(webSocketFullUrl, "carrier_activation_message");
	debugWebsocket.setMessageCallback(activateCarrierWSCallback);
}

function connectCarrierActivateWebsockect() {
    if (!carrierActivateWebsocket || !carrierActivateWebsocket.isConnected()) {
        initCarrierActivateWebSocket();
    }
}

function closeCarrierActivateWebsocket() {
    if(carrierActivateWebsocket && carrierActivateWebsocket.isConnected) {
		carrierActivateWebsocket.close();
	}
}

function initIqCaptureWebSocket() {
    iqCaptureWebsocket = new RfWebSocket(webSocketFullUrl, "iq_capture_message");
	iqCaptureWebsocket.setMessageCallback(captureIqWSCallback);
}

function connectIqCaptureWebsockect() {
    if (!iqCaptureWebsocket || !iqCaptureWebsocket.isConnected()) {
        initIqCaptureWebSocket();
    }
}

function closeIqCaptureWebsocket() {
    if(iqCaptureWebsocket && iqCaptureWebsocket.isConnected) {
		iqCaptureWebsocket.close();
	}
}

function initBlerCheckWebSocket() {
    blerCheckWebsocket = new RfWebSocket(webSocketFullUrl, "bler_check_message");
	blerCheckWebsocket.setMessageCallback(checkBlerWSCallback);
}

function connectBlerCheckWebsockect() {
    if (!blerCheckWebsocket || !blerCheckWebsocket.isConnected()) {
        initBlerCheckWebSocket();
    }
}

function closeBlerCheckWebsocket() {
    if(blerCheckWebsocket && blerCheckWebsocket.isConnected) {
		blerCheckWebsocket.close();
	}
}

function setDebugCompomentInitStatus() {
    var status = getTabStatus(carrierActivateTabStatusId);
    if (status === runningStatus) {
        var tabIndex = getTabIndex(carrierActivateTabName);
        //debugTabs.setActiveTab(carrierActivateTabName);
        debugTabs.setActiveTab(tabIndex);
        changeState(debugStopText, carrierActivateTabName)
        initCarrierActivateWebSocket();
    }
    status = getTabStatus(iqCaptureTabStatusId);
    if (status === runningStatus) {
        var tabIndex = getTabIndex(iqCaptureTabName);
        //debugTabs.setActiveTab(iqCaptureTabName);
        debugTabs.setActiveTab(tabIndex);
        changeState(debugStopText, iqCaptureTabName)
        initIqCaptureWebSocket();
    }
    status = getTabStatus(blerCheckTabStatusId);
    if (status === runningStatus) {
        var tabIndex = getTabIndex(blerCheckTabName);
        //debugTabs.setActiveTab(blerCheckTabName);
        debugTabs.setActiveTab(tabIndex);
        changeState(debugStopText, blerCheckTabName)
        initBlerCheckWebSocket();
    }
}

function getTabStatus(pTabStatusId) {
    return $("#"+ pTabStatusId).val();
}

function setTabStatus(pTabStatusId, pValue) {
    $("#"+ pTabStatusId).val(pValue);
}

