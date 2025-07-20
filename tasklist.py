from datetime import datetime
from flet import Text, Container, Column, Icon, Row, TextField, \
    Icons, alignment, Colors, padding, \
    Switch, SnackBar, ListView
from flet.core import border
from flet.core.app_bar import AppBar
from flet.core.form_field_control import InputBorder
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.pagelet import Pagelet
from flet.core.types import MainAxisAlignment, ScrollMode, TextAlign, CrossAxisAlignment, FontWeight

import nav
from task import Task
from api_request import APIRequest
from task_detail import TaskDetail


class TaskListControl(Row):
    def __init__(self, page, list_id):
        super().__init__()
        self.page = page
        self.list_name = list_id
        self.list_title = self.page.client_storage.get('list_title')
        self.show_finished = self.page.client_storage.get('list_show_finished')

        # 左侧drawer
        token = self.page.client_storage.get('token')
        self.drawer = NavigationDrawer(
            position=NavigationDrawerPosition.START,
            controls=[Container(content=nav.NavControl(page, token),
                                expand=1,
                                padding=padding.only(right=10, top=10, bottom=10),
                                # margin=margin.only(right=10, bottom=10),
                                bgcolor=Colors.WHITE,
                                )]
        )

        # 右侧drawer
        detail_info = TaskDetail(self.page, {})
        self.end_drawer = NavigationDrawer(
            position=NavigationDrawerPosition.END,
            controls=[Container(content=detail_info,
                               width=300,
                               # bgcolor=colors.WHITE,
                               bgcolor='#f2f4f8',
                               border=border.all(1, Colors.BLACK12),
                               # on_hover=self.on_detail_hover,
                               )]
        )

        task_list_controls = self.build()
        pagelet = Pagelet(
            appbar=AppBar(
                title=Text(self.list_title),
                bgcolor=Colors.BLUE,
                center_title=True,
            ),
            content=Container(task_list_controls, padding=padding.all(0)),
            bgcolor=Colors.WHITE24,
            drawer=self.drawer,
            end_drawer=self.end_drawer,
            width=self.page.width,
            height=self.page.height
        )

        self.controls = [pagelet]
        self.page.drawer = self.drawer
        self.page.end_drawer = self.end_drawer

    def query_tasks_by_list(self, list_name):
        lst_ret = []
        token = self.page.client_storage.get('token')
        str_today = datetime.now().strftime('%Y-%m-%d')
        headers = {'Authorization': f'Bearer {token}'}
        if list_name == 'today':
            lst_ret = APIRequest.query_tasks_by_date(token, str_today)
        elif list_name == 'future':
            lst_ret = APIRequest.query_future_tasks(token)
        elif list_name == 'expired':
            lst_ret = APIRequest.query_expired_tasks(token)
        elif isinstance(list_name, int):
            lst_ret = APIRequest.query_tasks_by_cate_id(token, list_name)
        if len(lst_ret) == 0:
            return
        if self.container_empty in self.col_tasklist.controls:
            self.col_tasklist.controls.remove(self.container_empty)
        # self.col_task.controls.clear()
        self.lv_task.controls.clear()
        for itm in lst_ret:
            if self.show_finished is False:
                if itm.get('task_status') is True:
                    continue
            task_item = Task(self.page,
                             self,
                             token,
                             itm)
            # self.col_task.controls.append(task_item)
            self.lv_task.controls.append(task_item)
        # self.page.update()

    def on_switch_show_finished(self, e):
        self.show_finished = e.control.value
        self.query_tasks_by_list(self.list_name)
        self.update()

    def on_input_task_submit(self, e):
        task_name = self.input_task.value
        str_today = datetime.today().strftime('%Y-%m-%d')
        if len(task_name) == 0:
            self.page.snack_bar = SnackBar(Text("任务信息不允许为空!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        token = self.page.client_storage.get('token')
        req_result = APIRequest.add_task(token,
                                         task_name,
                                         0,
                                         str_today,
                                         self.list_name,
                                         3)
        if req_result is False:
            self.page.snack_bar = SnackBar(Text("添加任务失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.query_tasks_by_list(self.list_name)
        self.input_task.value = ''
        self.update()

        nav_control = self.page.controls[0].content.controls[0].content
        nav_control.update_todolist()
        nav_control.col_nav.update()
        nav_control.update()
        self.input_task.focus()

    def build(self):
        dct_title = {"today": "今天",
                     "future": "未来七天",
                     "expired": "已过期",
                     "all": "全部",
                     self.list_name: self.list_title}

        self.input_task = TextField(hint_text='添加任务',
                                    prefix_icon=Icons.ADD,
                                    expand=True,
                                    filled=True,
                                    border=InputBorder.NONE,
                                    border_radius=10,
                                    height=50,
                                    bgcolor='#CEE8E8',
                                    on_submit=self.on_input_task_submit)
        self.col_task = Column(alignment=MainAxisAlignment.START,
                               # expand=True,
                               spacing=15,
                               height=620,
                               scroll=ScrollMode.HIDDEN)
        self.lv_task = ListView(expand=True,
                                spacing=10,
                                padding=10,
                                # auto_scroll=True,
                                )
        col_empty = Column([Icon(name=Icons.LIST_SHARP,
                                 color=Colors.BLACK12,
                                 size=128,
                                 # expand=True,
                                 ),
                            Text('没有可完成的任务，加油！',
                                 size=24,
                                 text_align=TextAlign.CENTER,
                                 # expand=True,
                                 )],
                           alignment=MainAxisAlignment.CENTER,
                           horizontal_alignment=CrossAxisAlignment.CENTER,
                           expand=True,
                           # height=500,
                           )
        self.container_empty = Container(content=col_empty,
                                         # expand=True,
                                         # height=500,
                                         alignment=alignment.center,
                                         )

        self.col_tasklist = Column(
            [
                Container(content=Row(
                    [Container(content=Icon(name=Icons.LIST, color=Colors.BLACK38)),
                             Container(content=Text(dct_title.get(self.list_name), size=24, weight=FontWeight.BOLD)),
                             Container(content=Switch(label='显示已完成',
                                value=False,
                                on_change=self.on_switch_show_finished),
                                expand=True, alignment=alignment.center_right)],
                            alignment=MainAxisAlignment.START,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                            # vertical_alignment='start',
                            spacing=15,
                            # height=50,
                            expand=1),
                    height=80,
                    padding=padding.only(top=20, bottom=20)),
                self.container_empty,
                Container(content=self.lv_task,
                          expand=True,
                          # height=650,
                          padding=padding.only(bottom=15,)
                          ),
                Container(content=Row([self.input_task, ],
                                      alignment=MainAxisAlignment.END,
                                      # vertical_alignment='end',
                                      ),
                          alignment=alignment.top_left,
                          height=70,
                          # margin=margin.only(bottom=20,),
                          padding=padding.only(bottom=20),
                          # expand=1,
                          ),
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            # scroll='hidden',
            # height=800,
            # alignment='start',
            # horizontal_alignment='start',
        )
        self.query_tasks_by_list(self.list_name)
        return self.col_tasklist
