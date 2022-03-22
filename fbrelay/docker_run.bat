set /p channelname="Facebook page name: "
set SSBLOCATION=%cd%\\..\\fbrelay_ssb\\%channelname%
mkdir %SSBLOCATION%
set SSBSHAREDLOCATION=%cd%\\..\\fbrelay_ssb\\.ssbshared
mkdir %SSBSHAREDLOCATION%
docker run --name %channelname%.fbrelay.container ^
	--expose 8008 ^
	--restart unless-stopped ^
	--mount type=bind,source=%SSBLOCATION%,target=/root/.ssb ^
	--mount type=bind,source=%SSBSHAREDLOCATION%,target=/root/.ssbshared ^
	--network fbrelaynet ^
	--sysctl net.core.somaxconn=50000 ^
    --sysctl net.ipv4.tcp_max_syn_backlog=30000 ^
    --sysctl net.ipv4.tcp_fin_timeout=10 ^
    --sysctl net.ipv4.tcp_tw_reuse=1 ^
    --sysctl net.netfilter.nf_conntrack_tcp_timeout_time_wait=5 ^
	fbrelay.image "%channelname%" "30"
pause