function RfTab(pTabDivId, pIsVertical) {
    this._tabDivId = pTabDivId;
    this._beforeActivateCallBack = null;
    this._activateCallBack = null;
    this._isVertical = pIsVertical
    this._currentTabName = ""
    
    this.initTab();
}

RfTab.prototype.initTab = function () {
    var _this = this;
    $( this._tabDivId ).tabs({
        active: 0,
        beforeActivate: function( event, ui ) {
            var isEnable = true;
            if (_this._beforeActivateCallBack) {
                var newTab = ui.newTab.text();
                isEnable = _this._beforeActivateCallBack(newTab);
            }
            if (isEnable) {
                _this._initBase = getBase();
                clearBase();
            }
            return isEnable;
        },
        activate: function( event, ui ) {
            _this._currentTabName = ui.newTab.text();
            if (_this._activateCallBack) {
                var newTab = _this._currentTabName;
                _this._activateCallBack(newTab);
            }
        }
    });
    if (this._isVertical) {
        $( this._tabDivId ).tabs().addClass( "ui-tabs-vertical ui-helper-clearfix" );
        $( this._tabDivId + " li" ).removeClass( "ui-corner-top" ).addClass( "ui-corner-left" );    
    }
};

RfTab.prototype.setBeforeActivateCallback = function(pBeforeActivateCallBack) {
	this._beforeActivateCallBack = pBeforeActivateCallBack;
};

RfTab.prototype.setActivateCallback = function(pActivateCallBack) {
	this._activateCallBack = pActivateCallBack;
};

RfTab.prototype.disableTabs = function(pDisabledTabsIndexes) {
	if (pDisabledTabsIndexes) {
		var indexes = pDisabledTabsIndexes.split(",");
		if (indexes) {
			for (var i = 0; i < indexes.length; i++) {
				$( this._tabDivId ).tabs( "disable", parseInt(indexes[i].trim()));
			}
		}
	}
	
};

RfTab.prototype.enableTabs = function(pEnabledTabsIndexes) {
	if (pEnabledTabsIndexes) {
		var indexes = pEnabledTabsIndexes.split(",");
		if (indexes) {
			for (var i = 0; i < indexes.length; i++) {
				$( this._tabDivId ).tabs( "enable", parseInt(indexes[i].trim()));
			}
		}
	}
};

RfTab.prototype.disableAllTabs = function() {
	$( this._tabDivId ).tabs( "disable" );
};

RfTab.prototype.enableAllTabs = function() {
	$( this._tabDivId ).tabs( "enable" );
};

RfTab.prototype.disableTab = function(pDisabledTabIndex) {
	$( this._tabDivId ).tabs( "disable", pDisabledTabIndex);
};

RfTab.prototype.enableTab = function(pEnabledTabIndex) {
	$( this._tabDivId ).tabs( "enable", pEnabledTabIndex);
};

RfTab.prototype.setActiveTab = function(pActiveTabIndex) {
	$( this._tabDivId ).tabs( "option", "active", pActiveTabIndex );
};

RfTab.prototype.getCurrentTab = function() {
	return this._currentTabName;
};

