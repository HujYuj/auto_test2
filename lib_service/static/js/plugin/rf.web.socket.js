function RfWebSocket(pWsUrl, pEventType) { 
	this.socket = null;
	this.wsUrl = pWsUrl;
    this.eventType = pEventType;
	this.messageCallback;
	this.init();
}

RfWebSocket.prototype.init = function() {
	this.socket = io.connect(this.wsUrl, {transports: ['websocket']});
	var _this = this;
    
	this.socket.on('connect', function() {
		console.log(_this.wsUrl + ' web socket opened!');
	});
	this.socket.on('disconnect', function() {
		console.log(_this.wsUrl + ' web socket disconnected!');
	});
	this.socket.on(this.eventType, function(message) {
        if(_this.messageCallback) {
			_this.messageCallback(message);	
		}
	});
}

RfWebSocket.prototype.setMessageCallback = function(pMessageCallback) {
    this.messageCallback = pMessageCallback;
	this.socket.onmessage = pMessageCallback;
}

RfWebSocket.prototype.send = function(data) {
	this.socket.send(data);
}

RfWebSocket.prototype.isConnected = function() {
	return this.socket.connected;
}

RfWebSocket.prototype.close = function() {
	this.socket.disconnect();
}