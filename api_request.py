import requests
import json


class APIRequest(object):

    @staticmethod
    def login_by_password(username, password):
        user_input = {'username': username,
                      'password': password}
        req = requests.post(url='https://restapi.10qu.com.cn/username_login/',
                            data=user_input)
        return req

    @staticmethod
    def logout(token):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url=f'https://restapi.10qu.com.cn/logout/',
                           headers=headers)
        json_req = json.loads(req.text)
        return json_req.get('code') == '0'

    @staticmethod
    def query_user_info(token):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/user_info/',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('results')
        return dct_ret

    @staticmethod
    def query_todolist(token):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/todo_profile/?show_expired=1',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('result')
        return dct_ret

    @staticmethod
    def query_tasks_by_date(token, str_date):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url=f'https://restapi.10qu.com.cn/todo_search/?task_time={str_date}',
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('results')
        return lst_ret

    @staticmethod
    def query_future_tasks(token):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/todo_type_profile/',
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('result')
        return lst_ret

    @staticmethod
    def query_expired_tasks(token):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/todo_type_profile/?flag=expired',
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('result')
        return lst_ret

    @staticmethod
    def query_tasks_by_cate_id(token, cate_id):
        headers = {'Authorization': f'jwt {token}'}
        req = requests.get(url=f'https://restapi.10qu.com.cn/user_todo/?todo_from_id={cate_id}',
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('result')
        return lst_ret

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

    @staticmethod
    def update_task_status(token, task_id):
        headers = {'Authorization': f'jwt {token}'}
        user_input = {'todo_id': task_id}
        req = requests.put(url='https://restapi.10qu.com.cn/update_todo_status/',
                           headers=headers,
                           data=user_input)
        if req.status_code in [200, 201, 202]:
            json_req = json.loads(req.text)
            if json_req.get('code') == '0':
                return True
        return False
