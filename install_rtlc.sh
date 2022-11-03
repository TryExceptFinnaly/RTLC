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
ExecStart=$INSTALL_PATH/rtlc\n\n\
[Install]\n\
WantedBy=multi-user.target' > /etc/systemd/system/$SERVICE_NAME.service"

echo $PASS | sudo -S install -d -o $RTLC_USER -g $RTLC_USER -m 0755 $INSTALL_PATH

cp ./rtlc $INSTALL_PATH 
chmod 755 $INSTALL_PATH/rtlc

echo $PASS | sudo -S systemctl daemon-reload
echo $PASS | sudo -S systemctl enable $SERVICE_NAME
echo $PASS | sudo -S systemctl start $SERVICE_NAME
echo $PASS | sudo -S systemctl status $SERVICE_NAME

echo 'File "config.ini" not found, modify the generated config file ("'$INSTALL_PATH'")'
