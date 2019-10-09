
# VPNサーバの代替設定
プライマリVPNサーバが落ちた時にRaspberry Piなどで自動でPPPoE接続し、代替VPNサーバが立ち上がるように設定  

* PPPoE接続+VPNサーバ起動&停止スクリプト  

	!!! example "check_vpn.sh"
		<script src="https://gist.github.com/roy-n-roy/032f1df08654a6aeb276aebb2ffeb871.js?file=check_vpn.sh"></script>

* Systemd自動起動 設定ファイル  

	!!! example "check_vpn.service"
		<script src="https://gist.github.com/roy-n-roy/032f1df08654a6aeb276aebb2ffeb871.js?file=check_vpn.service"></script>
