
import json
import subprocess


def WaitForId():
    while True:
        x=subprocess.run(["ssb-server","whoami"],shell=False,capture_output=True,text=True)
        if not x.stderr:
            print("id: " + x.stdout)
            return json.loads(x.stdout)["id"]