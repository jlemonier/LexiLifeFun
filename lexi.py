## Lexi Life
## - Jason LeMonier experimenting with Lexi API

##############################################################################
### Quick Start Notes ########################################################
# Set 4 environment variables: lexi_username, lexi_password, lexi_client_id, lexi_client_secret
# set lexi_username=jason@fun.com
# set lexi_password=LoveLexi
# set lexi_client_id=

parameter_hub_name = "Ratto Kickstarter"  # This helps the code choose from your list of hubs
user_guid          = "1e8e23d4-5288-485c-bff0-b01d4b4b1b00"  # From Cloud Api Tester

# Not needed if hub_name above is correct
# hub_guid         = "46b59a84-1dd2-11b2-bceb-410665d07897"
##############################################################################

import os
import json
from session import Session
import time

LEXI_HUB_SLEEP = 250

def sleep(milliseconds):
    print (f"       ........... sleeping for {milliseconds} ... ")
    time.sleep(milliseconds / 1000.0)

def ev(key, default_value):
    return os.environ.get(key, default_value)

class Urls:
    TOKEN = "https://lexidevice.com/oauth/token"
    DEV_LOGIN = "https://lexidevice.com/developer/login"
    

class Lexi(Session):
    def __init__(self, debug_minimal = True):
        super().__init__()
        # self.set_access_token()
        
        if debug_minimal:
            self.set_debug_minimal()
        
        self.myhub = {}
        self.myhub["ip"]   = "127.0.0.1"  # Defaulting to local server so remote/hub urls make sense w/o errors
        self.myhub["guid"] = "ce31f51d-92c3-xxxx-ba1e-xxxxxxxxxxxx"

        self.dev_login()
        self.hubs(parameter_hub_name)     # This sets correct hub info!!

    def get_my_hub(self):
        return self.myhub

    def _lexi_headers(self, h):
        h["authority"]  = "lexidevice.com"
        h["method"]     = "POST"
        h["path"]       = "/developer/login"
        h["scheme"]     = "https"
        h["referer"]      = "https://lexidevice.com/developer/login"

    def dev_login(self):
        url = Urls.DEV_LOGIN
        self.get(url)           # We have a Session so cookies are handled

        data = {}
        self._set_user_pass(data)
        self._set_client(data)
        data["grant_type"] = "password"
                
        h = {}  # dict for headers
        self._lexi_headers(h)

        # Allow content-type & content-length to be handled in post
        # h["content-type"] = "application/json" # "application/x-www-form-urlencoded" (default from browser)
        self.post(url, data = data, headers = h)
        
        # print (resp1.headers)
        # print (resp1.text)
        
        self.set_access_token()
    
    def get_user_guid(self):
        # TODO (automatically figure this out from login/password
        return user_guid
    
    def get_hub_guid(self):
        # TODO - show names & guids from hubs
        return self.get_my_hub().get("guid")

    """
        _set* methods helps to easily add key=value data wherever needed
    """
 
 
 
    def _set_userGuid(self, data):
        """ userGuid """
        data["userGuid"] = self.get_user_guid()
    
    def _set_hubGuid(self, data):
        data["hubGuid"]  = self.myhub.get("guid")
    
    def _set_user_pass(self, data):
        # Avoid duplication.  Add these key=values to any map/dict
        data["username"]      = ev("lexi_username"      , "username NOT_EMAIL")
        data["password"]      = ev("lexi_password"      , "LexiLife.io")
    
    def _set_client(self, data):
        # From Cloud Api Tester
        # <option value="42" data-id="vD******" data-secret="iPS*********">Party Life</option>
        data["client_id"]     = ev("lexi_client_id"     , "lexi Dev API signup and create an App")
        data["client_secret"] = ev("lexi_client_secret" , "")
    
    def get_data_user_hub(self, set_guid_to_userGuid = True):
        """ userGuid, hubGuid, guid=USER_GUID """
        data = {}
        self._set_hubGuid(data)
        self._set_userGuid(data)
        if set_guid_to_userGuid:
            data["guid"] = self.get_user_guid()
        return data
    
    def get_data_user(self):
        """ guid = USER GUID => actions ON / OFF need this"""
        data = {}
        data["guid"] = self.get_user_guid()
        return data
    
    def user(self):
        return self.get_data_user()
    
    def set_access_token(self):
            
        data = {}
        self._set_user_pass(data)
        self._set_client(data)
        data["grant_type"]    = "password"

        response = self.post(Urls.TOKEN, data)
        self.token_data = json.loads(response.text)
        print (f"access_token retrieved: {self.get_access_token() }")
      
    def get_access_token(self):
        return self.token_data.get("access_token")

    def hubs(self, hub_to_use = "If more than one"):
        url = "https://lexidevice.com/api/v1/oauth/hub/myhubs"
        
        data = {} # self.token_data()
        data["access_token"] = self.get_access_token()
        data["user_guid"] = self.get_user_guid()
        self._set_user_pass(data)
        
        h = {}
        self._lexi_headers(h)
        
        hubs_response = self.post(url, data, h)
        hubs_json = hubs_response.text
        
        hd = self.hubs_data = json.loads(hubs_json)
        hubs = hd.get("hubs")
        # ip guid name hub_owner_guid

        for h in hubs:
            # print (f"hub name: {h['name']} - ip: {h['ip']} guid: {h['guid']} ")
            if h['name'] == hub_to_use:
                print (f"    Found hub: {h['name']} ... ready to post to: {h['ip'] } ")
                self.myhub = h

        if len(hubs) == 1:
            self.myhub = h  # Default if ony 1

    def url(self, path, remote = False):
        """ 
        # https://bridge.lexidevice.com/remote/api/system/ping
        # http://{HUB IP}:8000                /api/system/ping
        """
        if remote:
            domain = f"https://bridge.lexidevice.com/remote"
        else:
            ip = self.myhub.get("ip")
            domain = f"http://{ip}:8000"
            
        url = f"{domain}{path}"
        return url

    def system_ping(self, remote = False):
        # https://bridge.lexidevice.com/remote/api/system/ping"
        # http://{HUB IP}                     /api/system/ping
        
        url = self.url("/api/system/ping", remote)
        data = {}
        self._set_userGuid(data)
        self._set_hubGuid(data)

        self.post(url, data)

    def discover(self, remote = False):
        url = self.url("/api/hub/discover", remote)
        data = {}
        self._set_hubGuid(data)
        return self.post(url, data)
        
    def registeredByManufacturer(self, remote = False):
        url = self.url("/api/hub/device/getRegisteredByManufacturer", remote)
        return self.post(url, self.get_data_user_hub(True))

    def registeredByType(self, remote = False):
        url = self.url("/api/hub/device/getRegisteredByType", remote)
        return self.post(url, self.get_data_user_hub(True))

    def scene_list(self, remote = False):
        url = self.url("/api/scene/list", remote)
        self.post(url, self.get_data_user_hub(True))

    def on(self, device, color, brightness):
        """ Device is "id" such as 6 not any guid """
        d = self.get_data_user()
        
        user = d["guid"]       = self.get_user_guid()
        d["device"]     = device  # "7"  NOT "1f86a80e-9009-11ea-86d6-b827eb6ed5d9"
        d["color"]      = color
        d["brightness"] = brightness
        
        url = self.url("/api/device/turnOn") 
        self.put(url, d)
        
        sleep(LEXI_HUB_SLEEP)

    def status(self, device):
        d = self.user()
        d["device"] = device
        
        url = self.url("/api/device/status") 
        return self.post(url, d)

    def status_all(self):
        d = self.user()
        url = self.url("/api/device/status/all")
        self.post(url, d)

    def group_list(self):
        url = self.url("/api/group/list")
        d = self.get_data_user_hub()
        self.post(url, d)

    def meta_data_testing_1(self):
        lexi.group_list()
        lexi.status_all()

        for remote in [True, False]:
            print (f"Running API tests -- remote={remote} ")
            
            lexi.system_ping(remote)
            lexi.discover(remote)
            lexi.scene_list(remote)
            lexi.registeredByManufacturer(remote)
            
            lexi.registeredByType(remote)
        

    def light_test_1(self):
        ms = 100
        lexi.on(3, "100,100,100", 25)
        sleep(ms)
        lexi.on(3, "200,200,200", 100)
        if False:
            sleep(ms)
            lexi.on(3, "100,100,100", 25)
            sleep(ms)
            lexi.on(3, "200,200,200", 50)
            sleep(ms)
            lexi.on(3, "100,100,100", 75)
            sleep(ms)
            lexi.on(3, "200,200,200", 100)
            sleep(ms)

        
        
        

# Lexi object inherits Session to handle cookies, http posts, etc
lexi = Lexi()
# Added to init
# lexi.dev_login()
# lexi.hubs(parameter_hub_name)     # This sets correct hub info!!

# print (f"Hub Info: {lexi.get_my_hub()} ")

if False:
    lexi.meta_data_testing_1()
    lexi.light_test_1()
    
# lexi.rotate_group(7)

