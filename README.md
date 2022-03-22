SETUP instructions:
- install Docker and make sure it's running
- download "Get cookies.txt" browser plugin and save your facebook login cookies to ./fbrelay_ssb/.ssbshared/cookies.txt
- install python 3
- run GUI.py
- input the name of the page you want to relay on ssb. Example, if you want to relay https://www.facebook.com/YourPageIsFunny, then the name is "YourPageIsFunny"

Known issues:
- pages containing '-' aren't relayed correctly at the moment, this is a known issue.