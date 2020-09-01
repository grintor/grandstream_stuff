# grandstream_stuff
A few things I have put together for the GDS systems to work with a raspberry pi

alarm2door.service goes in /etc/systemd/system/
alarm2door.py goes in /opt/

sudo systemctl daemon-reload
sudo systemctl enable alarm2door
sudo systemctl restart alarm2door

to tail the log:
journalctl -u alarm2door.service -f

