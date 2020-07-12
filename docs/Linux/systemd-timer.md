<!--
::::::::::::::
systemd-timers/backup_container_data.service
::::::::::::::
[Unit]
Description=Backup container data.

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup_container_data.sh
::::::::::::::
systemd-timers/backup_container_data.timer
::::::::::::::
[Unit]
Description=Backup container data.

[Timer]
OnCalendar=weekly
Persistent=true
RandomizedDelaySec=1h

[Install]
WantedBy=timers.target
::::::::::::::
systemd-timers/update_dns.service
::::::::::::::
[Unit]
Description=Update DNS record to MyDNS.jp.

[Service]
Type=oneshot
ExecStart=/usr/bin/curl "https://username@ipv4.mydns.jp/login.html"
::::::::::::::
systemd-timers/update_dns.timer
::::::::::::::
[Unit]
Description=Update DNS record to MyDNS.jp.

[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=10m

[Install]
WantedBy=timers.target
-->
