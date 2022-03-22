Scuttleface is intended to relay your favorite facebook page onto the Scuttlebutt network
For an example a running relay, check out @DGQe/A+GFqwH/gF1/39Zknel3kdko0jm2oRQToE4wj4=.ed25519 on FreeSocial (pub invite code pub.freesocial.co:8008:@ofYKOy2p9wsaxV73GqgOyh6C6nRGFM5FyciQyxwBd6A=.ed25519~ye9Z808S3KPQsV0MWr1HL0/Sh8boSEwW+ZK+8x85u9w=)

SETUP instructions:
- install Docker and make sure it's running
- download "Get cookies.txt" browser plugin and save your facebook login cookies to ./fbrelay_ssb/.ssbshared/cookies.txt
- install python 3
- run ./fbrelay/docker_createnet.bat if you're on windows, or 'docker network create fbrelaynet' in a terminal if you're on linux
- run GUI.py
- input the name of the page you want to relay on ssb. Example, if you want to relay https://www.facebook.com/YourPageIsFunny, then the name is "YourPageIsFunny"
- press "Start Relay"
- after the relay container started in docker (check the "Containers" tab in Docker) press "Ensure Invite"

Known issues:
- pages containing '-' aren't relayed correctly at the moment, this is a known bug. Feel free to fix it and submit a pull request.