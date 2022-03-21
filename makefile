dl:
	rsync -aiv --delete do-me-crypto-00:/var/www/pyys/tg_listener/storage/bot.session storage/
up:
	rsync -aiv --delete storage/bot.session do-me-crypto:/var/www/pyys/tg_listener/storage/
