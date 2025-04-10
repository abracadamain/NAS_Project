import json

# Ouvrir et lire un fichier JSON
with open('intents.json', 'r', encoding='utf-8') as file:
    data = json.load(file)  # Charger le contenu du fichier JSON en dictionnaire Python

with open('adresses.json', 'r', encoding='utf-8') as file:
    addr = json.load(file)

prefixe_ip = data["prefixe-ip"]
mask_ip = data ["masque-ip"]
prefixe_loopback = data ["prefixe-loopback"]
mask_loopback = data["masque-loopback"]


config = []
deb_config="version 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nboot-start-marker\nboot-end-marker\nno aaa new-model\nno ip icmp rate-limit unreachable\nip cef"


def check_neighbor_type (routeur, data, interface_name):
    for itf in routeur["interfaces"]:
        if itf["name"]==interface_name:
            neighbor = itf["voisin"]

            for a in data ["AS"]:
                for r in a["routeurs"]:
                    if r["hostname"] == neighbor:
                        return r["router-type"]


def get_as_neighbor(data, r_name):
    for a in data["AS"]:
        for r in a["routeurs"]:
            if r["hostname"]== r_name:
                return a["as-number"]

def get_vrf_id(voisin_name):
    return (get_as_neighbor(data, voisin_name)[:-1])

def interfaces_actives(r_name):
    for a in data["AS"]:
        for r in a["routeurs"]:
            if r["hostname"]== r_name:
                return len(r["interfaces"])



def vrf_PE(routeur, num_as, data):
    if routeur["router-type"] == "PE":
        
        for itf in routeur["interfaces"]:
            neighbor = itf["voisin"]

            for a in data ["AS"]:
                for r in a["routeurs"]:
                    if r["hostname"] == neighbor and r["router-type"] == "CE":
                        vrf_id = get_vrf_id(r["hostname"])
                        num_client = r["client-number"]
                        config.append(f"ip vrf vrf{vrf_id}")
                        config.append(f"rd {num_as}:{vrf_id}")
                        config.append(f"route-target export {num_as}:{num_client}")
                        config.append(f"route-target import {num_as}:{num_client}")


def mpls(routeur):
    config.append("no ip domain lookup\nno ipv6 cef")
    if routeur["router-type"]=="PE" or routeur["router-type"]=="P":
        config.append("mpls label protocol ldp")
    config.append("multilink bundle-name authenticated\n!\nip tcp synwait-time 5")


def loopback(routeur, masque, addr):
    if routeur["router-type"]=="PE" or routeur["router-type"]=="P":
        routeur_name = routeur["hostname"]
        if routeur_name in addr :
            adr_lb = addr[routeur_name]["loopback"]
            config.append(f"interface Loopback0\nip address {adr_lb} {masque}")


def intf(routeur, masque_ip, data):
    interfaces=[]
    r_name= routeur["hostname"]
    r_type = routeur["router-type"]
    toutes =["FastEthernet0/0","GigabitEthernet1/0","GigabitEthernet2/0","GigabitEthernet3/0"]  
    for r_i in routeur["interfaces"]:
        interfaces.append(r_i["name"])

    for t in toutes :
        config.append(t)

        if t in interfaces :
            for i in routeur["interfaces"]:
                if i["name"]==t:
                    voisin_name=i["voisin"]
            voisin_CE = False
            if routeur["router-type"]!="CE":
                if check_neighbor_type(routeur, data,t)=="CE":
                    
                    voisin_CE=True
                    config.append(f"ip vrf forwarding {get_vrf_id(voisin_name)}")

            if r_type == "PE": # a enlever une fois adr.json complet
                for ad in addr[r_name]["interfaces"]:
                    if ad["name"] == t:
                        addresse = ad["adresse"]
                        config.append(f"ip address {addresse} {masque_ip}")
                        config.append("negotiation auto")

            if not voisin_CE and routeur["router-type"]!="CE":
                config.append("mpls ip")

        else:
            config.append("no ip address\n shutdown")
            if "FastEthernet" in t:
                config.append("duplex full")
            else:
                config.append("negotiation auto")

    
def ospf (routeur):
    if routeur["router-type"]=="PE": # a enlever une fois adr.json complet
        r_name = routeur["hostname"]
        r_id = addr[r_name]["routeur-id"]
        adr_lb = addr[r_name]["loopback"]
        config.append("router ospf 1")
        config.append(f"router-id {r_id}")
        config.append(f"network {adr_lb} 0.0.0.0 area 0")

        for i in routeur["interfaces"]:
            if check_neighbor_type(routeur, data, i["name"])!= "CE":
                config.append("voisin P")
                for ii in addr[r_name]["interfaces"]:
                    if ii["name"]==i["name"]:
                        adr_res=ii["adresse-reseau"]
                        config.append(f"network {adr_res} 0.0.0.3 area 0")
                        

def iBGP_PE(routeur, as_num):
    if routeur["router-type"]=="PE":
        config.append(f"router bgp {as_num}")
        config.append("bgp log-neighbor-changes")
        for a in data["AS"]:
            for r in a["routeurs"]:
                if r["router-type"]=="PE" and r["hostname"]!=routeur["hostname"]:
                    lb_PE=addr[r["hostname"]]["loopback"]
                    config.append (f"neighbor {lb_PE} remote-as {as_num}")
                    config.append(f"neighbor {lb_PE} update-source Loopback0")
                    config.append("address-family ipv4")
                    config.append(f"neighbor {lb_PE} activate")
                    config.append("exit-address-family")
                    config.append("address-family vpnv4")
                    config.append(f"neighbor {lb_PE} activate")
                    config.append(f"neighbor {lb_PE} send-community both")
                    config.append("exit-address-family")


def eBGP_PE(routeur):
    if routeur["router-type"]=="PE":
        for i in routeur["interfaces"]:
            if check_neighbor_type(routeur, data,i["name"])=="CE":
                voisin_name=i["voisin"]
                config.append(f"address-family ipv4 vrf vrf{get_vrf_id(voisin_name)}")
                as_neighbor = get_as_neighbor(data, voisin_name)
                for k in range (interfaces_actives(voisin_name)):
                    config.append(f"neighbor ... remote-as {as_neighbor}")
                    config.append("neighbor ... activate")
                config.append("exit-address-family")


def bgp_CE (routeur, asnumber, masque_ip):
    config.append(f"router bgp {asnumber}")
    config.append("bgp log-neighbor-changes")
    for k in range (interfaces_actives(routeur["hostname"])):
        config.append(f"network ADDRESSE IP {masque_ip} ")
    for i in routeur["interfaces"]:
        if check_neighbor_type(routeur, data,i["name"])=="PE":
            voisin_name = i["voisin"]
            config.append(f"neighbor ADDRESSE DU VOISIN remote-as {get_as_neighbor(data, voisin_name)}")


fin_config="ip forward-protocol nd\nno ip http server\nno ip http secure-server\ncontrol-plane\nline con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\nstopbits 1\nline aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline vty 0 4\n login\nend"



for a in data["AS"]:
    asnumber = a["as-number"]
    
    for r in a["routeurs"]:
        config=[]
        #config.append(deb_config)
        config.append("hostname")
        config.append(r["hostname"])
        vrf_PE(r, asnumber, data)

        mpls(r)

        loopback(r,mask_loopback, addr)

        intf(r, mask_ip, data)

        ospf(r)

        iBGP_PE(r, asnumber)

        eBGP_PE(r)

        bgp_CE(r, asnumber, mask_ip)

        #config.append(fin_config)

        print(config)