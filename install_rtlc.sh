read -r -p 'Enter working directory (default is /srv/rtlc/): ' INSTALL_PATH
if [[ $INSTALL_PATH = '' ]]
then
	INSTALL_PATH="/srv/rtlc/"
fi
INSTALL_PATH=$(echo $INSTALL_PATH | sed 's/\/$//')
echo -e "\
[Unit]\n\
Description=rtlc.service\n\n\
[Service]\n\
Type=simple\n\n\
User=lins\n\
Group=lins\n\n\
ExecStart=/usr/bin/python3 /srv/rtlc/rtlc.py\n\n\
[Install]\n\
WantedBy=multi-user.target" > /etc/systemd/system/rtlc.service

install -d -o lins -g lins -m 0755 $INSTALL_PATH

cp ./config.py ./rtlc.py $INSTALL_PATH 
chmod 755 $INSTALL_PATH/*.py
chown lins:lins $INSTALL_PATH/*.py

systemctl daemon-reload
systemctl enable rtlc
systemctl start rtlc
systemctl status rtlc

echo 'File "config.ini" not found, modify the generated config file ("'$INSTALL_PATH'/config.ini")'
