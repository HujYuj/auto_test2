function jQButton(pID) {
	this._component = $(pID);
    this._component.button();
    this.setState(false);
}

jQButton.prototype.setPrimaryIcon = function(iconClass) {
	this._component.button({
        icons: {
            primary: iconClass   // Custom icon
        }});
};

jQButton.prototype.bind = function(pClickHandler) {
	this._component.unbind();
	this._component.bind("click", pClickHandler);
};

jQButton.prototype.IsEnabled = function() {
	return !this._component.button( "option", "disabled" );;
};

jQButton.prototype.setState = function(pEnabled) {
    if (pEnabled) {
        this._component.button( "enable" );
    } else {
        this._component.button( "disable" );
    }
};

jQButton.prototype.enable = function() {
    this.setState(true)
};

jQButton.prototype.disable = function() {
    this.setState(false)
};

jQButton.prototype.hide = function() {
	this._component.hide();
};

jQButton.prototype.show = function() {
	this._component.show();
};

jQButton.prototype.setAvailability = function() {
    this.setState(this.IsEnabled());
};

jQButton.prototype.getText = function() {
    return this._component.text();
};

jQButton.prototype.setText = function(pNewText) {
    this._component.button("option", "label", pNewText);
};

//Added for TAD671#1.Add message filter for LCT comparing. Wang Fuqiang 2015.03.04
jQButton.prototype.isVisible = function() {
    return this._component.is(":visible");
};

//Added for TAD671#1.Add message filter for LCT comparing. Wang Fuqiang 2015.03.04
jQButton.prototype.isHidden = function() {
    return this._component.is(":hidden");
};
