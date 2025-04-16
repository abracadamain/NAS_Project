import json
import ipaddress

def ipv4_to_str(obj):
    """Converti un objet IPv4Address ou IPv4Network en string"""
    return str(obj)

dict_ip = {}
with open("intents.json", "r") as file:
    data = json.load(file)

loopback = ipaddress.ip_network(data["prefixe-loopback"])
preIp = ipaddress.ip_network(data["prefixe-ip"])
subnets = list(preIp.subnets(new_prefix=30))

indiceRouteurId = "1"
indiceLoopback = 1
indiceSubnet = 0

for As in data["AS"] :
    for routeur in As["routeurs"] :
        dict_ip[routeur["hostname"]] = {}
        if routeur["router-type"] != "CE" :
            dict_ip[routeur["hostname"]]["routeur-id"] = indiceRouteurId + "." + indiceRouteurId+ "." +indiceRouteurId+ "." +indiceRouteurId
            indiceRouteurId = str(int(indiceRouteurId) + 1)
        if routeur["router-type"] == "PE" :
            dict_ip[routeur["hostname"]]["loopback"] = loopback[indiceLoopback]
            indiceLoopback += 1
        for interface in routeur["interfaces"] :
            dict_ip[routeur["hostname"]][interface["name"]] = {}
            if interface["voisin"] in dict_ip.keys() :
                for Vas in data["AS"] :
                    Vrouteurs = Vas["routeurs"]
                    for Vrouteur in Vrouteurs :
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
    json.dump(dict_ip, file, indent=4, default=ipv4_to_str)         


            