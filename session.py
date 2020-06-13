
from http import cookies
import requests
import urllib
import re
import json
import enum

"""
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
"""

class DF(enum.Enum):
    """ Debug Flags/Types enum 
    
    Enums are an easy & safe way to set and control several settings
    
    
        -- All with int 0 .. 99   will be set to true  for errors (if ErrorsShowAll) (for failed request)
        -- All with int -1 .. -99 will be set to false for errors (if ErrorsShowAll)
    """
    
    # Booleans
    Url         = 7
    Cookies     = 1     # Eclipse needs = 1 for lookahead
    Headers     = 2 
    FormData    = 3 
    UrlEncoded  = 5
    ResponseText= 4
    ResponseHeaders = 8
    JsonPretty  = 6

    TrimResponse        = -2    # Leading & trailing whitespace
    TruncateReponse     = -1    # Helpful for screen scraping when false
    
    DebugSettingChanges = 101
    ObscureFormPost     = 108   # Not obscuring GET (for now)
    ResponseTextOneLine = 109
    
    ErrorsShowAll = 200
    OneLineOnly   = 201         # Even if there is an error ... 1 line

    # Ints
    ResponseLength       = 220
    JsonResponseLength   = 221

    # Strings
    ObscureOutputSubstrings = 300
    PadReponseText          = 301

class Session:
    

    """ Post to get IP address 
    APP NAME    CLIENT ID    CLIENT SECRET    ACTION
    Party Life    vDRc2uQb    iPSqzQIUYkYk
    """
    def __init__(self):
        self.cookies = None
        self.sess    = requests.Session()
        di = self.debug_info = {}

        di[DF.ObscureOutputSubstrings] = "password,client_,user_,access_"
        self.obscure_dict = di[DF.ObscureOutputSubstrings].split(",")

        self.set_debug_development()

    def set_debug_minimal(self):
        di = self.debug_info
        di[DF.Cookies] = False
        di[DF.Headers] = False
        di[DF.FormData]= False
        di[DF.ResponseText] = False

    def set_debug_development(self):
        di = self.debug_info

        # Defaults ...
        di[DF.Url]          = True
        di[DF.Cookies]      = False
        di[DF.Headers]      = False
        di[DF.FormData]     = True
        di[DF.UrlEncoded]   = True
        di[DF.TrimResponse] = True
        di[DF.TruncateReponse] = True
        di[DF.DebugSettingChanges] = True

        di[DF.JsonPretty]      = True
        di[DF.ObscureFormPost] = True
        di[DF.OneLineOnly]     = False
        
        di[DF.ResponseHeaders] = True
        di[DF.ResponseText] = True
        di[DF.ResponseTextOneLine] = False
        
        di[DF.ResponseLength] = 500
        di[DF.JsonResponseLength] = 2000
        di[DF.PadReponseText] = '-'*100 + "\n"

    def set_debug_errors_only(self):
        di = self.debug_info
        

    def set_debug_state(self, df_key, df_value):
        """ DF_key such as: DF.Cookies
            DF_value must match type of existing value or warning will occur """
        di = self.debug_info
        v0 = di[df_key]
        t0 = type(v0)
        
        t1 = type(df_value)
        
        if t1 == t0:
            di[df_key] = df_value
            if di[DF.DebugSettingChanges]:
                print (f"Session debug_info[{df_key}] = {df_value}  (was: {v0} )")
        else:
            print (f"Warning: debug_info[{df_key}] = {v0} with type: {t0} could not be set to: {v1} with type: {t1} )")

    def _obscure(self, key):
        for obs_key in self.obscure_dict:
            if re.search(obs_key, key):
               return True
        return False 

    def get(self, url, data = {}):
        return self.post(url, data, {}, method = "GET")

    def put(self, url, data):
        return self.post(url, data, {}, method = "PUT")

    def _debug_post(self, url, method, data, headers, resp):

        result = []
        di  = self.debug_info

        # Debug info for failed POST/http call
        resp_status = resp.status_code
        if resp_status >= 400 and di[DF.ErrorsShowAll]:
            di2 = di.copy()
            for debug_key in DF:    # Cookies = 1
                dki = int(debug_key)
                if 1 <= dki <= 99:
                    di2[debug_key] = True
                if -99 <= dki <= -1:
                    di2[debug_key] = False
            di = di2    # For this request only
        
        nl  = "\n"; t = "\t"
        if di[DF.OneLineOnly]:
            nl = " | "; tab = " - "

        if di[DF.Url]:
            result.append(f"{method} => {url}") 

        if di[DF.Cookies]:
            result.append (f"{t}cookies: ")
            for c in self.sess.cookies:
                result.append (f"{t}{t}{c}")

        if di[DF.Headers]:
            result.append (f"{t}request headers:")
            for h in headers.keys():
                result.append (f"\t\t{h} => {headers[h]}")
    
        if di[DF.FormData]:
            result.append (f"{t}form data:")
            
            for k in data.keys():
                v = data[k]
                if di[DF.ObscureFormPost] and self._obscure(k):
                    v = "*" * len(v)
                result.append(f"{t}{t}{k} => {v}")
        
        ct = resp.headers.get("content-type")
        result.append(f"{t}response-code: {resp.status_code} {t} content-type: {ct} {t} content-size: {len(resp.text)} {t} reason: {resp.reason}")

        if [di[DF.ResponseHeaders]]:
            rh = resp.headers
            result.append(f"{t}response headers:")
            for k in rh.keys():
                result.append(f"{t*2}{k} => {rh[k]} ")

        resp_text_display = self._format_response_text(resp.text, di)
        result.append(resp_text_display)
        
        print (nl.join(result))
        # self._debug_post(data, headers)

    def pp(self, arg, comment = ""):
        
        s = self.pretty(json.dumps(arg))
        
        print (f"{comment} => {s} ")
    def pretty(self, arg):
        try:
            data = json.loads(arg)
            pretty = json.dumps(data, indent=2, sort_keys=True)
            text = pretty
        except Exception as e:
            print (f"Failed parsing json: {e} ")
            text = json

        return text

    def data_sorted(self, arg):
        try:
            json_obj = json.loads(arg)
            pretty_sorted_text = json.dumps(json_obj, indent=2, sort_keys=True)
            data = json.loads(pretty_sorted_text)
            return data
            
        except Exception as e:
            print (f"Failed parsing json: {e} ")
            return arg

    def _format_response_text(self, text, debug_info_override):
        
        di = debug_info_override
        if not di[DF.ResponseText]:
            return ""
        
        nl  = "\n"; t = "\t"
        if di[DF.OneLineOnly]:
            nl = " | "; tab = " - "
        
        is_json = False
        if di[DF.TrimResponse]:
            text = text.strip()
            is_json = text.startswith("{")
        else:
            if di[DF.JsonPretty]:
                text2 = text.trim()
                is_json = text2.startswith("{")
        
        if is_json and di[DF.JsonPretty]:
            text = pretty(text)

        if di[DF.TruncateReponse]:
            maxlen = di[DF.JsonResponseLength] if is_json else di[DF.ResponseLength]
            
            append = f" ... (truncated) "
            text = f"{text[:maxlen]}{nl}{append}{nl}" if len(text) > maxlen else text 
        
        if di[DF.OneLineOnly]:
            text = re.sub('[\r\n]', '', text)
        
        else:
            pad = di[DF.PadReponseText]
            text = f"{pad}{text}{nl}{pad}"

        return text
        
    def post(self, url, data, headers = {}, method = "POST"):
        di = self.debug_info
        
        method = method.upper()
        urlencoded_data = urllib.parse.urlencode(data)
        
        if method in ("POST","PUT"):
            headers["content-type"]   = "application/x-www-form-urlencoded"
            headers["content-length"] = str(len(urlencoded_data))               # type & length were critical!! Or Server 500
        
        if method in ("GET"):
            params = f"?{urlencoded_data}" if len(urlencoded_data) > 0 else ""
            url = f"{url}{params}"
        
        if method == "POST":
            resp = self.sess.post(url, data=urlencoded_data, headers = headers)
        elif method == "PUT":
            resp = self.sess.put(url, data)
        elif method == "GET":
            resp = self.sess.get(url)
        elif method == "DELETE":
            resp = self.sess.delete(url)
        else:
            print (f"method: {method} - not supported. ?")
            return
        
        self._debug_post(url, method, data, headers, resp)

        return resp

