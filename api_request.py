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
    def send_sms(phone_num):
        user_input = {'mobile': phone_num}
        req = requests.post(url='https://restapi.10qu.com.cn/sms_code/',
                            data=user_input)
        return req

    @staticmethod
    def login_by_code(phone_num, sms_code):
        user_input = {'mobile': phone_num,
                      'sms_code': sms_code}
        req = requests.post(url='https://restapi.10qu.com.cn/mobile_login/',
                            data=user_input)
        json_req = json.loads(req.text)
        return json_req

    @staticmethod
    def logout(token):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.get(url=f'https://restapi.10qu.com.cn/logout/',
                           headers=headers)
        json_req = json.loads(req.text)
        return json_req.get('code') == '0'

    @staticmethod
    def registry(username, password):
        user_input = {'custom_username': username,
                      'password': password}
        req = requests.post(url='https://restapi.10qu.com.cn/username_register/',
                            data=user_input)
        json_req = json.loads(req.text)
        return json_req

    @staticmethod
    def query_user_info(token):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/user_info/',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('results')
        return dct_ret

    @staticmethod
    def query_todolist(token):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/todo_profile/?show_expired=1',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('result')
        return dct_ret

    @staticmethod
    def query_tasks_by_date(token, str_date, task_status):
        headers = {'Authorization': f'Bearer {token}'}
        if task_status is False:
            url = f'https://restapi.10qu.com.cn/todo_search/?task_time={str_date}&task_status={task_status}'
        else:
            url = f'https://restapi.10qu.com.cn/todo_search/?task_time={str_date}'
        req = requests.get(url=url,
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('results')
        return lst_ret

    @staticmethod
    def query_future_tasks(token):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/todo_type_profile/',
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('result')
        return lst_ret

    @staticmethod
    def query_expired_tasks(token):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/todo_type_profile/?flag=expired',
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('result')
        return lst_ret

    @staticmethod
    def query_tasks_by_cate_id(token, cate_id, task_status=False):
        headers = {'Authorization': f'Bearer {token}'}
        if task_status is False:
            url = f'https://restapi.10qu.com.cn/user_todo/?todo_from_id={cate_id}&task_status={task_status}'
        else:
            url = f'https://restapi.10qu.com.cn/user_todo/?todo_from_id={cate_id}'
        req = requests.get(url=url,
                           headers=headers)
        json_req = json.loads(req.text)
        lst_ret = json_req.get('result')
        return lst_ret

    @staticmethod
    def add_task(token, task_name, task_repeat, task_time, task_cate, task_type):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_name': task_name,
                      'task_repeat': task_repeat,
                      'task_time': task_time,
                      'todo_from': task_cate,
                      'type': task_type}
        if task_cate is None or task_cate == '' or task_cate in ['today', 'future', 'expired']:
            del user_input['todo_from']
        req = requests.post(url='https://restapi.10qu.com.cn/todo/',
                            headers=headers,
                            data=user_input)
        # json_req = json.loads(req.text)
        return req.status_code == 201

    @staticmethod
    def update_task_status(token, task_id):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'todo_id': task_id}
        req = requests.put(url='https://restapi.10qu.com.cn/update_todo_status/',
                           headers=headers,
                           data=user_input)
        if req.status_code in [200, 201, 202]:
            json_req = json.loads(req.text)
            if json_req.get('code') == '0':
                return True
        return False

    @staticmethod
    def update_task_time(token, task_id, task_time):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': task_time}
        req = requests.put(url=f'https://restapi.10qu.com.cn/todo/{task_id}/',
                           headers=headers,
                           data=user_input)
        return req.status_code == 200

    @staticmethod
    def update_task_cate(token, task_time, task_id_from, task_id_to):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': task_time,
                      'todo_from': task_id_to}
        req = requests.put(url=f'https://restapi.10qu.com.cn/todo/{task_id_from}/',
                           headers=headers,
                           data=user_input)
        return req.status_code == 200

    @staticmethod
    def update_task_repeat(token, task_id, task_time, task_repeat):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': task_time,
                      'task_repeat': task_repeat}
        req = requests.put(url=f'https://restapi.10qu.com.cn/todo/{task_id}/',
                           headers=headers,
                           data=user_input)
        return req.status_code == 200

    @staticmethod
    def update_task_level(token, task_id, task_time, task_level):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': task_time,
                      'type': task_level}
        req = requests.put(url=f'https://restapi.10qu.com.cn/todo/{task_id}/',
                           headers=headers,
                           data=user_input)
        return req.status_code == 200

    @staticmethod
    def update_task_name(token, task_id, task_name):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_name': task_name}
        req = requests.put(url=f'https://restapi.10qu.com.cn/todo/{task_id}/',
                           headers=headers,
                           data=user_input)
        return req.status_code == 200

    @staticmethod
    def update_task_desc(token, task_id, task_time, task_desc):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': task_time,
                      'task_desc': task_desc}
        req = requests.put(url=f'https://restapi.10qu.com.cn/todo/{task_id}/',
                           headers=headers,
                           data=user_input)
        return req.status_code == 200

    @staticmethod
    def delete_task(token, task_id):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.delete(url=f'https://restapi.10qu.com.cn/todo/{task_id}/',
                              headers=headers)
        return req.status_code == 204

    @staticmethod
    def add_task_list(token, list_name):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'name': list_name}
        req = requests.post(url='https://restapi.10qu.com.cn/todo_from/',
                            headers=headers,
                            data=user_input)
        return req.status_code == 201

    @staticmethod
    def delete_task_list(token, tasklist_id):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.delete(url=f'https://restapi.10qu.com.cn/todo_from/{tasklist_id}/',
                              headers=headers)
        return req.status_code == 204

    @staticmethod
    def update_task_list(token, cate_id, new_name):
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'name': new_name}
        req = requests.put(url=f'https://restapi.10qu.com.cn/todo_from/{cate_id}/',
                           headers=headers,
                           data=user_input)
        return req.status_code == 200
