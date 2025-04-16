import requests
import shutil
import os
username = "gns3"
password = "gns3"
project_name="NAS"
auth = (username, password)
projects=requests.get("http://localhost:3080/v2/projects",auth=auth).json()
project=next((p for p in projects if p["name"]==project_name), None)
project_id=project["project_id"]
nodes=requests.get(f"http://localhost:3080/v2/projects/{project_id}/nodes").json()
for i in range (len(nodes)):
    node=nodes[i]
    node_id=node["node_id"]
    node_name=node["name"]
    print(node_name)
    node_info=requests.get(f"http://localhost:3080/v2/projects/{project_id}/nodes/{node_id}").json()
    if node_info["node_directory"]:
        node_directory=node_info["node_directory"]
        file_avant="i"+str(i+1)+"_startup-config.cfg"
        config_file_path = os.path.join(node_directory, "configs", file_avant)
        stop_url = f"http://localhost:3080/v2/projects/v2/projects/{project_id}/nodes/{node_id}/stop"
        requests.post(stop_url)
        print("Node stopped.")
        try:
            
            file_apres=str(node_name)+".cfg"
            shutil.copyfile(file_apres,config_file_path)
            print("Config file replaced successfully.")
        except Exception as e:
            print(f"Failed to copy config file: {e}")
        start_url = f"http://localhost:3080/v2/projects/v2/projects/v2/projects/{project_id}/nodes/{node_id}/start"
        requests.post(start_url)
        print("Node started.")
    
