function Button(pID) {
	jQButton.call(this, pID);
    this.setAvailability();
}

Button.prototype = new jQButton();

