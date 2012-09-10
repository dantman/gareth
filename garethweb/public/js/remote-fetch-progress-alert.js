(function($, io) {
	$(function() {
		io.connect('/fetchprogress')
			.on('connect', function() {
				// this.emit('subscribe', { remote: ... });
			})
			.on('progress', function() {
				
			});
	});
})(jQuery, io);