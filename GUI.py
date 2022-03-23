import json
import dearpygui.dearpygui as dpg
import os
import logging
import re

def FindFreePort(existingContainers:list,start:int=8008):
    while start < 10000:
        if start in existingContainers:
            start+=1
        else:
            break
    return start

def WindowsPathToUnixMountPath(path:str):
    newpath=path
    a=os.path.splitdrive(path)
    if a:
        letter=a[0]
        tail=a[1]
        letter=letter.replace(':','')
        tail=tail.replace('\\','/')
        newpath='/mnt/'+letter+tail

    return newpath

def ImageExists(image:str):  
    stream=os.popen("docker image ls " + image +".image")    
    output = stream.read()
    found=output.find(image) 
    return found

def BuildImage(image:str):    
    thisDir=GetFileDir()
    dirpath = os.path.join(thisDir,image)
    dockerfile=os.path.join(dirpath,"Dockerfile")
    os.system("docker build -t "+image+".image -f "+dockerfile+" "+dirpath)

def EnsureImage(image:str):
    found=ImageExists(image)
    while found == -1:        
        logger = logging.getLogger()
        logger.error("Image " + image + ".image doesnt exist. building")
        BuildImage(image)

        logger.error("Build finished")
        found=ImageExists(image)
    pass

def ContainerFullName(name:str,port:int,image:str):
    strport = str(port)
    containerFullName=name + "." + strport + "."+image+".container"
    return containerFullName

def ContainerExists(name:str,port:int,image:str):
    containername=ContainerFullName(name,port,image)
    stream=os.popen("docker container ls -a")    
    output = stream.read()
    found=output.find(containername) 
    return found

def ContainerStarted(name:str,port:int,image:str):
    containername=ContainerFullName(name,port,image)
    stream=os.popen("docker container ls")    
    output = stream.read()
    found=output.find(containername) 
    return found

def StartContainer(name:str,port:int,image:str):
    containername=ContainerFullName(name,port,image)
    os.system("docker container start " + containername)


def DeleteContainer(name:str,port:int,image:str):
    containername=ContainerFullName(name,port,image)
    os.system("docker container stop "+containername)
    os.system("docker container rm "+containername)

def EnsureStartedContainer(name:str,port:int,image:str,networkname,hostmode:bool):
    DeleteContainer(name,port,image)
    found=ContainerExists(name,port,image)
    while found == -1:        
        logger = logging.getLogger()
        logger.error("Container " + image + ".image doesnt exist. Creating")
        CreateContainer(name,port,image,networkname,hostmode)

        logger.error("Creating container finished")
        found=ContainerExists(name,port,image)
    
    started=ContainerStarted(name,port,image)
    
    while started == -1:        
        logger = logging.getLogger()
        logger.error("Container " + image + ".image is not started. Starting")
        StartContainer(name,port,image)

        logger.error("Starting container finished")
        started=ContainerStarted(name,port,image)

    pass
def GetFileDir():
    cd = os.path.dirname(os.path.realpath(__file__))
    return cd

def CreateContainer(channelname:str, port:int,image:str="fbrelay",networkname:str="fbrelaynet",hostmode:bool=False):
    EnsureImage(image)
    cd = GetFileDir()
    ssblocation=os.path.join(cd,"fbrelay_ssb",channelname)
    ssbsharedlocation=os.path.join(cd,"fbrelay_ssb",".ssbshared")
    strport = str(port)
    containerName=ContainerFullName(channelname,port,image)
    command="docker run -d --name " + containerName+\
        " --expose " + strport
    if hostmode:
        command += " -p 0.0.0.0:" + strport + ":" + strport
    command += \
        " --network "+networkname +\
        " --restart unless-stopped "\
        " --mount type=bind,source="+ssblocation+",target=/root/.ssb "\
        " --mount type=bind,source="+ssbsharedlocation+",target=/root/.ssbshared "\
        " --sysctl net.core.somaxconn=100000 "\
        " --sysctl net.ipv4.tcp_max_syn_backlog=60000 "\
        " --sysctl net.ipv4.tcp_fin_timeout=5 "\
        " --sysctl net.ipv4.tcp_tw_reuse=1 "\
        " --sysctl net.netfilter.nf_conntrack_tcp_timeout_time_wait=5 " + \
        image + ".image \""+channelname+"\" \"30\" " + str(port)
        
        #" --network fbrelaynet "\
    stream=os.popen(command)
    output = stream.read()
    pass

def GenerateInvite():
    command="docker exec -it fbrelayhub.8008.fbrelayhub.container ssb-server invite.create 1"    
    stream=os.popen(command)
    output = stream.read()
    output=output.replace("\n","")
    invite=output.replace("0.0.0.0","fbrelayhub.8008.fbrelayhub.container")
    return invite

def AcceptInvite(channelName:str,port:int,image:str,invite:str):
    container=ContainerFullName(channelName,port,image)
    command="docker exec -it "+container+" ssb-server invite.accept "+invite
    stream=os.popen(command)
    output = stream.read()

def ConnectRelayToHub(channelName:str,port:int,image:str):
    invite=GenerateInvite()
    AcceptInvite(channelName,port,image,invite)

def ConnectRelayToPub(invite,channelName:str,port:int,image:str):    
    AcceptInvite(channelName,port,image,invite)

def GetContainers():
    stream = os.popen("docker container ls -a")
    output = stream.read()
    containers=re.findall("\\b[\\w.-]+.container",output)

    return containers

def ProcessFrame():    
    jobs = dpg.get_callback_queue() # retrieves and clears queue
    dpg.run_callbacks(jobs)
    dpg.render_dearpygui_frame()

def RestartAllRelays():
    print("Restarting all relays...")
    existingContainers = GetContainers()
    for relayname in existingContainers:    
        name = relayname.split('.')[0]    
        if name!="fbrelayhub":
            print("Restarting " + name + "...")            
            EnsureStartedContainer(name,8008,"fbrelay","fbrelaynet",hostmode=False)
            print("Finished restarting " + name)
    print("Finished restarting all relays")

def main():
            
    EnsureStartedContainer("fbrelayhub",8008,"fbrelayhub","fbrelaynet",hostmode=True)

    #port=FindFreePort(existingContainers)
    def EnsureInvite():
        channelname=dpg.get_value("channel_name")
        dpg.set_value("channel_name","")
        ProcessFrame()
        ConnectRelayToHub(channelname,8008,"fbrelay")
        print("Profile "+channelname+" has joined the Scuttleface pub")

    def MakeProfilePublic():
        channelName=dpg.get_value("channel_name")
        dpg.set_value("channel_name","")
        ProcessFrame()
        container=ContainerFullName(channelName,8008,"fbrelay")
        
        command="docker exec -it "+container+" ssb-server whoami"
        stream=os.popen(command)
        output = stream.read()
        profileid=json.loads(output)["id"]

        command="docker exec -it "+container+" ssb-server publish --type about --about "+profileid+" --publicWebHosting"
        stream=os.popen(command)
        output = stream.read()
        print("Profile "+channelName+" ("+profileid+") has been made public")


    def StartRelayContainerCb(sender, data):
        channelname=dpg.get_value("channel_name")
        dpg.set_value("channel_name","")
        ProcessFrame()
        EnsureStartedContainer(channelname,8008,"fbrelay","fbrelaynet",hostmode=False)
        ConnectRelayToHub(channelname,8008,"fbrelay")
        #dpg.show_item("file_dialog_id")
    def JoinPubUsingInvite(sender,data):
        invite=dpg.get_value("invite")
        channelname=dpg.get_value("channel_name")
        dpg.set_value("channel_name","")
        ProcessFrame()
        ConnectRelayToPub(invite,channelname,8008,"fbrelay")

    dpg.create_context()
    dpg.configure_app(manual_callback_management=True)
    dpg.create_viewport(title="Add relay", width=600,height=300)

    def callback(sender, app_data):
        print("Sender: ", sender)
        print("App Data: ", app_data)

    dpg.add_file_dialog(directory_selector=True, show=False, callback=callback, tag="file_dialog_id")

    def RebuildRelayImage():
        BuildImage("fbrelay")
        print("rebuild finished")

    with dpg.window(label="Example window") as main_window:
        dpg.add_text("Add a page from facebook")
        
        dpg.add_input_text(tag="channel_name",label="Channel Name", default_value="") 
        dpg.add_button(label="(Re)Start relay", callback=StartRelayContainerCb)
        dpg.add_button(label="Make friends with relay hub", callback=EnsureInvite)
        #sbot publish --type about --about "@your.public.id.here" --publicWebHosting
        dpg.add_button(label="Make profile public (parsable by viewers)", callback=MakeProfilePublic)
        
        dpg.add_input_text(tag="invite",label="Invite", default_value="") 
        dpg.add_button(label="Join Pub using invite code", callback=JoinPubUsingInvite)
        dpg.add_button(label="Rebuild relay docker image", callback=RebuildRelayImage)
        dpg.add_button(label="Restart all relays", callback=RestartAllRelays)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window(main_window, True)
    #dpg.start_dearpygui()
    dpg.focus_item(main_window)
    while dpg.is_dearpygui_running():
        ProcessFrame()


    dpg.destroy_context()

if __name__=="__main__":
    main()