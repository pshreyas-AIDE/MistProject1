import json
'''
Phase 1: Implement a recursive script that turns any nested dict into a list of "Path-Value" tuples.


'''

l=[]
class nested_dict_to_list:
    # payload - Is the nested dictionary structure
    def __init__(self):
        self.list = []
    def __iter__(self,payload,l):
        # Base condition
        # If the type of payload is list or str or int or float or boolean -- Break
        # Else if payload is dictionary continue
        t=type(payload)
        if(t == dict):
            for key in payload:
                l.append(key)
                self.__iter__(payload[key],l)
                l.pop()
        elif(isinstance(payload,list)):
            if(len(payload)):
                type_of_list_element=type(payload[0])
            else:
                #empty list
                type_of_list_element="empty list"
            if(type_of_list_element == dict):
                for element in payload:
                    if(type(element) == dict):
                        l.append("%[[[[[[% ")
                        self.__iter__(element, l)
                        l.pop()
            elif(type_of_list_element == list):
                for element in payload:
                    list_to_string=str(element).replace(", ","|")[1:len(str(element))-1]
                    l.append("%[[[[[[% "+list_to_string+" %]]]]]]%")
                    self.list.append(l.copy())
                    l.pop()
            else:
                # This can be list of int, list of str , list of float
                if(type_of_list_element=="empty list"):
                    # Empty list
                    l.append("%[[[[[[%" +" [] "+ "%]]]]]]%")
                    self.list.append(l.copy())
                    l.pop()
                else:
                    l.append("%[[[[[[%"+str(payload).replace(", ","|")[1:len(str(payload))-1]+"%]]]]]]%")
                    self.list.append(l.copy())
                    l.pop()
        else:
            # This is impossible since in https payload its not allowed
            if(isinstance(payload,tuple) or isinstance(payload,set)):
                for element in payload:
                    l.append(element)
                    self.list.append(l.copy())
                    l.pop()
            else:
                l.append(payload)
                self.list.append(l.copy())
                l.pop()
            return self.list

    def print_list_equivalent_of_dict(self):
        for key in self.list:
            l.append(key)


# Complexity - O( n )  n --- > Number of layers nested

payload={
    "adopted": False,
    "disable_auto_config": False,
    "managed": True,
    "role": "",
    "notes": "",
    "networks": {
        "marvisvlan2": {
            "vlan_id": 2,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan3": {
            "vlan_id": 3,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan4": {
            "vlan_id": 4,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan5": {
            "vlan_id": 5,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan6": {
            "vlan_id": 6,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan7": {
            "vlan_id": 7,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan8": {
            "vlan_id": 8,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan9": {
            "vlan_id": 9,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan10": {
            "vlan_id": 10,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan11": {
            "vlan_id": 11,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan12": {
            "vlan_id": 12,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan13": {
            "vlan_id": 13,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan14": {
            "vlan_id": 14,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan15": {
            "vlan_id": 15,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan16": {
            "vlan_id": 16,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan17": {
            "vlan_id": 17,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan18": {
            "vlan_id": 18,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan19": {
            "vlan_id": 19,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan20": {
            "vlan_id": 20,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan21": {
            "vlan_id": 21,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan22": {
            "vlan_id": 22,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan23": {
            "vlan_id": 23,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan24": {
            "vlan_id": 24,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan25": {
            "vlan_id": 25,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan26": {
            "vlan_id": 26,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan27": {
            "vlan_id": 27,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan28": {
            "vlan_id": 28,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan29": {
            "vlan_id": 29,
            "subnet": "",
            "subnet6": ""
        },
        "vlan100": {
            "vlan_id": "100",
            "subnet": "",
            "subnet6": ""
        }
    },
    "port_usages": {
        "new": {
            "mode": "access",
            "disabled": False,
            "port_network": "default",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "10m",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "access10": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan10",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False,
            "poe_legacy_pd": False
        },
        "vl1n20": {
            "name": "vl1n20",
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan20",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "predpc10": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan10",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "postdpc20": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan20",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "dot1x_heb_issue": {
            "mode": "access",
            "disabled": False,
            "port_network": "default",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": "dot1x",
            "allow_multiple_supplicants": False,
            "enable_mac_auth": False,
            "mac_auth_only": False,
            "mac_auth_preferred": False,
            "guest_network": None,
            "bypass_auth_when_server_down": True,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": "65000",
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "access7": {
            "name": "access7",
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan7",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "port-mirror": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan10",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "access-ravi": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan18",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "dot1x_vlan20": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan20",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": "dot1x",
            "allow_multiple_supplicants": False,
            "enable_mac_auth": False,
            "mac_auth_only": False,
            "mac_auth_preferred": False,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": "65000",
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "mtu-lesser": {
            "mode": "access",
            "disabled": False,
            "port_network": "default",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": 1279,
            "description": "",
            "disable_autoneg": False
        },
        "mtuvalid": {
            "mode": "access",
            "disabled": False,
            "port_network": "default",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": 1514,
            "description": "",
            "disable_autoneg": False
        },
        "port_mirror_profile": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan12",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "devicedpc": {
            "mode": "access",
            "disabled": False,
            "port_network": "default",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "poe_priority": None,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "dynamic": {
            "mode": "dynamic",
            "rules": [
                {
                    "src": "lldp_chassis_id",
                    "usage": "postdpc20",
                    "equals": "3c:94:fd:09:91:f6",
                    "expression": "[0:17]"
                }
            ]
        },
        "vc-4400-profile": {
            "mode": "trunk",
            "disabled": False,
            "port_network": None,
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": [
                "marvisvlan2",
                "marvisvlan3",
                "marvisvlan4",
                "marvisvlan5",
                "marvisvlan6",
                "marvisvlan7",
                "marvisvlan8",
                "marvisvlan9",
                "marvisvlan10",
                "marvisvlan11"
            ],
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "poe_priority": None,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "vc-4400-profile",
            "disable_autoneg": False
        },
        "stormcontrolandqos": {
            "name": "stormcontrolandqos",
            "mode": "access",
            "disabled": False,
            "port_network": "default",
            "voip_network": None,
            "stp_edge": True,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": True,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "poe_priority": None,
            "enable_qos": True,
            "storm_control": {
                "percentage": 80,
                "no_broadcast": True,
                "no_multicast": True,
                "no_unknown_unicast": False,
                "disable_port": False
            },
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "valn11": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan11",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "poe_priority": None,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "uplink": {
            "mode": "trunk",
            "all_networks": False,
            "stp_edge": False,
            "port_network": "default",
            "voip_network": None,
            "isDeletable": True,
            "disabled": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "networks": [
                "default",
                "marvisvlan2",
                "marvisvlan3",
                "marvisvlan4",
                "marvisvlan5",
                "marvisvlan6",
                "marvisvlan7",
                "marvisvlan8",
                "marvisvlan9",
                "marvisvlan10",
                "marvisvlan11",
                "marvisvlan12",
                "marvisvlan13",
                "marvisvlan14",
                "marvisvlan15",
                "marvisvlan16",
                "marvisvlan17",
                "marvisvlan18",
                "marvisvlan19",
                "marvisvlan20",
                "marvisvlan21",
                "marvisvlan22",
                "marvisvlan23",
                "marvisvlan24",
                "marvisvlan25",
                "marvisvlan26",
                "marvisvlan27",
                "marvisvlan28",
                "marvisvlan29"
            ],
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "poe_priority": None,
            "poe_keep_state_when_reboot": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        },
        "acccessvlan100": {
            "mode": "access",
            "disabled": False,
            "port_network": "vlan100",
            "voip_network": None,
            "stp_edge": False,
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "poe_priority": None,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False,
            "poe_keep_state_when_reboot": False
        },
        "edge_port": {
            "mode": "access",
            "disabled": False,
            "port_network": "default",
            "voip_network": None,
            "stp_edge": True,
            "family": "junos",
            "stp_disable": False,
            "stp_required": False,
            "stp_p2p": False,
            "stp_no_root_port": False,
            "use_vstp": False,
            "port_auth": None,
            "allow_multiple_supplicants": None,
            "enable_mac_auth": None,
            "mac_auth_only": None,
            "mac_auth_preferred": None,
            "guest_network": None,
            "bypass_auth_when_server_down": None,
            "bypass_auth_when_server_down_for_unknown_client": None,
            "dynamic_vlan_networks": None,
            "server_reject_network": None,
            "server_fail_network": None,
            "mac_auth_protocol": None,
            "reauth_interval": None,
            "all_networks": False,
            "networks": None,
            "speed": "auto",
            "duplex": "auto",
            "mac_limit": 0,
            "persist_mac": False,
            "poe_disabled": False,
            "poe_legacy_pd": False,
            "poe_priority": None,
            "poe_keep_state_when_reboot": False,
            "enable_qos": False,
            "storm_control": {},
            "mtu": None,
            "description": "",
            "disable_autoneg": False
        }
    },
    "additional_config_cmds": [
        "delete protocols l2-learning global-mac-ip-snooping"
    ],
    "bgp_config": None,
    "routing_policies": {},
    "optic_port_config": {},
    "other_ip_configs": {
        "marvisvlan2": {
            "type": "dhcp"
        },
        "marvisvlan3": {
            "type": "dhcp"
        },
        "marvisvlan4": {
            "type": "dhcp"
        },
        "marvisvlan5": {
            "type": "dhcp"
        },
        "marvisvlan6": {
            "type": "dhcp"
        },
        "marvisvlan7": {
            "type": "dhcp"
        },
        "marvisvlan8": {
            "type": "dhcp"
        },
        "marvisvlan9": {
            "type": "dhcp"
        },
        "marvisvlan10": {
            "type": "dhcp"
        },
        "marvisvlan11": {
            "type": "dhcp"
        },
        "marvisvlan12": {
            "type": "dhcp"
        },
        "marvisvlan13": {
            "type": "dhcp"
        },
        "marvisvlan14": {
            "type": "dhcp"
        },
        "marvisvlan15": {
            "type": "dhcp"
        },
        "marvisvlan16": {
            "type": "dhcp"
        },
        "marvisvlan17": {
            "type": "dhcp"
        },
        "marvisvlan18": {
            "type": "dhcp"
        },
        "marvisvlan19": {
            "type": "dhcp"
        },
        "marvisvlan20": {
            "type": "dhcp"
        },
        "marvisvlan21": {
            "type": "dhcp"
        },
        "marvisvlan22": {
            "type": "dhcp"
        },
        "marvisvlan23": {
            "type": "dhcp"
        },
        "marvisvlan24": {
            "type": "dhcp"
        },
        "marvisvlan25": {
            "type": "dhcp"
        },
        "marvisvlan26": {
            "type": "dhcp"
        },
        "marvisvlan27": {
            "type": "dhcp"
        },
        "marvisvlan28": {
            "type": "dhcp"
        },
        "marvisvlan29": {
            "type": "dhcp"
        }
    },
    "port_config": {
        "ge-0/0/11": {
            "usage": "ap",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/10": {
            "usage": "ap",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/1-4, ge-0/0/6-9": {
            "usage": "default",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/5": {
            "usage": "dot1x_heb_issue",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/0": {
            "usage": "uplink",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        }
    },
    "vars": {},
    "switch_mgmt": {
        "root_password": "mist123",
        "local_accounts": {
            "deviceuser": {
                "role": "admin",
                "password": "abcdfg"
            },
            "newuser": {
                "role": "admin",
                "password": "mist&123"
            },
            "new": {
                "role": "admin",
                "password": "abcdef{}[]'~"
            },
            "new1": {
                "role": "admin",
                "password": "abcdef{}[]'~sad&:"
            }
        }
    },
    "radius_config": {
        "enabled": False,
        "auth_servers": [],
        "acct_servers": [],
        "auth_servers_timeout": 5,
        "auth_servers_retries": 3,
        "fast_dot1x_timers": False,
        "acct_interim_interval": 0,
        "auth_server_selection": "ordered",
        "coa_enabled": False,
        "coa_port": ""
    },
    "mist_nac": {
        "enabled": True,
        "auth_servers_timeout": 5,
        "auth_servers_retries": 3,
        "fast_dot1x_timers": False,
        "acct_interim_interval": 0,
        "network": None,
        "coa_enabled": False,
        "coa_port": ""
    },
    "remote_syslog": {
        "enabled": True,
        "time_format": "",
        "source_address": None,
        "routing_instance": None,
        "archive": {
            "files": "",
            "size": ""
        },
        "files": [
            {
                "file": "asd",
                "match": "dsf",
                "archive": {
                    "files": "",
                    "size": ""
                },
                "explicit_priority": False,
                "structured_data": False,
                "contents": []
            }
        ],
        "servers": [],
        "users": [],
        "console": {}
    },
    "snmp_config": {
        "enabled": True,
        "name": "asd",
        "location": "",
        "description": "",
        "contact": "",
        "views": [],
        "network": None,
        "client_list": [],
        "trap_groups": [],
        "v2c_config": []
    },
    "dhcpd_config": {
        "enabled": False
    },
    "oob_ip_config": {
        "type": "static",
        "ip": "10.216.194.60",
        "netmask": "/26",
        "use_mgmt_vrf": True,
        "use_mgmt_vrf_for_host_out": True,
        "gateway": "10.216.194.1"
    },
    "vrf_instances": {
        "vrf1": {
            "networks": [
                "marvisvlan20",
                "marvisvlan21",
                "marvisvlan22"
            ],
            "extra_routes": {},
            "extra_routes6": {}
        }
    },
    "port_mirroring": {
        "latency": {
            "output_port_id": "ge-0/0/11",
            "input_port_ids_ingress": [
                "ge-0/0/0"
            ],
            "input_port_ids_egress": [
                "ge-0/0/0"
            ],
            "input_networks_ingress": []
        }
    },
    "extra_routes": {
        "0.0.0.0/0": {
            "via": [
                "10.216.194.1"
            ],
            "discard": False
        }
    },
    "extra_routes6": {},
    "id": "00000000-0000-0000-1000-209339051400",
    "name": "Temp-new-name-change",
    "site_id": "e0863444-2933-4e70-a778-ee17da87eaa7",
    "org_id": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
    "created_time": 1772613575,
    "modified_time": 1776425993,
    "map_id": None,
    "mac": "209339051400",
    "serial": "FJ3824AV0219",
    "model": "EX4100-F-12P",
    "hw_rev": "A",
    "type": "switch",
    "tag_uuid": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
    "tag_id": 638460,
    "evpn_scope": None,
    "evpntopo_id": None,
    "st_ip_base": "",
    "deviceprofile_id": None,
    "bundled_mac": None,
    "mist_configured": True
}
obj=nested_dict_to_list()
obj.__iter__(payload, l)
for i in obj.list:
    print(i)





