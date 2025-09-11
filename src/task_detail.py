import json
from datetime import datetime

import httpx
from flet import Text, Container, Column, Icon, Row, TextField, \
    Icons, alignment,  padding, Checkbox,  Page, \
    Dropdown, IconButton, dropdown, SnackBar
from flet.core.date_picker import DatePicker
from flet.core.outlined_button import OutlinedButton
from flet.core.types import MainAxisAlignment


class TaskDetail(Row):
    def __init__(self, page:Page, task_control, task_info):
        super().__init__()
        self.page = page
        self.task_control = task_control
        self.task_info = task_info
        self.page.run_task(self.build_interface)

    def on_close_click(self, e):
        self.page.end_drawer.open = False
        self.page.update()

    def __handle_update_todolist(self, ret_result) -> dict:
        dct_result = {}
        todo_data = ret_result[1].get('todo_data')
        for itm in todo_data:
            dct_result[itm.get('from_id')] = itm.get('name')
        return dct_result

    async def query_tasks_cate(self):
        # ret_result = APIRequest.query_todolist(token)
        cached_cate_list_value = await self.page.client_storage.get_async('todo_cate_list')
        cached_note_list = json.loads(cached_cate_list_value) if cached_cate_list_value else []
        if cached_note_list:
            return self.__handle_update_todolist(cached_note_list)

        token = await self.page.client_storage.get_async('token')
        url = 'https://restapi.10qu.com.cn/todo_profile/?show_expired=1'
        headers = {'Authorization': f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("获取清单失败."))
                    self.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    self.page.update()
                    return {}
                else:
                    data = resp.json()
                    ret_result = data.get('result')
                    return self.__handle_update_todolist(ret_result)
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"获取用户清单集异常：{str(ex)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
            return {}

    async def refresh(self):
        await self.task_control.update_list()

    async def on_task_date_change(self, e):
        # 调用更新任务日期接口
        token = await self.page.client_storage.get_async('token')
        sel_date = e.control.value.date()
        new_date = sel_date.strftime('%Y-%m-%d')
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': new_date}
        url = f'https://restapi.10qu.com.cn/todo/{self.task_info.get('id')}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新任务时间失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                # self.btn_sel_date.text = new_date
                btn_sel_date = self.controls[0].controls[2].content
                if btn_sel_date and isinstance(btn_sel_date, OutlinedButton):
                    btn_sel_date.text = new_date
                    e.control.page.update()
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务时间失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def on_task_cate_change(self, e):
        selected_cate = e.control.value
        new_cate = list(self.dct_cates.keys())[list(self.dct_cates.values()).index(selected_cate)]
        token = await self.page.client_storage.get_async('token')
        # update_status = APIRequest.update_task_cate(token,
        #                                             self.task_info.get('task_time'),
        #                                             self.task_info.get('id'),
        #                                             new_cate)
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': self.task_info.get('task_time'),
                      'todo_from': new_cate}
        url = f'https://restapi.10qu.com.cn/todo/{self.task_info.get('id')}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新任务目录失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务目录失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def on_task_repeat_change(self, e):
        selected_repeat = e.control.value
        lst_repeat = ['无', '每天', '每周工作日', '每周', '每月', '每年']
        idx = lst_repeat.index(selected_repeat)
        token = await self.page.client_storage.get_async('token')
        # update_status = APIRequest.update_task_repeat(token,
        #                                               self.task_info.get('id'),
        #                                               self.task_info.get('task_time'),
        #                                               idx)
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': self.task_info.get('task_time'),
                      'task_repeat': idx}
        url = f'https://restapi.10qu.com.cn/todo/{self.task_info.get('id')}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新任务重复状态失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务重复状态失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def on_task_level_change(self, e):
        selected_level = e.control.value
        lst_level = ['重要紧急', '重要不紧急', '不重要紧急', '不重要不紧急']
        idx = lst_level.index(selected_level)
        token = await self.page.client_storage.get_async('token')
        # update_status = APIRequest.update_task_level(token,
        #                                              self.task_info.get('id'),
        #                                              self.task_info.get('task_time'),
        #                                              idx)
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': self.task_info.get('task_time'),
                      'type': idx}
        url = f'https://restapi.10qu.com.cn/todo/{self.task_info.get('id')}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新任务象限失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务象限失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def on_task_name_change(self, e):
        token = await self.page.client_storage.get_async('token')
        # update_status = APIRequest.update_task_name(token,
        #                                             self.task_info.get('id'),
        #                                             e.control.value)
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_name': e.control.value}
        url = f'https://restapi.10qu.com.cn/todo/{self.task_info.get('id')}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新任务名称失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务象限失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def on_task_status_change(self, e):
        if e.control.value is False:
            return
        token = await self.page.client_storage.get_async('token')
        # ret_result = APIRequest.update_task_status(token,
        #                                            self.task_info.get('id'))
        # if ret_result is True:
        #     self.refresh()
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'todo_id': self.task_info.get('id')}
        url='https://restapi.10qu.com.cn/update_todo_status/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新任务状态失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务状态失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def on_task_desc_change(self, e):
        comment_str = e.control.value
        token = await self.page.client_storage.get_async('token')
        # update_status = APIRequest.update_task_desc(token,
        #                                             self.task_info.get('id'),
        #                                             self.task_info.get('task_time'),
        #                                             comment_str)
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'task_time': self.task_info.get('task_time'),
                      'task_desc': comment_str}
        url = f'https://restapi.10qu.com.cn/todo/{self.task_info.get('id')}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新任务描述信息失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务状态失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def on_task_delete(self, e):
        token = await self.page.client_storage.get_async('token')
        # update_status = APIRequest.delete_task(token,
        #                                        self.task_info.get('id'))
        headers = {'Authorization': f'Bearer {token}'}
        url = f'https://restapi.10qu.com.cn/todo/{self.task_info.get('id')}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.delete(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 204:
                    snack_bar = SnackBar(Text("任务删除失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                self.page.end_drawer.open = False
                await self.refresh()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务状态失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    async def build_interface(self):
        # CheckBox任务完成状态
        self.cb_name = Checkbox(
            # label=self.task.task_info.get('task_name'),
            value=self.task_info.get('task_status', 0),
            adaptive=True,
            on_change=self.on_task_status_change)

        # 任务名称
        self.tf_task_name = TextField(
            value=self.task_info.get('task_name', '未知'),
            multiline=True,
            border_width=1,
            adaptive=True,
            width=230,
            # expand=True,
            on_blur=self.on_task_name_change)

        # 任务分类
        self.dpd_cate = Dropdown(
            width=280,
            hint_text='清单',
            # icon=Icons.LIST,
            # expand=True,
            # padding=padding.only(left=10),
            on_change=self.on_task_cate_change)
        self.dct_cates = await self.query_tasks_cate()
        lst_cates = self.dct_cates.values()
        for itm in lst_cates:
            self.dpd_cate.options.append(dropdown.Option(itm))
        self.dct_cates[-1] = '--'
        self.dpd_cate.options.append(dropdown.Option('--'))
        cate_id = self.task_info.get('todo_from', -1)
        self.dpd_cate.value = self.dct_cates.get(cate_id)

        # 任务日期
        str_task_time = self.task_info.get('task_time', '--')
        if str_task_time != '--':
            dt_task_time = datetime.strptime(str_task_time, '%Y-%m-%d')
        else:
            dt_task_time = None
        self.btn_sel_date = OutlinedButton(
            text=str_task_time,
            width=280,
            on_click=lambda e: e.control.page.open(
                DatePicker(
                    value=dt_task_time,
                    open=True,
                    on_change=self.on_task_date_change,
                )
           )
        )

        # 任务重复
        lst_repeat = ['无', '每天', '每周工作日', '每周', '每月', '每年']
        self.dpd_repeat = Dropdown(
            width=280,
            hint_text='重复',
            # icon=Icons.REPEAT,
            # padding=padding.only(left=10),
            # expand=True,
            on_change=self.on_task_repeat_change)
        for itm in lst_repeat:
            self.dpd_repeat.options.append(dropdown.Option(itm))
        if not self.task_info:
            self.dpd_repeat.value = '无'
        else:
            self.dpd_repeat.value = lst_repeat[self.task_info.get('task_repeat', 0)]

        # 任务紧急度
        lst_level = ['重要紧急', '重要不紧急', '不重要紧急', '不重要不紧急']
        self.dpd_level = Dropdown(
            width=280,
            hint_text='象限',
            on_change=self.on_task_level_change)
        for itm in lst_level:
            self.dpd_level.options.append(dropdown.Option(itm))
        self.dpd_level.value = lst_level[self.task_info.get('type', 0)]

        self.tf_comment = TextField(
            hint_text='添加备注',
            multiline=True,
            width=280,
            # expand=True,
            border_width=1,
            border_radius=2,
            value=self.task_info.get('task_desc', ''),
            on_blur=self.on_task_desc_change
        )

        row_top = Row(
            controls=[self.cb_name, self.tf_task_name],
            alignment=MainAxisAlignment.START,
            adaptive=True,
            # expand=True,
        )

        if not self.task_info:
            create_time = '--'
        else:
            create_time = self.task_info.get('create_time').split('.')[0]

        row_bottom = Row(
            controls = [
                Icon(name=Icons.FORWARD),
                Text(f"{create_time}  创建",expand=True),
                IconButton(icon=Icons.DELETE,
                        on_click=self.on_task_delete),
                ],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )

        col_detail = Column(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            adaptive=True,
            controls = [
                Container(
                    adaptive=True,
                    content=row_top,
                    padding=padding.only(top=10),
                ),
                Container(
                    adaptive=True,
                    content=self.dpd_cate,
                    padding=padding.only(left=10, right=0, top=2, bottom=2)
                ),
                Container(
                    adaptive=True,
                    content=self.btn_sel_date,
                    padding=padding.only(left=10, right=0, top=2, bottom=2)
                ),
                Container(
                    adaptive=True,
                    content=self.dpd_repeat,
                    padding=padding.only(left=10, right=0, top=2, bottom=2)
                ),
                Container(
                    adaptive=True,
                    content=self.dpd_level,
                    padding=padding.only(left=10, right=0, top=2, bottom=2)
                ),
                Container(
                    adaptive=True,
                    content=self.tf_comment,
                    padding=padding.only(left=10, right=0, top=2, bottom=2),
                ),
                Container(expand=True),
                Container(
                    adaptive=True,
                    content=row_bottom,
                    padding=padding.only(left=10),
                    alignment=alignment.bottom_left
                )
            ],
        )

        # return col_detail
        self.controls = [col_detail]
        self.page.update()
