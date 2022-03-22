docker run --name fbrelayhub.container ^
	--mount type=bind,source=%cd%\\.ssb,target=/root/.ssb ^
	--ip 172.24.81.192 ^
	--network fbrelaynet ^
	--sysctl net.core.somaxconn=50000 ^
    --sysctl net.ipv4.tcp_max_syn_backlog=30000 ^
    --sysctl net.ipv4.tcp_fin_timeout=10 ^
    --sysctl net.ipv4.tcp_tw_reuse=1 ^
    --sysctl net.netfilter.nf_conntrack_tcp_timeout_time_wait=5 ^
	fbrelayhub.image
pause