import datetime
import time
import random
import json
import requests
from youtalk.creds import DYNAMIC_LINKS_API

def random_alphanumeric(length=9,lowercase=True,uppercase=True):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXY'
    if lowercase:
        chars += "abcdefghijklmnopqrstuvwxyz"
    code = ""
    for x in range(length):
        code += random.choice(chars)
    return code

def getDateAtGap(day_increment=0):
    per_day_time_microseconds = 24 * 60 * 60 * 1000 * 1000
    now_time = time.time() * 1000 * 1000
    millsGap = (per_day_time_microseconds * abs(day_increment))
    if day_increment<0:
        target_time = now_time - millsGap
    else:
        target_time = now_time + millsGap
    final_date = datetime.date.fromtimestamp(target_time/1000000)
    return final_date.strftime("%Y-%m-%d")  

def get_short_link(link):
    try:
        dynamicLinkData = {
                            "dynamicLinkInfo": {
                                "domainUriPrefix": "https://filmmee.page.link",
                                "link": "https://filmmee.com"+link,
                                "androidInfo": {
                                    "androidPackageName": "com.sevenmbtech.utokcore",
                                    "androidMinPackageVersionCode":"12"
                                },
                                "navigationInfo": {
                                    "enableForcedRedirect": True
                                },
                                "iosInfo": {
                                    "iosBundleId": "com.sevenmbtech.utokcore",
                                    "iosAppStoreId":"1542626766"
                                }
                            }
                        }
        dynamicLinkData = json.dumps(dynamicLinkData)                            
        dynamicLinkResponse = requests.post(DYNAMIC_LINKS_API,data=dynamicLinkData)
        short_link = json.loads(dynamicLinkResponse.text)
        return short_link['shortLink']
    except:
        return ""    
