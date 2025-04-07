import json
import ipaddress

def custom_serializer(obj):
    if isinstance(obj, (ipaddress.IPv4Address, ipaddress.IPv4Network)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

dict_ip = {}
with open("intents.json", "r") as file:
    data = json.load(file)

loopback = ipaddress.ip_network(data["prefixe-loopback"])
preIp = ipaddress.ip_network(data["prefixe-ip"])
subnets = list(preIp.subnets(new_prefix=30))

indiceRouteurId = "1"
indiceLoopback = 1
indiceSubnet = 0

for i in range(len(data["AS"])) :
    AS = data["AS"][i]
    routeurs = AS["routeurs"]
    for j in range(len(routeurs)) :
        routeur = routeurs[j]
        dict_ip[routeur["hostname"]] = {}
        if routeur["type"] != "CE" :
            dict_ip[routeur["hostname"]]["routeur-id"] = indiceRouteurId + "." + indiceRouteurId+ "." +indiceRouteurId+ "." +indiceRouteurId
            indiceRouteurId = str(int(indiceRouteurId) + 1)
        if routeur["type"] == "PE" :
            dict_ip[routeur["hostname"]]["loopback"] = loopback[indiceLoopback]
            indiceLoopback += 1
        for k in range(len(routeur["interfaces"])) :
            interface = routeur["interfaces"][k]
            if interface["voisin"] != "switch" :
                dict_ip[routeur["hostname"]][interface["name"]] = {}
                if interface["voisin"] in dict_ip.keys() :
                    for Vrouteur in routeurs :
                        if Vrouteur["hostname"] == interface["voisin"] :
                            for Vinterface in Vrouteur["interfaces"] :
                                if Vinterface["voisin"] == routeur["hostname"] :
                                    interfaceVoisin = Vinterface["name"]
                                    
                    dict_ip[routeur["hostname"]][interface["name"]]["adresse-reseau"] = dict_ip[interface["voisin"]][interfaceVoisin]["adresse-reseau"]
                    dict_ip[routeur["hostname"]][interface["name"]]["adresse"] = dict_ip[interface["voisin"]][interfaceVoisin]["adresse"] + 1
                
                else :
                    dict_ip[routeur["hostname"]][interface["name"]]["adresse-reseau"] = subnets[indiceSubnet][0]
                    dict_ip[routeur["hostname"]][interface["name"]]["adresse"] = subnets[indiceSubnet][1]
                    indiceSubnet += 1

with open("adresses.json", "w") as file:
    json.dump(dict_ip, file, indent=4, default=custom_serializer)         


            