from lexi_info import LexiInfo
import json
from session import DF
from collections import defaultdict, OrderedDict
from lexi import sleep

""" Handy to have eyes on json format ...
{
  "lexi": "/hub/device/getRegisteredByType",
  "lighttypes": [
    {
      "106": {
        "deviceCount": 5,
        "devices": [
          {
            "brand": "Lexi",
            "com": "mesh",
            "family": "luminaire",
            "guid": "98535258-a712-11ea-b0f9-b827eb6ed5d9",
            "hub": "46b59a84-1dd2-11b2-bceb-410665d07897",
            "id": 32,
            "ipaddr": "8023",
            "last_value": "255,255,255;15;3",
            "macaddress": "70B3D5AC50A0",
            "model": "BRC-GU10-HTA-001",
            "name": "K2",
            "status": 0,
            "swversion": "1",
            "taxonomyID": 12,
            "type": "124"
          },
          {
            "brand": "Lexi",
            "com": "mesh",

"""

class LexiFun(LexiInfo):

    def _array(self):
        return []
    def _dict(self):
        return {}   # OrderedDict didn't work here
 
    def _get_info(self):
        reg_info = self.registeredByType(False)
        
        # lights2 is a dict with every key => {"Tea 7" => {device data } } already set to append
        lights2 = defaultdict(self._dict)

        lighttypes_array = json.loads(reg_info.text)["lighttypes"]
        for lt in lighttypes_array:
            # print (f"lt => {lt}")
            for dtype, devices in lt.items():
                # print (f"{dtype} {type(dtype) } {type(devices) } {devices.keys() }")
                # 106 <class 'str'> <class 'dict'> dict_keys(['deviceCount', 'devices', 'name'])
                d2 = devices["devices"]
                for d in d2: 
            
                    dtype = d['type']
                    dname = d['name']
                    
                    # lights[dtype].append(d)
                    lights2[dtype][dname] = d
                    
        return lights2

    def rotate_group(self, brightness):
        """ Make motion! """
        # type or group
        # get regByType ... list each light: name|id|status
        
        reg_info = self._get_info()
        self.pp (reg_info, "reg_info")

        for reg_id, reg_hash1 in reg_info.items():
            print (f"reg_id:{reg_id} devices:{len(reg_hash1)} ")
            
            
            dev_names = sorted(reg_hash1.keys())
            
            if len(dev_names) <= 1:
                continue

            dname_last = dev_names[-1]
            dev_last   = reg_hash1[dname_last]
            
            for dname in dev_names:
                
                dev = reg_hash1[dname]
                id  = dev['id']
                name= dev['name']
                color , b, cx   = dev_last["last_value"].split(";")
                
                print (f"{id} {name} {color} {b}")
                
                lf.on(id, color, b)
                
                dname_last = dev['name']
                dev_last   = reg_hash1[dname_last]
            

    def old_ref(self):        

        for i in [0]:
            offset = -1 -i 
            if abs(i) >= len(teas):
                offset = -1
            last_name = names[offset]
            last = teas[last_name]
                
            for device_name in sorted(teas):
                ddata = teas[device_name]
                
                color0, b0, cx0 = ddata["last_value"].split(";")
                
                color , b, cx   = last["last_value"].split(";")
                id = ddata["id"]
                name = ddata["name"]
                
                print (f"{id} {name} => color:{color} was: {color0} => b:{b}")
                lf.on(id, color, brightness)
                
                last = ddata
                last_name = name
                
    def set_tea(self, brightness = "100"):
        lf.on("23", "48,255,197" , brightness)
        lf.on("24", "123,240,255", brightness)
        lf.on("26", "193,122,255", brightness)
        lf.on("25", "255,158,216", brightness)
        lf.on("27", "255,106,186", brightness)
        lf.on("28", "255,63,70"  , brightness)
        
    def set_tea2(self, brightness = "100"):
        lf.on("28", "48,255,197" , brightness)
        lf.on("27", "123,240,255", brightness)
        lf.on("25", "193,122,255", brightness)
        lf.on("26", "255,158,216", brightness)
        lf.on("24", "255,106,186", brightness)
        lf.on("23", "255,63,70"  , brightness)
        
      
lf = LexiFun()
# lf.set_debug_development()
lf.set_tea()
# lf.set_tea2()

for i in range(500000):
    b = "100" if i % 2 == 0 else "50"
    lf.rotate_group(b)
    
    print (f"Rotating lights by type ... {i} ")
    sleep(2000)

# lf.set_debug_state(DF.TruncateReponse, False)
# lf.rotate_group(0)

# lf.set_tea("25")
#for brightness in ("100", "50", "25", "100"):
#    lf.set_tea(brightness)
#     lf.rotate_group(7)



"""
    -- Hub had this saved.  Turned on group ... all to 1 color?  
Tea Lights only ...
    28 - Tea 6 - 255,63,70;100;0 - type:136 - status: 0
    26 - Tea 3 - 193,122,255;100;0 - type:136 - status: 0
    25 - Tea 4 - 255,158,216;100;0 - type:136 - status: 0
    24 - Tea 2 - 123,240,255;100;0 - type:136 - status: 0
    23 - Tea 1 - 48,255,197;100;0 - type:136 - status: 0
    27 - Tea 5 - 255,106,186;100;0 - type:136 - status: 0
"""



