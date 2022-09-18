import requests
import json


class APIRequest(object):

    @staticmethod
    def logout(token):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url=f'https://restapi.10qu.com.cn/logout/',
                           headers=headers)
        json_req = json.loads(req.text)
        return json_req.get('code') == '0'
