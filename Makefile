
link:
	rm garethweb/public/bootstrap
	ln -s "${PWD}/bootstrap/bootstrap/" garethweb/public/bootstrap
	ln -s "${PWD}/bootstrap/js/bootstrap-alert.js" garethweb/public/themes/bootstrap/js/bootstrap-alert.js

.PHONY: link
