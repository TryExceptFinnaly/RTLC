read -r -p 'Enter service name prefix (or leave empty): ' SERVICE_NAME
if [[ $SERVICE_NAME == '' ]]
then
	SERVICE_NAME="rtlc"
else
	SERVICE_NAME="rtlc_$SERVICE_NAME"
fi
read -r -p 'Enter working directory (default is /srv/'$SERVICE_NAME'/): ' INSTALL_PATH
printf "sudo password: "
read -s PASS
echo
RTLC_USER=`basename $MAIL`
if [[ $INSTALL_PATH == '' ]]
then
	INSTALL_PATH="/srv/$SERVICE_NAME/"
fi
INSTALL_PATH=$(echo $INSTALL_PATH | sed 's/\/$//')
echo $PASS | sudo -S bash -c "echo -e '\
[Unit]\n\
Description=$SERVICE_NAME.service\n\n\
[Service]\n\
Type=simple\n\n\
User=$RTLC_USER\n\
Group=$RTLC_USER\n\n\
ExecStart=/usr/bin/python3 $INSTALL_PATH/rtlc.py\n\n\
[Install]\n\
WantedBy=multi-user.target' > /etc/systemd/system/$SERVICE_NAME.service"

echo $PASS | sudo -S install -d -o lins -g lins -m 0755 $INSTALL_PATH

cp ./config.py ./rtlc.py $INSTALL_PATH 
chmod 755 $INSTALL_PATH/*.py
#chown lins:lins $INSTALL_PATH/*.py

echo $PASS | sudo -S systemctl daemon-reload
echo $PASS | sudo -S systemctl enable $SERVICE_NAME
echo $PASS | sudo -S systemctl start $SERVICE_NAME
echo $PASS | sudo -S systemctl status $SERVICE_NAME

echo 'File "config.ini" not found, modify the generated config file ("'$INSTALL_PATH'/config.ini")'
