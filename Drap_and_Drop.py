import requests
import shutil
import os
project_name="NAS"
projects=requests.get("http://localhost:3080/v2/projects").json()
project=next((p for p in projects if p["name"]==project_name), None)
project_id=project["project_id"]
nodes=requests.get(f"http://localhost:3080/v2/projects/{project_id}/nodes").json()
'''
node=nodes[1]
node_id=node["node_id"]
node_name=node["name"]
print(f"{node_name}")
node_info=requests.get(f"http://localhost:3080/v2/projects/{project_id}/nodes/{node_id}").json()
node_directory=node_info["node_directory"]
config_file_path = os.path.join(node_directory, "configs", "i1_startup-config.cfg")
stop_url = f"http://localhost:3080/v2/projects/v2/projects/{project_id}/nodes/{node_id}/stop"
requests.post(stop_url)
print("Node stopped.")

# Step 2: Replace the config file
try:
    shutil.copyfile("PE1.cfg",config_file_path)
    print("Config file replaced successfully.")
except Exception as e:
    print(f"Failed to copy config file: {e}")

# Step 3: Start the node again
start_url = f"http://localhost:3080/v2/projects/v2/projects/v2/projects/{project_id}/nodes/{node_id}/start"
requests.post(start_url)
print("Node started.")
'''
for i in range (len(nodes)):
    node=nodes[i]
    node_id=node["node_id"]
    node_name=node["name"]
    node_info=requests.get(f"http://localhost:3080/v2/projects/{project_id}/nodes/{node_id}").json()
    node_directory=node_info["node_directory"]
    file_avant="i[{i}]_startup-config.cfg"
    config_file_path = os.path.join(node_directory, "configs", file_avant)
    stop_url = f"http://localhost:3080/v2/projects/v2/projects/{project_id}/nodes/{node_id}/stop"
    requests.post(stop_url)
    print("Node stopped.")
    try:
        file_apres=""
        shutil.copyfile("{node_name}.cfg",config_file_path)
        print("Config file replaced successfully.")
    except Exception as e:
        print(f"Failed to copy config file: {e}")
    start_url = f"http://localhost:3080/v2/projects/v2/projects/v2/projects/{project_id}/nodes/{node_id}/start"
    requests.post(start_url)
    print("Node started.")
