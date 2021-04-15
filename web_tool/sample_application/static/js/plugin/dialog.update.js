/**
 * dialog.update.js
 * Copyright (c) 2020 NOKIA
 *
 * @author Wang, Fuqiang Q. (NSB - CN/Hangzhou) <fuqiang.q.wang@nokia-sbell.com>
 */

function UpdateDialog(pUpdateDiagID, pVersioDiagID, pForceConfirmDialogID, pDialogWidth, pProcessbarID, pCheckUrl, pUpdateUrl) {
	this._updateDialog   = $(pUpdateDiagID);
    this._versionDialog   = $(pVersioDiagID);
    this._forceConfirmDialog = $(pForceConfirmDialogID);
    this._dialogWidth = pDialogWidth;
    this._processbar = $(pProcessbarID);
    this._processbarContainer = $(pProcessbarID).parent();
    this._processbarLabel = $(pProcessbarID).prev();
    this._checkUrl = pCheckUrl;
    this._updateUrl = pUpdateUrl;

    this._checkVersionCallback;

    this._beforeSendCallback;
    this._successCallback;
    this._errorCallback;
    this._ajaxRequestData;

    this._isDialogShown = false;
    this._isGoingOn = false;
    this._isDone = false;

    this._timeout = 30 * 1000;

    this._updateType = this.AUTO_UPDATE_TYPE_AUTO;

    this._verInfo;
    this._verMessage;

    this._updateOKBtnID = "updateOKBtn";
    this._updateUpdateBtnID = "updateUpdateBtn";
    this._updateCancelBtnID = "updateCancelBtn";
    this._updateDetailBtnID = "updateDetailBtn";
    this._request_data;

	var _this = this;

    this._versionDialog.dialog({
        resizable: false,
        autoOpen: false,
        height: "auto",
        width    : _this._dialogWidth,
        modal: false,
		open: function(){
			_this.updateVersionDialogPosition();
		}
    });
    this._versionDialog.dialog("widget").find(".ui-dialog-titlebar").hide();

    this._updateDialog.dialog({
        resizable: false,
        autoOpen: false,
        height: "auto",
        width: _this._dialogWidth,
        modal: true,
        draggable: false,
        buttons: {
            "Update" : {
                text: "Update",
                id: _this._updateUpdateBtnID,
                click: function() {
                    _this.checkStatus();
                    $( this ).dialog( "close" );
                }
            },
            "OK" : {
                text: "OK",
                id: _this._updateOKBtnID,
                click: function() {
                    $( this ).dialog( "close" );
                }
            },
            "Cancel" : {
                text: "Cancel",
                id:  _this._updateCancelBtnID,
                click: function() {
                    $( this ).dialog( "close" );
                }
            },
            "Detail" : {
                text: "Detail",
                id: _this._updateDetailBtnID,
                click: function() {
                    var isOpen = _this._versionDialog.dialog( "isOpen" );
                    if (isOpen) {
                        _this._versionDialog.dialog( "close" );
                    } else {
                        _this._versionDialog.dialog( "open" );
                    }
                }
            }
        },
        close: function( event, ui ) {
           _this._versionDialog.dialog( "close" );
        }
    });

    this._forceConfirmDialog.dialog({
        resizable: false,
        autoOpen: false,
        height: "auto",
        width: _this._dialogWidth,
        modal: true,
        draggable: false,
        buttons: {
            "Yes" : {
                text: "Yes",
                click: function() {
                    _this.update();
                    $( this ).dialog( "close" );
                }
            },
            "No" : {
                text: "No",
                click: function() {
                    $( this ).dialog( "close" );
                }
            }
        }
    });

    this._processbarContainer.dialog({
        resizable: false,
        autoOpen: false,
        height: "auto",
        width: _this._dialogWidth,
        modal: true,
        draggable: false,
        buttons: _this.processbarContainerCancelButtons
    });
    this._processbarContainer.dialog("widget").find(".ui-dialog-titlebar-close").hide();

    this._processbar.progressbar({
        value: false,
        complete: function() {
            _this._processbarContainer.dialog( "option", "buttons", _this.processbarContainerCloseButtons);
        }
    });
}

UpdateDialog.prototype.AUTO_UPDATE_TYPE_AUTO = "auto";
UpdateDialog.prototype.AUTO_UPDATE_TYPE_MANUAL = "manual";

UpdateDialog.prototype.setOperationTimeout = function (pTimeout){
   this._timeout = pTimeout;
};

UpdateDialog.prototype.setCheckVersionCallback = function (pCheckVersionCallback){
   this._checkVersionCallback = pCheckVersionCallback;
};

UpdateDialog.prototype.callCheckVersionCallback = function (pNewVersionAvailable, pLatestVersion){
    if(this._checkVersionCallback) {
        this._checkVersionCallback(pNewVersionAvailable, pLatestVersion);
    }
};

UpdateDialog.prototype.setDialogShown = function (pIsDialogShown){
    this._isDialogShown = pIsDialogShown;
};

UpdateDialog.prototype.isGoingOn = function (){
   return this._isGoingOn;
};

UpdateDialog.prototype.processbarContainerCancelButtons = [{
    //text: "Cancel Update",
    text: "Close",
    click: function() {
        //_this.update(true);
        $( this ).dialog( "close" );
        //console.info("Update Cancel to be implemented.");
    }
}];

UpdateDialog.prototype.processbarContainerCloseButtons = [{
    text: "Close",
    click: function() {
        $( this ).dialog( "close" );
    }
}];

UpdateDialog.prototype.showProcessbar = function () {
    this._processbarLabel.text( "Updating..." );
	this._processbar.progressbar( "option", "value", false );
    this._processbarContainer.dialog( "option", "buttons", this.processbarContainerCancelButtons);
    this._processbarContainer.dialog( "open" );
};


UpdateDialog.prototype.setUpdateType = function (pUpdatType) {
    this._updateType   = pUpdatType;
};

UpdateDialog.prototype.getUpdateType = function () {
    return this._updateType;
};

UpdateDialog.prototype.checkVersion = function (pType, pData) {
    if (this._isDone && pType == UpdateDialog.prototype.AUTO_UPDATE_TYPE_MANUAL) {
        this._processbarContainer.dialog( "open" );
        return;
    }

    if (pType) {
        this._updateType =  pType;
    } else {
        this._updateType =  this.AUTO_UPDATE_TYPE_AUTO;
    }

    if (pData) {
        this._request_data = new Array();
        this._request_data.push(pData);
    }

	var _aArr = new Array();
    if (this._request_data) {
        _aArr.push(this._request_data);
    }
	_aArr.push("operation=checkVersion");

    var csrfToken = $("#csrf_token").val();
    var paramData = {
        "csrf_token": csrfToken
    }
    _aArr.push("csrf_token="+csrfToken);
	var _req = _aArr.join("&").toString();
	_aArr = null;

    this._ajaxRequestData = _req;
    this._beforeSendCallback = this.checkVersionBeforeSendCallback;
    this._successCallback = this.checkVersionSuccCallback;
    this._errorCallback = this.defaultErrorCallback; //Added for TAD331#2.Add timeout for ajax request in update plugin. Wang Fuqiang 2017.10.24
    this.sendPostAjaxRequest(this._checkUrl);
};

UpdateDialog.prototype.checkVersionBeforeSendCallback = function () {
    if (this.updateThat._isDialogShown && this.updateThat._updateType === this.updateThat.AUTO_UPDATE_TYPE_MANUAL) {
        this.updateThat.showUpdateMessage("Checking version...");
    }
    this.updateThat._isGoingOn = true;
    this.updateThat._isDone = false;
};

UpdateDialog.prototype.checkVersionSuccCallback = function (data) {
    var isNewVersionAvailable = false;
    var tip, verMessage, message;
    var isJson = this.updateThat.isJson(data);
    if (isJson) {
        var verJSON = JSON.parse(data);
        if (verJSON.version && verJSON.message) { //new version available
            this.updateThat._verInfo = verJSON.version;

            verMessage = verJSON.message;
            tip = verJSON.tip;
            isNewVersionAvailable = true;
        } else if (verJSON.message){ //no new version available
            message = verJSON.message;
        }
    } else {
        message = data;
    }

    if (isNewVersionAvailable) {
        this.updateThat.callCheckVersionCallback(true, this.updateThat._verInfo);
        if (this.updateThat._isDialogShown) {
            this.updateThat.showUpdateDialog(tip, verMessage);
            if (this.updateThat.updateType == UpdateDialog.prototype.AUTO_UPDATE_TYPE_AUTO) {
                this.updateThat.setUpdateType(UpdateDialog.prototype.AUTO_UPDATE_TYPE_MANUAL);
            }
        }
    } else {
        this.updateThat.callCheckVersionCallback(false);
        if (this.updateThat._isDialogShown && this.updateThat._updateType === this.updateThat.AUTO_UPDATE_TYPE_MANUAL) {
            this.updateThat.showUpdateMessage(message);
        }
    }
    this.updateThat._isGoingOn = false;
};

UpdateDialog.prototype.defaultErrorCallback = function ( jqXHR, textStatus, errorThrown) {
	console.info("checkVersion error:" + textStatus);
    var desc = this.updateThat.handleError(jqXHR, textStatus, errorThrown);

    if (this.updateThat._isDialogShown && this.updateThat._updateType === this.updateThat.AUTO_UPDATE_TYPE_MANUAL) {
        this.updateThat.showUpdateMessage( desc );
    }
    this.updateThat._isGoingOn = false;
};

UpdateDialog.prototype.handleError = function ( jqXHR, textStatus, errorThrown) {
    var desc = textStatus;

    if (jqXHR.status == 0 && textStatus == "timeout") {
        desc = "Operation timed out.";
    } else if (jqXHR.status == 0 && textStatus == "error") {
        desc = "No response from server. Please check your network connectivity.";
    } else if (jqXHR.status == 500) {
        desc =  "Error occured during update, please contact developers.";
    } else {
        console.info("Not supported status code:" + jqXHR.status + ".");
    }

    return desc;
};


UpdateDialog.prototype.showUpdateDialog = function (pTip, pVerMessage) {
    $( "#" + this._updateOKBtnID ).hide();
    $( "#" + this._updateUpdateBtnID ).show();
    $( "#" + this._updateCancelBtnID ).show();
    $( "#" + this._updateDetailBtnID ).show();
    this._updateDialog.html(pTip);
    this._updateDialog.dialog( "open" );
    this._versionDialog.html(this.getHTMLFormatMessage(pVerMessage));
};

UpdateDialog.prototype.showUpdateMessage = function (pMessage) {
    $( "#" + this._updateOKBtnID ).show();
    $( "#" + this._updateUpdateBtnID ).hide();
    $( "#" + this._updateCancelBtnID ).hide();
    $( "#" + this._updateDetailBtnID ).hide();
    this._updateDialog.html(pMessage);

    this._updateDialog.dialog( "open" );
    this._versionDialog.html("");
    this._isGoingOn = false;
};

UpdateDialog.prototype.getHTMLFormatMessage = function (pMessage) {
    var formatted = pMessage;
    if (pMessage) {
        formatted = pMessage.replace(/\n/g, "<br>")
    }
    return formatted;
};

UpdateDialog.prototype.checkStatus = function () {
	var _aArr = new Array();
    if (this._request_data) {
        _aArr.push(this._request_data);
    }
    _aArr.push("operation=checkStatus");

	var _req = _aArr.join("&").toString();
	_aArr = null;

    this._ajaxRequestData = _req;
    this._beforeSendCallback = this.checkStatusBeforeSendCallback();
    this._successCallback = this.checkStatusSuccCallback;
    this._errorCallback = this.defaultErrorCallback; //Added for TAD331#2.Add timeout for ajax request in update plugin. Wang Fuqiang 2017.10.24
    this.sendPostAjaxRequest(this._updateUrl);
};

UpdateDialog.prototype.checkStatusBeforeSendCallback = function (data) {
    this._isGoingOn = true;
};

UpdateDialog.prototype.checkStatusSuccCallback = function (data) {
    if (data == "") {
        this.updateThat.update();
    } else {
        var isJson = this.updateThat.isJson(data);
        if (isJson) { //Added for TAD330#2.Check if it's json object for returned data in update plugin. Wang Fuqiang 2017.09.18
            var resultJSON = JSON.parse(data);
            if ("status" in resultJSON) {
                this.updateThat._forceConfirmDialog.html("Dut Control is running.<br>Would you like to continue updating?");
                this.updateThat._forceConfirmDialog.dialog( "open" );
            } else {
                this.updateThat.showUpdateMessage(data);
            }
        } else {
            this.updateThat.showUpdateMessage(data);
        }
    }
    this.updateThat._isGoingOn = false;
};


UpdateDialog.prototype.update = function () {
	var _aArr = new Array();
    if (this._request_data) {
        _aArr.push(this._request_data);
    }
    _aArr.push("operation=update");
    _aArr.push("version=" + this._verInfo);
	var _req = _aArr.join("&").toString();
	_aArr = null;

    this._ajaxRequestData = _req;
    this._beforeSendCallback = this.updateBeforeSendCallback;
    this._successCallback = this.updateSuccCallback;
    this._errorCallback = this.updateErrorCallback;
    this.sendPostAjaxRequest(this._updateUrl);
};

UpdateDialog.prototype.updateBeforeSendCallback = function (data) {
    this.updateThat.showProcessbar();
    this.updateThat._isGoingOn = true;
};

UpdateDialog.prototype.updateSuccCallback = function (data) {
	console.info("update result:" + data);
    var isJson = this.updateThat.isJson(data);
    if (isJson) { //Added for TAD330#2.Check if it's json object for returned data in update plugin. Wang Fuqiang 2017.09.18
        var message;
        var resultJSON = JSON.parse(data);
        if ("result" in resultJSON) {
            message = resultJSON.result;
        } else {
            message = data;
        }
        this.updateThat._processbar.progressbar( "option", "value", 100 );
        this.updateThat._processbarLabel.text( message );
        this.updateThat._processbarContainer.dialog( "option", "buttons", this.updateThat.processbarContainerCloseButtons);
        var isOpen = this.updateThat._processbarContainer.dialog( "isOpen");
        if (!isOpen) {
            this.updateThat._processbarContainer.dialog( "open" );
        }
    } else {
        this.updateThat.showUpdateMessage(data);
    }
    this.updateThat._isGoingOn = false;
    this.updateThat._isDone = true;
};

UpdateDialog.prototype.updateErrorCallback = function ( jqXHR, textStatus, errorThrown) {
	console.info("update error:" + textStatus);
    var desc;

    if (jqXHR.status == 0 && textStatus == "error") {
        desc =  "Update done. Please refresh the page";
        console.info("TAD GUI was shut down. Connection lost.");
    } else {
        desc = this.updateThat.handleError(jqXHR, textStatus, errorThrown);
    }
    this.updateThat._processbar.progressbar( "option", "value", 100 );
    this.updateThat._processbarLabel.text( desc );
    this.updateThat._processbarContainer.dialog( "option", "buttons", this.updateThat.processbarContainerCloseButtons);
    var isOpen = this.updateThat._processbarContainer.dialog( "isOpen");
    if (!isOpen) {
        this.updateThat._processbarContainer.dialog( "open" );
    }
    this.updateThat._isGoingOn = false;
    this.updateThat._isDone = true;
};

UpdateDialog.prototype.getAjaxOptions = function (){
    var options = {
        timeout: this._timeout,
        type: 'POST',
        data : this._ajaxRequestData,
        beforeSend: this._beforeSendCallback,
        success: this._successCallback,
        error: this._errorCallback,
        updateThat: this
    };
   return options;
};

UpdateDialog.prototype.sendPostAjaxRequest = function (pUrl){
   $.ajax(pUrl, this.getAjaxOptions());
};

UpdateDialog.prototype.updateVersionDialogPosition = function (){
    var updateDlgContainer = this._updateDialog.parent();
    var updateDlgContainerOffset = updateDlgContainer.offset();
    var updateDlgContainerHeight = updateDlgContainer.outerHeight();
    var topPosition = updateDlgContainerOffset.top + updateDlgContainerHeight;

    var versionDlgContainer = this._versionDialog.parent();
    versionDlgContainer.css({
        top: topPosition,
        left: updateDlgContainerOffset.left
    });
};

UpdateDialog.prototype.isJson = function (str){
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
};
