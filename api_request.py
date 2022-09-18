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

    @staticmethod
    def add_task(token, task_name, task_repeat, task_time, task_cate, task_type):
        headers = {'Authorization': f'jwt {token}'}
        user_input = {'task_name': task_name,
                      'task_repeat': task_repeat,
                      'task_time': task_time,
                      'todo_from': task_cate,
                      'type': task_type}
        req = requests.post(url='https://restapi.10qu.com.cn/todo/',
                            headers=headers,
                            data=user_input)
        # json_req = json.loads(req.text)
        return req.status_code in [200, 201]
