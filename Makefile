SYSTEMD_DIR=${HOME}/.config/systemd/user
BIN_DIR=${HOME}/.local/bin

install:
	install -D -t ${SYSTEMD_DIR} sunset.service sunset.timer
	install -D -m 0755 sunset.py ${BIN_DIR}/sunset.py
	systemctl --user daemon-reload
	systemctl --user enable sunset.timer
	systemctl --user start sunset.timer

uninstall:
	systemctl --user disable sunset.timer
	rm -rf ${SYSTEMD_DIR}/sunset.{service,timer}
	rm -rf ${BIN_DIR}/sunset.py
	systemctl --user stop sunset.timer
	systemctl --user daemon-reload
