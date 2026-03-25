'''
Phase 1: Implement a recursive script that turns any nested dict into a list of "Path-Value" tuples.


'''


class nested_dict_to_list:
    # payload - Is the nested dictionary structure
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.list = []
        self.__iter__(self.dictionary,[])
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
        else:
            if(isinstance(payload,list) or isinstance(payload,tuple) or isinstance(payload,set)):
                for element in payload:
                    l.append(element)
                    self.list.append(l.copy())
                    l.pop()
            else:
                l.append(payload)
                self.list.append(l.copy())
                l.pop()
            return

    def print_list_equivalent_of_dict(self):
        for key in self.list:
            print(key)


# Complexity - O( n )  n --- > Number of layers nested

payload={
    "disable_auto_config": False,
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
        "marvisvlan30": {
            "vlan_id": 30,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan31": {
            "vlan_id": 31,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan32": {
            "vlan_id": 32,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan33": {
            "vlan_id": 33,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan34": {
            "vlan_id": 34,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan35": {
            "vlan_id": 35,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan36": {
            "vlan_id": 36,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan37": {
            "vlan_id": 37,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan38": {
            "vlan_id": 38,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan39": {
            "vlan_id": 39,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan40": {
            "vlan_id": 40,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan41": {
            "vlan_id": 41,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan42": {
            "vlan_id": 42,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan43": {
            "vlan_id": 43,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan44": {
            "vlan_id": 44,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan45": {
            "vlan_id": 45,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan46": {
            "vlan_id": 46,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan47": {
            "vlan_id": 47,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan48": {
            "vlan_id": 48,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan49": {
            "vlan_id": 49,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan50": {
            "vlan_id": 50,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan51": {
            "vlan_id": 51,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan52": {
            "vlan_id": 52,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan53": {
            "vlan_id": 53,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan54": {
            "vlan_id": 54,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan55": {
            "vlan_id": 55,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan56": {
            "vlan_id": 56,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan57": {
            "vlan_id": 57,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan58": {
            "vlan_id": 58,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan59": {
            "vlan_id": 59,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan60": {
            "vlan_id": 60,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan61": {
            "vlan_id": 61,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan62": {
            "vlan_id": 62,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan63": {
            "vlan_id": 63,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan64": {
            "vlan_id": 64,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan65": {
            "vlan_id": 65,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan66": {
            "vlan_id": 66,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan67": {
            "vlan_id": 67,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan68": {
            "vlan_id": 68,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan69": {
            "vlan_id": 69,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan70": {
            "vlan_id": 70,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan71": {
            "vlan_id": 71,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan72": {
            "vlan_id": 72,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan73": {
            "vlan_id": 73,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan74": {
            "vlan_id": 74,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan75": {
            "vlan_id": 75,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan76": {
            "vlan_id": 76,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan77": {
            "vlan_id": 77,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan78": {
            "vlan_id": 78,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan79": {
            "vlan_id": 79,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan80": {
            "vlan_id": 80,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan81": {
            "vlan_id": 81,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan82": {
            "vlan_id": 82,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan83": {
            "vlan_id": 83,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan84": {
            "vlan_id": 84,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan85": {
            "vlan_id": 85,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan86": {
            "vlan_id": 86,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan87": {
            "vlan_id": 87,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan88": {
            "vlan_id": 88,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan89": {
            "vlan_id": 89,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan90": {
            "vlan_id": 90,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan91": {
            "vlan_id": 91,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan92": {
            "vlan_id": 92,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan93": {
            "vlan_id": 93,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan94": {
            "vlan_id": 94,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan95": {
            "vlan_id": 95,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan96": {
            "vlan_id": 96,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan97": {
            "vlan_id": 97,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan98": {
            "vlan_id": 98,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan99": {
            "vlan_id": 99,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan100": {
            "vlan_id": 100,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan101": {
            "vlan_id": 101,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan102": {
            "vlan_id": 102,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan103": {
            "vlan_id": 103,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan104": {
            "vlan_id": 104,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan105": {
            "vlan_id": 105,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan106": {
            "vlan_id": 106,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan107": {
            "vlan_id": 107,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan108": {
            "vlan_id": 108,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan109": {
            "vlan_id": 109,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan110": {
            "vlan_id": 110,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan111": {
            "vlan_id": 111,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan112": {
            "vlan_id": 112,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan113": {
            "vlan_id": 113,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan114": {
            "vlan_id": 114,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan115": {
            "vlan_id": 115,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan116": {
            "vlan_id": 116,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan117": {
            "vlan_id": 117,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan118": {
            "vlan_id": 118,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan119": {
            "vlan_id": 119,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan120": {
            "vlan_id": 120,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan121": {
            "vlan_id": 121,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan122": {
            "vlan_id": 122,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan123": {
            "vlan_id": 123,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan124": {
            "vlan_id": 124,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan125": {
            "vlan_id": 125,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan126": {
            "vlan_id": 126,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan127": {
            "vlan_id": 127,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan128": {
            "vlan_id": 128,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan129": {
            "vlan_id": 129,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan130": {
            "vlan_id": 130,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan131": {
            "vlan_id": 131,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan132": {
            "vlan_id": 132,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan133": {
            "vlan_id": 133,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan134": {
            "vlan_id": 134,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan135": {
            "vlan_id": 135,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan136": {
            "vlan_id": 136,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan137": {
            "vlan_id": 137,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan138": {
            "vlan_id": 138,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan139": {
            "vlan_id": 139,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan140": {
            "vlan_id": 140,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan141": {
            "vlan_id": 141,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan142": {
            "vlan_id": 142,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan143": {
            "vlan_id": 143,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan144": {
            "vlan_id": 144,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan145": {
            "vlan_id": 145,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan146": {
            "vlan_id": 146,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan147": {
            "vlan_id": 147,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan148": {
            "vlan_id": 148,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan149": {
            "vlan_id": 149,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan150": {
            "vlan_id": 150,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan151": {
            "vlan_id": 151,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan152": {
            "vlan_id": 152,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan153": {
            "vlan_id": 153,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan154": {
            "vlan_id": 154,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan155": {
            "vlan_id": 155,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan156": {
            "vlan_id": 156,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan157": {
            "vlan_id": 157,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan158": {
            "vlan_id": 158,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan159": {
            "vlan_id": 159,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan160": {
            "vlan_id": 160,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan161": {
            "vlan_id": 161,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan162": {
            "vlan_id": 162,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan163": {
            "vlan_id": 163,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan164": {
            "vlan_id": 164,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan165": {
            "vlan_id": 165,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan166": {
            "vlan_id": 166,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan167": {
            "vlan_id": 167,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan168": {
            "vlan_id": 168,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan169": {
            "vlan_id": 169,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan170": {
            "vlan_id": 170,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan171": {
            "vlan_id": 171,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan172": {
            "vlan_id": 172,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan173": {
            "vlan_id": 173,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan174": {
            "vlan_id": 174,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan175": {
            "vlan_id": 175,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan176": {
            "vlan_id": 176,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan177": {
            "vlan_id": 177,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan178": {
            "vlan_id": 178,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan179": {
            "vlan_id": 179,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan180": {
            "vlan_id": 180,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan181": {
            "vlan_id": 181,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan182": {
            "vlan_id": 182,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan183": {
            "vlan_id": 183,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan184": {
            "vlan_id": 184,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan185": {
            "vlan_id": 185,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan186": {
            "vlan_id": 186,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan187": {
            "vlan_id": 187,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan188": {
            "vlan_id": 188,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan189": {
            "vlan_id": 189,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan190": {
            "vlan_id": 190,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan191": {
            "vlan_id": 191,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan192": {
            "vlan_id": 192,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan193": {
            "vlan_id": 193,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan194": {
            "vlan_id": 194,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan195": {
            "vlan_id": 195,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan196": {
            "vlan_id": 196,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan197": {
            "vlan_id": 197,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan198": {
            "vlan_id": 198,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan199": {
            "vlan_id": 199,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan200": {
            "vlan_id": 200,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan201": {
            "vlan_id": 201,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan202": {
            "vlan_id": 202,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan203": {
            "vlan_id": 203,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan204": {
            "vlan_id": 204,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan205": {
            "vlan_id": 205,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan206": {
            "vlan_id": 206,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan207": {
            "vlan_id": 207,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan208": {
            "vlan_id": 208,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan209": {
            "vlan_id": 209,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan210": {
            "vlan_id": 210,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan211": {
            "vlan_id": 211,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan212": {
            "vlan_id": 212,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan213": {
            "vlan_id": 213,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan214": {
            "vlan_id": 214,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan215": {
            "vlan_id": 215,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan216": {
            "vlan_id": 216,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan217": {
            "vlan_id": 217,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan218": {
            "vlan_id": 218,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan219": {
            "vlan_id": 219,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan220": {
            "vlan_id": 220,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan221": {
            "vlan_id": 221,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan222": {
            "vlan_id": 222,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan223": {
            "vlan_id": 223,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan224": {
            "vlan_id": 224,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan225": {
            "vlan_id": 225,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan226": {
            "vlan_id": 226,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan227": {
            "vlan_id": 227,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan228": {
            "vlan_id": 228,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan229": {
            "vlan_id": 229,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan230": {
            "vlan_id": 230,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan231": {
            "vlan_id": 231,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan232": {
            "vlan_id": 232,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan233": {
            "vlan_id": 233,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan234": {
            "vlan_id": 234,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan235": {
            "vlan_id": 235,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan236": {
            "vlan_id": 236,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan237": {
            "vlan_id": 237,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan238": {
            "vlan_id": 238,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan239": {
            "vlan_id": 239,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan240": {
            "vlan_id": 240,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan241": {
            "vlan_id": 241,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan242": {
            "vlan_id": 242,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan243": {
            "vlan_id": 243,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan244": {
            "vlan_id": 244,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan245": {
            "vlan_id": 245,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan246": {
            "vlan_id": 246,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan247": {
            "vlan_id": 247,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan248": {
            "vlan_id": 248,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan249": {
            "vlan_id": 249,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan250": {
            "vlan_id": 250,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan251": {
            "vlan_id": 251,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan252": {
            "vlan_id": 252,
            "subnet": "",
            "subnet6": ""
        },
        "marvisvlan253": {
            "vlan_id": 253,
            "subnet": "",
            "subnet6": ""
        },
        "vlandummy": {
            "vlan_id": "4094",
            "subnet": ""
        },
        "vlanmtu": {
            "vlan_id": "499",
            "subnet": "",
            "subnet6": ""
        },
        "devicedpc": {
            "vlan_id": "998",
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
            "port_network": "vlanmtu",
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
            "port_network": "vlanmtu",
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
            "port_network": "devicedpc",
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
                    "src": "lldp_system_name",
                    "usage": "devicedpc",
                    "equals": "device",
                    "expression": "[0:6]"
                },
                {
                    "src": "link_peermac",
                    "usage": "orgdpc",
                    "equals": "11",
                    "expression": "[0:2]"
                },
                {
                    "src": "radius_dynamicfilter",
                    "usage": "orgdpc",
                    "equals": "orgdpc",
                    "expression": "[0:6]"
                },
                {
                    "src": "radius_username",
                    "usage": "orgdpc",
                    "equals": "orgdpc",
                    "expression": "[0:6]"
                },
                {
                    "src": "lldp_chassis_id",
                    "usage": "orgdpc",
                    "equals": "11",
                    "expression": "[0:2]"
                },
                {
                    "src": "lldp_system_description",
                    "usage": "orgdpc",
                    "equals": "orgdpc",
                    "expression": "[0:6]"
                },
                {
                    "src": "lldp_system_name",
                    "usage": "orgdpc",
                    "equals": "orgdpc",
                    "expression": "[0:6]"
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
        "acccessvlan100": {
            "mode": "access",
            "disabled": False,
            "port_network": "marvisvlan100",
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
        }
    },
    "additional_config_cmds": [
        "delete protocols l2-learning global-mac-ip-snooping"
    ],
    "stp_config": {},
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
        },
        "marvisvlan30": {
            "type": "dhcp"
        },
        "marvisvlan31": {
            "type": "dhcp"
        },
        "marvisvlan32": {
            "type": "dhcp"
        },
        "marvisvlan33": {
            "type": "dhcp"
        },
        "marvisvlan34": {
            "type": "dhcp"
        },
        "marvisvlan35": {
            "type": "dhcp"
        },
        "marvisvlan36": {
            "type": "dhcp"
        },
        "marvisvlan37": {
            "type": "dhcp"
        },
        "marvisvlan38": {
            "type": "dhcp"
        },
        "marvisvlan39": {
            "type": "dhcp"
        },
        "marvisvlan40": {
            "type": "dhcp"
        },
        "marvisvlan41": {
            "type": "dhcp"
        },
        "marvisvlan42": {
            "type": "dhcp"
        },
        "marvisvlan43": {
            "type": "dhcp"
        },
        "marvisvlan44": {
            "type": "dhcp"
        },
        "marvisvlan45": {
            "type": "dhcp"
        },
        "marvisvlan46": {
            "type": "dhcp"
        },
        "marvisvlan47": {
            "type": "dhcp"
        },
        "marvisvlan48": {
            "type": "dhcp"
        },
        "marvisvlan49": {
            "type": "dhcp"
        },
        "marvisvlan50": {
            "type": "dhcp"
        },
        "marvisvlan51": {
            "type": "dhcp"
        },
        "marvisvlan52": {
            "type": "dhcp"
        },
        "marvisvlan53": {
            "type": "dhcp"
        },
        "marvisvlan54": {
            "type": "dhcp"
        },
        "marvisvlan55": {
            "type": "dhcp"
        },
        "marvisvlan56": {
            "type": "dhcp"
        },
        "marvisvlan57": {
            "type": "dhcp"
        },
        "marvisvlan58": {
            "type": "dhcp"
        },
        "marvisvlan59": {
            "type": "dhcp"
        },
        "marvisvlan60": {
            "type": "dhcp"
        },
        "marvisvlan61": {
            "type": "dhcp"
        },
        "marvisvlan62": {
            "type": "dhcp"
        },
        "marvisvlan63": {
            "type": "dhcp"
        },
        "marvisvlan64": {
            "type": "dhcp"
        },
        "marvisvlan65": {
            "type": "dhcp"
        },
        "marvisvlan66": {
            "type": "dhcp"
        },
        "marvisvlan67": {
            "type": "dhcp"
        },
        "marvisvlan68": {
            "type": "dhcp"
        },
        "marvisvlan69": {
            "type": "dhcp"
        },
        "marvisvlan70": {
            "type": "dhcp"
        },
        "marvisvlan71": {
            "type": "dhcp"
        },
        "marvisvlan72": {
            "type": "dhcp"
        },
        "marvisvlan73": {
            "type": "dhcp"
        },
        "marvisvlan74": {
            "type": "dhcp"
        },
        "marvisvlan75": {
            "type": "dhcp"
        },
        "marvisvlan76": {
            "type": "dhcp"
        },
        "marvisvlan77": {
            "type": "dhcp"
        },
        "marvisvlan78": {
            "type": "dhcp"
        },
        "marvisvlan79": {
            "type": "dhcp"
        },
        "marvisvlan80": {
            "type": "dhcp"
        },
        "marvisvlan81": {
            "type": "dhcp"
        },
        "marvisvlan82": {
            "type": "dhcp"
        },
        "marvisvlan83": {
            "type": "dhcp"
        },
        "marvisvlan84": {
            "type": "dhcp"
        },
        "marvisvlan85": {
            "type": "dhcp"
        },
        "marvisvlan86": {
            "type": "dhcp"
        },
        "marvisvlan87": {
            "type": "dhcp"
        },
        "marvisvlan88": {
            "type": "dhcp"
        },
        "marvisvlan89": {
            "type": "dhcp"
        },
        "marvisvlan90": {
            "type": "dhcp"
        },
        "marvisvlan91": {
            "type": "dhcp"
        },
        "marvisvlan92": {
            "type": "dhcp"
        },
        "marvisvlan93": {
            "type": "dhcp"
        },
        "marvisvlan94": {
            "type": "dhcp"
        },
        "marvisvlan95": {
            "type": "dhcp"
        },
        "marvisvlan96": {
            "type": "dhcp"
        },
        "marvisvlan97": {
            "type": "dhcp"
        },
        "marvisvlan98": {
            "type": "dhcp"
        },
        "marvisvlan99": {
            "type": "dhcp"
        },
        "marvisvlan100": {
            "type": "dhcp"
        },
        "marvisvlan101": {
            "type": "dhcp"
        },
        "marvisvlan102": {
            "type": "dhcp"
        },
        "marvisvlan103": {
            "type": "dhcp"
        },
        "marvisvlan104": {
            "type": "dhcp"
        },
        "marvisvlan105": {
            "type": "dhcp"
        },
        "marvisvlan106": {
            "type": "dhcp"
        },
        "marvisvlan107": {
            "type": "dhcp"
        },
        "marvisvlan108": {
            "type": "dhcp"
        },
        "marvisvlan109": {
            "type": "dhcp"
        },
        "marvisvlan110": {
            "type": "dhcp"
        },
        "marvisvlan111": {
            "type": "dhcp"
        },
        "marvisvlan112": {
            "type": "dhcp"
        },
        "marvisvlan113": {
            "type": "dhcp"
        },
        "marvisvlan114": {
            "type": "dhcp"
        },
        "marvisvlan115": {
            "type": "dhcp"
        },
        "marvisvlan116": {
            "type": "dhcp"
        },
        "marvisvlan117": {
            "type": "dhcp"
        },
        "marvisvlan118": {
            "type": "dhcp"
        },
        "marvisvlan119": {
            "type": "dhcp"
        },
        "marvisvlan120": {
            "type": "dhcp"
        },
        "marvisvlan121": {
            "type": "dhcp"
        },
        "marvisvlan122": {
            "type": "dhcp"
        },
        "marvisvlan123": {
            "type": "dhcp"
        },
        "marvisvlan124": {
            "type": "dhcp"
        },
        "marvisvlan125": {
            "type": "dhcp"
        },
        "marvisvlan126": {
            "type": "dhcp"
        },
        "marvisvlan127": {
            "type": "dhcp"
        },
        "marvisvlan128": {
            "type": "dhcp"
        },
        "marvisvlan129": {
            "type": "dhcp"
        },
        "marvisvlan130": {
            "type": "dhcp"
        },
        "marvisvlan131": {
            "type": "dhcp"
        },
        "marvisvlan132": {
            "type": "dhcp"
        },
        "marvisvlan133": {
            "type": "dhcp"
        },
        "marvisvlan134": {
            "type": "dhcp"
        },
        "marvisvlan135": {
            "type": "dhcp"
        },
        "marvisvlan136": {
            "type": "dhcp"
        },
        "marvisvlan137": {
            "type": "dhcp"
        },
        "marvisvlan138": {
            "type": "dhcp"
        },
        "marvisvlan139": {
            "type": "dhcp"
        },
        "marvisvlan140": {
            "type": "dhcp"
        },
        "marvisvlan141": {
            "type": "dhcp"
        },
        "marvisvlan142": {
            "type": "dhcp"
        },
        "marvisvlan143": {
            "type": "dhcp"
        },
        "marvisvlan144": {
            "type": "dhcp"
        },
        "marvisvlan145": {
            "type": "dhcp"
        },
        "marvisvlan146": {
            "type": "dhcp"
        },
        "marvisvlan147": {
            "type": "dhcp"
        },
        "marvisvlan148": {
            "type": "dhcp"
        },
        "marvisvlan149": {
            "type": "dhcp"
        },
        "marvisvlan150": {
            "type": "dhcp"
        },
        "marvisvlan151": {
            "type": "dhcp"
        },
        "marvisvlan152": {
            "type": "dhcp"
        },
        "marvisvlan153": {
            "type": "dhcp"
        },
        "marvisvlan154": {
            "type": "dhcp"
        },
        "marvisvlan155": {
            "type": "dhcp"
        },
        "marvisvlan156": {
            "type": "dhcp"
        },
        "marvisvlan157": {
            "type": "dhcp"
        },
        "marvisvlan158": {
            "type": "dhcp"
        },
        "marvisvlan159": {
            "type": "dhcp"
        },
        "marvisvlan160": {
            "type": "dhcp"
        },
        "marvisvlan161": {
            "type": "dhcp"
        },
        "marvisvlan162": {
            "type": "dhcp"
        },
        "marvisvlan163": {
            "type": "dhcp"
        },
        "marvisvlan164": {
            "type": "dhcp"
        },
        "marvisvlan165": {
            "type": "dhcp"
        },
        "marvisvlan166": {
            "type": "dhcp"
        },
        "marvisvlan167": {
            "type": "dhcp"
        },
        "marvisvlan168": {
            "type": "dhcp"
        },
        "marvisvlan169": {
            "type": "dhcp"
        },
        "marvisvlan170": {
            "type": "dhcp"
        },
        "marvisvlan171": {
            "type": "dhcp"
        },
        "marvisvlan172": {
            "type": "dhcp"
        },
        "marvisvlan173": {
            "type": "dhcp"
        },
        "marvisvlan174": {
            "type": "dhcp"
        },
        "marvisvlan175": {
            "type": "dhcp"
        },
        "marvisvlan176": {
            "type": "dhcp"
        },
        "marvisvlan177": {
            "type": "dhcp"
        },
        "marvisvlan178": {
            "type": "dhcp"
        },
        "marvisvlan179": {
            "type": "dhcp"
        },
        "marvisvlan180": {
            "type": "dhcp"
        },
        "marvisvlan181": {
            "type": "dhcp"
        },
        "marvisvlan182": {
            "type": "dhcp"
        },
        "marvisvlan183": {
            "type": "dhcp"
        },
        "marvisvlan184": {
            "type": "dhcp"
        },
        "marvisvlan185": {
            "type": "dhcp"
        },
        "marvisvlan186": {
            "type": "dhcp"
        },
        "marvisvlan187": {
            "type": "dhcp"
        },
        "marvisvlan188": {
            "type": "dhcp"
        },
        "marvisvlan189": {
            "type": "dhcp"
        },
        "marvisvlan190": {
            "type": "dhcp"
        },
        "marvisvlan191": {
            "type": "dhcp"
        },
        "marvisvlan192": {
            "type": "dhcp"
        },
        "marvisvlan193": {
            "type": "dhcp"
        },
        "marvisvlan194": {
            "type": "dhcp"
        },
        "marvisvlan195": {
            "type": "dhcp"
        },
        "marvisvlan196": {
            "type": "dhcp"
        },
        "marvisvlan197": {
            "type": "dhcp"
        },
        "marvisvlan198": {
            "type": "dhcp"
        },
        "marvisvlan199": {
            "type": "dhcp"
        },
        "marvisvlan200": {
            "type": "dhcp"
        },
        "marvisvlan201": {
            "type": "dhcp"
        },
        "marvisvlan202": {
            "type": "dhcp"
        },
        "marvisvlan203": {
            "type": "dhcp"
        },
        "marvisvlan204": {
            "type": "dhcp"
        },
        "marvisvlan205": {
            "type": "dhcp"
        },
        "marvisvlan206": {
            "type": "dhcp"
        },
        "marvisvlan207": {
            "type": "dhcp"
        },
        "marvisvlan208": {
            "type": "dhcp"
        },
        "marvisvlan209": {
            "type": "dhcp"
        },
        "marvisvlan210": {
            "type": "dhcp"
        },
        "marvisvlan211": {
            "type": "dhcp"
        },
        "marvisvlan212": {
            "type": "dhcp"
        },
        "marvisvlan213": {
            "type": "dhcp"
        },
        "marvisvlan214": {
            "type": "dhcp"
        },
        "marvisvlan215": {
            "type": "dhcp"
        },
        "marvisvlan216": {
            "type": "dhcp"
        },
        "marvisvlan217": {
            "type": "dhcp"
        },
        "marvisvlan218": {
            "type": "dhcp"
        },
        "marvisvlan219": {
            "type": "dhcp"
        },
        "marvisvlan220": {
            "type": "dhcp"
        },
        "marvisvlan221": {
            "type": "dhcp"
        },
        "marvisvlan222": {
            "type": "dhcp"
        },
        "marvisvlan223": {
            "type": "dhcp"
        },
        "marvisvlan224": {
            "type": "dhcp"
        },
        "marvisvlan225": {
            "type": "dhcp"
        },
        "marvisvlan226": {
            "type": "dhcp"
        },
        "marvisvlan227": {
            "type": "dhcp"
        },
        "marvisvlan228": {
            "type": "dhcp"
        },
        "marvisvlan229": {
            "type": "dhcp"
        },
        "marvisvlan230": {
            "type": "dhcp"
        },
        "marvisvlan231": {
            "type": "dhcp"
        },
        "marvisvlan232": {
            "type": "dhcp"
        },
        "marvisvlan233": {
            "type": "dhcp"
        },
        "marvisvlan234": {
            "type": "dhcp"
        },
        "marvisvlan235": {
            "type": "dhcp"
        },
        "marvisvlan236": {
            "type": "dhcp"
        },
        "marvisvlan237": {
            "type": "dhcp"
        },
        "marvisvlan238": {
            "type": "dhcp"
        },
        "marvisvlan239": {
            "type": "dhcp"
        },
        "marvisvlan240": {
            "type": "dhcp"
        },
        "marvisvlan241": {
            "type": "dhcp"
        },
        "marvisvlan242": {
            "type": "dhcp"
        },
        "marvisvlan243": {
            "type": "dhcp"
        },
        "marvisvlan244": {
            "type": "dhcp"
        },
        "marvisvlan245": {
            "type": "dhcp"
        },
        "marvisvlan246": {
            "type": "dhcp"
        },
        "marvisvlan247": {
            "type": "dhcp"
        },
        "marvisvlan248": {
            "type": "dhcp"
        },
        "marvisvlan249": {
            "type": "dhcp"
        },
        "marvisvlan250": {
            "type": "dhcp"
        },
        "marvisvlan251": {
            "type": "dhcp"
        },
        "marvisvlan252": {
            "type": "dhcp"
        },
        "marvisvlan253": {
            "type": "dhcp"
        }
    },
    "port_config": {
        "ge-0/0/0": {
            "usage": "uplink",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/15": {
            "usage": "ap",
            "dynamic_usage": "dynamic",
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/2-3, ge-0/0/7": {
            "usage": "vc-4400-profile",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/4-6, ge-0/0/9-11": {
            "usage": "default",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-0/0/1, ge-0/0/8": {
            "usage": "access10",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-5/0/0-47,ge-6/0/0-47,ge-7/0/0-47,ge-8/0/0-47": {
            "usage": "dot1x_heb_issue",
            "dynamic_usage": "dynamic",
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "ge-1/0/0-47,ge-2/0/0-47,ge-3/0/0-47,ge-4/0/0-47,ge-9/0/0-47,ge-10/0/0-47": {
            "usage": "ap",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "mge-1/0/0-47,mge-2/0/0-47,mge-3/0/0-47,mge-4/0/0-47": {
            "usage": "default",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "mge-5/0/0-47,mge-6/0/0-47,mge-7/0/0-47,mge-8/0/0-47": {
            "usage": "stormcontrolandqos",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "mge-9/0/0-47,mge-10/0/0-47": {
            "usage": "stormcontrolandqos",
            "dynamic_usage": "dynamic",
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "xe-1/0/0-47,xe-2/0/0-47,xe-3/0/0-47,xe-4/0/0-47": {
            "usage": "ap",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "xe-5/0/0-47,xe-6/0/0-47,xe-7/0/0-47,xe-8/0/0-47": {
            "usage": "iot",
            "dynamic_usage": "dynamic",
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        },
        "xe-9/0/0-47,xe-10/0/0-47": {
            "usage": "ap",
            "dynamic_usage": None,
            "critical": False,
            "description": "",
            "no_local_overwrite": True
        }
    },
    "oob_ip_config": {
        "type": "dhcp",
        "use_mgmt_vrf": False
    },
    "extra_routes": {
        "0.0.0.0/0": {
            "via": [
                "172.30.10.254"
            ],
            "discard": False
        }
    },
    "extra_routes6": {},
    "radius_config": {
        "enabled": True,
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
        "enabled": False,
        "auth_servers_timeout": 5,
        "auth_servers_retries": 3,
        "fast_dot1x_timers": False,
        "acct_interim_interval": 0,
        "network": None,
        "coa_enabled": False,
        "coa_port": ""
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
    "vrf_config": {
        "enabled": True
    },
    "switch_mgmt": {
        "local_accounts": {
            "deviceuser": {
                "role": "admin",
                "password": "abcdfg"
            },
            "newuser": {
                "role": "admin",
                "password": "mist&123"
            }
        }
    },
    "adopted": False,
    "vars": {},
    "port_mirroring": {
        "new": {
            "output_network": "default",
            "input_port_ids_ingress": [],
            "input_port_ids_egress": [
                "ae5,ge-0/0/6,ge-0/0/10"
            ],
            "input_networks_ingress": []
        }
    },
    "id": "00000000-0000-0000-1000-a4e11abcad00",
    "name": "Shreyas-JMA",
    "site_id": "3b15346f-c581-4d5b-986b-65dd3e2b0d39",
    "org_id": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
    "created_time": 1762518317,
    "modified_time": 1769696916,
    "map_id": None,
    "mac": "a4e11abcad00",
    "serial": "FJ0223AV0853",
    "model": "EX4100-F-12P",
    "hw_rev": "A",
    "type": "switch",
    "tag_uuid": "a85ecd8b-95e9-4ce7-88e0-356b27e2486f",
    "tag_id": 587474,
    "evpn_scope": None,
    "evpntopo_id": None,
    "st_ip_base": "",
    "deviceprofile_id": None,
    "bundled_mac": None,
    "mist_configured": True
}
obj=nested_dict_to_list(payload)
obj.print_list_equivalent_of_dict()

