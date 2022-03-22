docker network rm fbrelaynet
docker network create -d macvlan ^
	--subnet=172.24.81.0/20 ^
	--gateway=172.24.81.1 ^
	--aux-address="host=172.24.81.223" ^
	-o macvlan_mode=bridge ^
	-o parent=eth0 fbrelaynet
pause