from datetime import datetime, timedelta

import httpx
from flet import Text, Container, Column, Icon, Row, TextField, \
    Icons, Colors, Switch, SnackBar, ListView
from flet.core import border
from flet.core.alert_dialog import AlertDialog
from flet.core.app_bar import AppBar
from flet.core.bottom_sheet import BottomSheet
from flet.core.date_picker import DatePicker
from flet.core.divider import Divider
from flet.core.floating_action_button import FloatingActionButton
from flet.core.form_field_control import InputBorder
from flet.core.icon_button import IconButton
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.popup_menu_button import PopupMenuButton, PopupMenuItem
from flet.core.progress_ring import ProgressRing
from flet.core.safe_area import SafeArea
from flet.core.text_button import TextButton
from flet.core.types import MainAxisAlignment, ScrollMode, CrossAxisAlignment, FontWeight

from task import Task
from nav import NavControl
from task_detail import TaskDetail


class TaskListControl(Column):
    def __init__(self, page, list_id):
        super().__init__()
        self.page = page

        self.str_task_date = datetime.today().strftime('%Y-%m-%d')
        self.n_task_level = 0
        self.n_task_repeat = 0

        self.list_name = list_id
        self.list_title = None
        self.show_finished = False

        # 修改对话框
        self.tf_cate = TextField(hint_text='请输入清单名称')
        self.dlg_rename_cate = AlertDialog(
            modal=True,
            title=Text('重命名清单'),
            content=self.tf_cate,
            actions=[TextButton("确定", on_click=self.on_dlg_rename_cate_ok_click),
                     TextButton("取消", on_click=self.on_dlg_rename_cate_cancel_click)],
            actions_alignment=MainAxisAlignment.END,
            title_padding=10,
            # on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        # 删除对话框
        self.dlg_delete_confirm = AlertDialog(
            modal=True,
            title=Text('您确定吗?'),
            content=Column(
                controls=[Divider(height=1, color='gray'),
                          Text('您确定要删除此清单吗?'),
                          ],
                alignment=MainAxisAlignment.START,
                width=200,
                height=50,
            ),
            actions=[TextButton("确定", on_click=self.on_dlg_delete_confirm_ok_click),
                     TextButton('取消', on_click=self.on_dlg_delete_confirm_cancel_click)],
            actions_alignment=MainAxisAlignment.END,
            title_padding=10,
            # on_dismiss=lambda e: print("对话框已关闭!"),
        )

        # 左侧drawer
        self.drawer = NavigationDrawer(
            position=NavigationDrawerPosition.START,
            controls=[
                Container(
                    content=NavControl(page),
                    expand=1,
                    padding=0,
                )
            ]
        )
        task_list_menu_btn = PopupMenuButton(
            items=[
                PopupMenuItem(icon=Icons.EDIT, text='重命名列表',
                              on_click=self.on_rename_list),
                PopupMenuItem(icon=Icons.DELETE, text='删除列表',
                              on_click=self.on_delete_list)
            ]
        )
        task_list_menu_btn.visible = self.list_name not in ['today', 'future', 'expired', 'all']
        self.page.appbar = AppBar(
            title=Text('布尔清单', color=Colors.WHITE),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            actions=[task_list_menu_btn],
        )

        # 右侧drawer
        detail_info = TaskDetail(self.page, self, {})
        self.end_drawer = NavigationDrawer(
            position=NavigationDrawerPosition.END,
            controls=[
                Container(
                    content=detail_info,
                    width=300,
                    bgcolor='#f2f4f8',
                    border=border.all(1, Colors.BLACK12),
                    # on_hover=self.on_detail_hover,
                )
            ]
        )

        self.page.floating_action_button = FloatingActionButton(
            icon=Icons.ADD,
            bgcolor=Colors.BLUE,
            foreground_color=Colors.WHITE,
            data=0,
            on_click=self.on_fab_pressed,
        )

        self.controls = [self.dlg_delete_confirm,
                         self.dlg_rename_cate]
        self.page.drawer = self.drawer
        self.page.end_drawer = self.end_drawer
        self.page.run_task(self.build_interface)

    async def query_tasks_by_list(self, list_name, task_status=False):
        token = await self.page.client_storage.get_async('token')
        str_today = datetime.now().strftime('%Y-%m-%d')
        result_field = 'result'
        url = f'https://restapi.10qu.com.cn/todo_search/?task_time={str_today}'
        if list_name == 'today':
            # lst_ret = APIRequest.query_tasks_by_date(token, str_today, task_status)
            result_field = 'results'
            if not task_status:
                url = f'https://restapi.10qu.com.cn/todo_search/?task_time={str_today}&task_status={task_status}'
            else:
                url = f'https://restapi.10qu.com.cn/todo_search/?task_time={str_today}'
        elif list_name == 'future':
            result_field = 'result'
            # lst_ret = APIRequest.query_future_tasks(token)
            url = 'https://restapi.10qu.com.cn/todo_type_profile/'
        elif list_name == 'expired':
            result_field = 'result'
            # lst_ret = APIRequest.query_expired_tasks(token)
            url = 'https://restapi.10qu.com.cn/todo_type_profile/?flag=expired'
        elif isinstance(list_name, int):
            # lst_ret = APIRequest.query_tasks_by_cate_id(token, list_name, task_status)
            result_field = 'result'
            if not task_status:
                url = f'https://restapi.10qu.com.cn/user_todo/?todo_from_id={list_name}&task_status={task_status}'
            else:
                url = f'https://restapi.10qu.com.cn/user_todo/?todo_from_id={list_name}'

        # if self.container_empty in self.col_tasklist.controls:
        #     self.col_tasklist.controls.remove(self.container_empty)
        # self.col_task.controls.clear()

        headers = {'Authorization': f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("获取任务清单失败."))
                    self.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    self.page.update()
                    return {}
                else:
                    data = resp.json()
                    lst_ret = data.get(result_field)
                    if len(lst_ret) == 0:
                        return None
                    self.lv_task.controls.clear()
                    for itm in lst_ret:
                        if self.show_finished is False:
                            if itm.get('task_status') is True:
                                continue
                        task_item = Task(
                            self.page,
                            self,
                            token,
                            itm
                        )
                        # self.col_task.controls.append(task_item)
                        self.lv_task.controls.append(task_item)
                    # self.page.update()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"获取任务清单列表异常：{str(ex)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

    async def on_switch_show_finished(self, e):
        self.show_finished = e.control.value
        await self.query_tasks_by_list(self.list_name, task_status=True)
        self.update()

    def on_rename_list(self, e):
        self.tf_cate.value = self.list_title
        self.dlg_rename_cate.open = True
        self.page.update()

    def on_delete_list(self, e):
        self.dlg_delete_confirm.open = True
        self.page.update()

    async def on_dlg_delete_confirm_ok_click(self, e):
        token = await self.page.client_storage.get_async('token')
        # if APIRequest.delete_task_list(token, self.list_name):
        #     self.page.go('/dashboard')
        headers = {'Authorization': f'Bearer {token}'}
        url = f'https://restapi.10qu.com.cn/todo_from/{self.list_name}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.delete(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 204:
                    snack_bar = SnackBar(Text("清单删除失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务状态失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
        # 跳转至主界面
        self.page.controls.clear()
        from dashboard import DashboardControl
        page_view = SafeArea(
            DashboardControl(self.page),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_dlg_delete_confirm_cancel_click(self, e):
        self.dlg_delete_confirm.open = False
        self.page.update()

    async def on_dlg_rename_cate_ok_click(self, e):
        token = await self.page.client_storage.get_async('token')
        tasklist_name = self.tf_cate.value
        self.list_title = tasklist_name
        # if APIRequest.update_task_list(token, self.list_name, tasklist_name):
        #     self.dlg_rename_cate.open = False
        #     await self.update_list()
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'name': tasklist_name}
        url = f'https://restapi.10qu.com.cn/todo_from/{self.list_name}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("更新清单名称失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务象限失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
        self.dlg_rename_cate.open = False
        await self.update_list()

    def on_dlg_rename_cate_cancel_click(self, e):
        self.dlg_rename_cate.open = False
        self.page.update()

    def on_fab_pressed(self, e):
        async def on_input_task_submit(ex):
            input_task.value = ex.data
            task_name = input_task.value
            if len(task_name) == 0:
                snack_bar = SnackBar(Text("任务信息不允许为空!"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
                return
            token = await self.page.client_storage.get_async('token')
            # req_result = APIRequest.add_task(token,
            #                                  task_name,
            #                                  self.n_task_repeat,
            #                                  self.str_task_date,
            #                                  self.list_name,
            #                                  self.n_task_level)
            url = 'https://restapi.10qu.com.cn/todo/'
            headers = {'Authorization': f'Bearer {token}'}
            user_input = {'task_name': task_name,
                          'task_repeat': self.n_task_repeat,
                          'task_time': self.str_task_date,
                          'todo_from': self.list_name,
                          'type': self.n_task_level}
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.post(
                        url,
                        headers=headers,
                        json=user_input,
                    )
                    resp.raise_for_status()
                    if resp.status_code != 201:
                        snack_bar = SnackBar(Text("添加任务失败!"))
                        e.control.page.overlay.append(snack_bar)
                        snack_bar.open = True
                        e.control.page.update()
                        return
                    snack_bar = SnackBar(Text("任务添加成功!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.update()
                    e.control.page.update()
                    e.control.focus()

                    # 关闭BottomSheet
                    bs.open = False
                    ex.page.overlay.clear()
                    ex.control.update()
                    ex.control.page.update()

                    # 更新列表
                    await self.update_list()
            except httpx.HTTPError as ex:
                snack_bar = SnackBar(Text(f"任务添加异常：{str(ex)}"))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

        async def on_btn_add_clicked(ex):
            str_task_name = input_task.value
            # 提交任务
            if len(str_task_name) == 0:
                snack_bar = SnackBar(Text("任务信息不允许为空!"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
                return
            token = await self.page.client_storage.get_async('token')
            # req_result = APIRequest.add_task(token,
            #                                  str_task_name,
            #                                  self.n_task_repeat,
            #                                  self.str_task_date,
            #                                  self.list_name,
            #                                  self.n_task_level)
            url = 'https://restapi.10qu.com.cn/todo/'
            headers = {'Authorization': f'Bearer {token}'}
            user_input = {'task_name': str_task_name,
                          'task_repeat': self.n_task_repeat,
                          'task_time': self.str_task_date,
                          'todo_from': self.list_name,
                          'type': self.n_task_level}
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.post(
                        url,
                        headers=headers,
                        json=user_input,
                    )
                    resp.raise_for_status()
                    if resp.status_code != 201:
                        snack_bar = SnackBar(Text("添加任务失败!"))
                        e.control.page.overlay.append(snack_bar)
                        snack_bar.open = True
                        e.control.page.update()
                        return
                    snack_bar = SnackBar(Text("任务添加成功!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.update()
                    e.control.page.update()
                    # e.control.focus()
                    # 关闭BottomSheet
                    bs.open = False
                    ex.page.overlay.clear()
                    ex.control.update()
                    ex.control.page.update()
                    # 更新列表
                    await self.update_list()
            except httpx.HTTPError as ex:
                snack_bar = SnackBar(Text(f"任务添加异常：{str(ex)}"))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

        def on_select_task_date_by_picker(ex):
            task_date_picker.open = True
            ex.page.overlay.append(task_date_picker)
            # ex.control.page.open(task_date_picker)
            ex.control.update()
            ex.control.page.update()

        # 选择某个日期
        def on_select_task_date(ex):
            select_id = ex.data
            select_text = ''
            for item in ex.control.items:
                if select_id == item.uid:
                    select_text = item.text
                    break
            btn_due_date.content.controls[1].value = select_text
            btn_due_date.content.controls[1].color = Colors.RED
            ex.control.update()
            ex.control.page.update()
            today = datetime.today()
            match select_text:
                case '今天':
                    self.str_task_date = today.strftime('%Y-%m-%d')
                case '明天':
                    self.str_task_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
                case '下周一':
                    days_until_monday = (0 - today.weekday()) % 7
                    next_monday = today + timedelta(days=days_until_monday)
                    self.str_task_date = next_monday.strftime('%Y-%m-%d')

        def on_select_task_level(ex):
            select_id = ex.data
            select_text = ''
            for item in ex.control.items:
                if select_id == item.uid:
                    select_text = item.text
                    break
            btn_level.content.controls[1].value = select_text
            btn_level.content.controls[1].color = Colors.RED
            ex.control.update()
            ex.control.page.update()
            lst_level = ('重要紧急', '重要不紧急', '不重要紧急', '不重要不紧急')
            self.n_task_level = lst_level.index(select_text)

        def on_select_task_repeat(ex):
            select_id = ex.data
            select_text = ''
            for item in ex.control.items:
                if select_id == item.uid:
                    select_text = item.text
                    break
            btn_repeat.content.controls[1].value = select_text
            btn_repeat.content.controls[1].color = Colors.RED
            lst_repeat = ('无', '每天', '每周工作日', '每周', '每月', '每年')
            self.n_task_repeat = lst_repeat.index(select_text)

        # 通过日期控件选择日期
        def on_change_date(ex):
            dt_selected_date = ex.control.value
            self.str_task_date = dt_selected_date.strftime('%Y-%m-%d')
            btn_due_date.content.controls[1].value = self.str_task_date
            btn_due_date.content.controls[1].color = Colors.RED
            ex.control.update()
            ex.control.page.update()

        input_task = TextField(
            hint_text='添加任务',
            prefix_icon=Icons.ADD,
            expand=True,
            filled=True,
            border=InputBorder.NONE,
            border_radius=5,
            height=40,
            bgcolor='#CEE8E8',
            autofocus=True,
            adaptive=True,
            on_submit=on_input_task_submit,
            # on_blur=on_input_task_blue,
        )
        btn_add = IconButton(
            icon=Icons.ARROW_UPWARD,
            on_click=on_btn_add_clicked
        )
        btn_due_date = PopupMenuButton(
            icon=Icons.CALENDAR_MONTH_OUTLINED,
            content=Row([Icon(name=Icons.CALENDAR_MONTH),
                        Text('截止日期')]),
            items=[PopupMenuItem(text='今天', icon=Icons.CALENDAR_TODAY_OUTLINED),
                  PopupMenuItem(text='明天', icon=Icons.CALENDAR_VIEW_DAY_OUTLINED),
                  PopupMenuItem(text='下周一', icon=Icons.CALENDAR_VIEW_WEEK_OUTLINED),
                  PopupMenuItem(text='选择日期',
                                icon=Icons.CALENDAR_MONTH_OUTLINED,
                                on_click=on_select_task_date_by_picker,
                                )
                  ],
           on_select=on_select_task_date
        )
        btn_level = PopupMenuButton(icon=Icons.LABEL_IMPORTANT,
                                    content=Row([Icon(name=Icons.LABEL_IMPORTANT),
                                                 Text('重要程度')]),
                                    items=[PopupMenuItem(text='重要紧急', icon=Icons.LABEL_IMPORTANT_OUTLINED),
                                           PopupMenuItem(text='重要不紧急', icon=Icons.LABEL_IMPORTANT_OUTLINE),
                                           PopupMenuItem(text='不重要紧急', icon=Icons.WARNING),
                                           PopupMenuItem(text='不重要不紧急', icon=Icons.GPP_MAYBE_OUTLINED)],
                                    on_select=on_select_task_level
                                    )
        btn_repeat = PopupMenuButton(icon=Icons.REPEAT,
                                     content=Row([Icon(name=Icons.REPEAT),
                                                  Text('重复')]),
                                     items=[PopupMenuItem(text='无', icon=Icons.NOTIFICATIONS_NONE_OUTLINED),
                                            PopupMenuItem(text='每天', icon=Icons.EVENT_REPEAT),
                                            PopupMenuItem(text='每周工作日', icon=Icons.CALENDAR_VIEW_WEEK_OUTLINED),
                                            PopupMenuItem(text='每周', icon=Icons.WEEKEND_OUTLINED),
                                            PopupMenuItem(text='每月', icon=Icons.CALENDAR_MONTH),
                                            PopupMenuItem(text='每年', icon=Icons.REPEAT_OUTLINED)],
                                     on_select=on_select_task_repeat
                                     )
        row_input = Row(
            controls=[input_task, btn_add],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )
        row_ex = Row(
            controls=[btn_due_date, btn_level, btn_repeat],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )
        bs = BottomSheet(
            Container(
                Column(
                    [
                        row_input, row_ex
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    tight=True,
                ),
                adaptive=True,
                border_radius=2,
                padding=15,
            ),
            use_safe_area=True,
            open=True,
        )
        e.page.overlay.append(bs)
        e.control.update()
        e.control.page.update()

        task_date_picker = DatePicker(
            # first_date=datetime(2023, 10, 1),
            # last_date=datetime(2024, 12, 1),
            value=datetime.today().date(),
            open=True,
            on_change=on_change_date,
        )

    async def update_list(self):
        # task_list_controls = self.build_interface()
        # self.pagelet.content = Container(task_list_controls, padding=padding.all(0))
        await self.build_interface()

        self.drawer.controls = [
            Container(
                content=NavControl(self.page),
                expand=1,
            )
        ]
        self.page.update()

    async def build_interface(self):
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        self.page.overlay.append(progress_ring)
        self.page.update()

        self.list_title = await self.page.client_storage.get_async('list_title')
        self.show_finished = await self.page.client_storage.get_async('list_show_finished')

        dct_title = {"today": "今天",
                     "future": "未来七天",
                     "expired": "已过期",
                     "all": "全部",
                     self.list_name: self.list_title}

        self.col_task = Column(
            alignment=MainAxisAlignment.START,
            # expand=True,
            spacing=15,
            height=620,
            scroll=ScrollMode.HIDDEN
        )
        self.lv_task = ListView(
            expand=True,
            spacing=5,
            padding=5,
            adaptive=True,
        )
        # 定义了一个任务项为空的组件。
        # col_empty = Column([Icon(name=Icons.LIST_SHARP,
        #                          color=Colors.BLACK12,
        #                          size=128,
        #                          # expand=True,
        #                          ),
        #                     Text('没有可完成的任务，加油！',
        #                          size=24,
        #                          text_align=TextAlign.CENTER,
        #                          # expand=True,
        #                          )],
        #                    alignment=MainAxisAlignment.CENTER,
        #                    horizontal_alignment=CrossAxisAlignment.CENTER,
        #                    expand=True,
        #                    # height=500,
        #                    )
        # self.container_empty = Container(content=col_empty,
        #                                  # expand=True,
        #                                  # height=500,
        #                                  alignment=alignment.center,
        #                                  )

        # task_list_menu_btn = PopupMenuButton(
        #     items=[
        #         PopupMenuItem(icon=Icons.EDIT, text='重命名列表',
        #                       on_click=self.on_rename_list),
        #         PopupMenuItem(icon=Icons.DELETE, text='删除列表',
        #                       on_click=self.on_delete_list)
        #     ]
        # )
        # task_list_menu_btn.visible = self.list_name not in ['today', 'future', 'expired', 'all']

        self.col_tasklist = Column(
            controls = [
                Container(content=Row(
                    controls = [
                        Container(content=Text(dct_title.get(self.list_name), size=24, weight=FontWeight.BOLD)),
                        Switch(label='显示已完成',
                            value=False,
                            on_change=self.on_switch_show_finished,
                            expand=True,
                            adaptive=True,
                            )],
                        alignment=MainAxisAlignment.START,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                        spacing=5,
                        expand=1),
                ),
                # self.container_empty,
                self.lv_task,
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            adaptive=True
        )
        await self.query_tasks_by_list(self.list_name)
        # return self.col_tasklist
        self.controls.append(self.col_tasklist)
        progress_ring.visible = False
        self.page.update()
