import json
import urllib.request


def webRequest(url):
    try:
        req = urllib.request.Request(url)
        r = urllib.request.urlopen(req).read()
        output = json.loads(r.decode('utf-8'))
        return output
    except:
        print('HTTP request to: ' + url + ' failed.')
