/**
 * FilerableSelectize.js
 * Copyright (c) 2020 NOKIA
 *
 * @author Wang, Fuqiang Q. (NSB - CN/Hangzhou) <fuqiang.q.wang@nokia-sbell.com>
 */


function FilterableSelectize(pID, pValueField, pLabelField, pChangable, pIsList, pAddOptionCallback, pIsRemoveBtnVisible) {
    this._valueField = "value";
    if (pValueField) {
        this._valueField = pValueField;
    }
    
    this._labelField = "text";
    if (pLabelField) {
        this._labelField = pLabelField;
    }
    
    this._changable = false;
    if (pChangable) {
        this._changable = pChangable;
    }
    
    this._isLIst = false;
    if (pIsList) {
        this._isLIst = pIsList;
    }
    
    this._addOptionCallback = null;
    if (pAddOptionCallback) {
        this._addOptionCallback = pAddOptionCallback;
    }
    
    this._plugins = [];
    if (pIsRemoveBtnVisible) {
        this._plugins.push("remove_button");
    }
    
	var _this = this;
    
	// initial
    if (_this._addOptionCallback) {
        this._selectize = $(pID).selectize({
            valueField: _this._valueField,
            labelField: _this._labelField,
           searchField: _this._labelField,
                create: _this._changable,
                isList: _this._isLIst,
                create: function(input, callback) {
                    return _this._addOptionCallback(input);
                },
                plugins: _this._plugins
        })[0].selectize;
    } else {
        this._selectize = $(pID).selectize({
            valueField: _this._valueField,
            labelField: _this._labelField,
           searchField: _this._labelField,
                create: _this._changable,
                isList: _this._isLIst,
                plugins: _this._plugins
        })[0].selectize;
    }
    
}

FilterableSelectize.prototype.addEvent = function (pEventName, pHandler) {
	this._selectize.on(pEventName, pHandler);
};

FilterableSelectize.prototype.removeEvent = function (pEventName) {
	this._selectize.off(pEventName);
};

FilterableSelectize.prototype.destroy = function () {
	this._selectize.destroy();
};

FilterableSelectize.prototype.enable = function() {
	this._selectize.enable();
};

FilterableSelectize.prototype.disable = function() {
	this._selectize.disable();
};

FilterableSelectize.prototype.getValue = function () {
	return this._selectize.getValue();
};

FilterableSelectize.prototype.setValue = function (pValue, pSilent) {
	this._selectize.setValue(pValue, pSilent);
};

FilterableSelectize.prototype.getItem = function (pValue) {
	return this._selectize.getOption(pValue);
};

FilterableSelectize.prototype.clear = function (pSilent) {
	this._selectize.clear(pSilent);
};

FilterableSelectize.prototype.getSelectedJSONOptions = function (pIsRemovable) {
    var values = this._selectize.getValue();
	return this.generateJSONOptions(values, pIsRemovable);
};

FilterableSelectize.prototype.setValueField = function (pValueField) {
	this._selectize.settings.valueField = pValueField;
};

FilterableSelectize.prototype.setLabelField = function (pLabelField) {
	this._selectize.settings.labelField = pLabelField;
};

FilterableSelectize.prototype.addOption = function (pData) {
	this._selectize.addOption(pData);
    this._selectize.refreshOptions(false);
};

FilterableSelectize.prototype.removeOption = function (pValue, pSilent) {
	//this._selectize.removeItem(pValue, pSilent);
    this._selectize.removeOption(pValue);
};

FilterableSelectize.prototype.removeAllOptions = function (pSilent) {
    if (typeof pSilent === "boolean"){
      this._selectize.clear(pSilent);
    } else {
        this._selectize.clear();
    }
    this._selectize.clearOptions();
    this._selectize.refreshOptions(false);
    
};

FilterableSelectize.prototype.getAllValues = function () {
    return this._selectize.getAllValues();
};

FilterableSelectize.prototype.getSize = function () {
    return this._selectize.getSize();
};

FilterableSelectize.prototype.getAllJSONOptions = function (pIsRemovable) {
    var values = this._selectize.getAllValues();
	return this.generateJSONOptions(values, pIsRemovable);
};

FilterableSelectize.prototype.generateJSONOptions = function (pValues, pIsRemovable) {
    var jsonOption;
    if (pValues) {
        jsonOption = [];  
        if (typeof pValues === 'string') {
            pValues = pValues.split(this._selectize.settings.delimiter);
        }
        for (var i = 0; i < pValues.length; i++) { 
            var value = pValues[i];
            //var text = this._selectize.getItem(value)[0].innerHTML;
            var text = this._selectize.getTextByValue(value);
            var item = {}
            item [this._valueField] = value;
            item [this._labelField] = text;
            jsonOption.push(item);
        }
        if (pIsRemovable && typeof pIsRemovable == typeof true) {
            for (var j = pValues.length; j >= 0; j--) { 
                this.removeOption(pValues[j]);
            }
        }
    }
	return jsonOption;
};
