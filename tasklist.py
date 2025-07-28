from datetime import datetime, timedelta
from flet import Text, Container, Column, Icon, Row, TextField, \
    Icons, alignment, Colors, padding, \
    Switch, SnackBar, ListView
from flet.core import border, icon, date_picker
from flet.core.bottom_sheet import BottomSheet
from flet.core.cupertino_textfield import CupertinoTextField
from flet.core.date_picker import DatePicker
from flet.core.floating_action_button import FloatingActionButton
from flet.core.form_field_control import InputBorder
from flet.core.icon_button import IconButton
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.outlined_button import OutlinedButton
from flet.core.pagelet import Pagelet
from flet.core.popup_menu_button import PopupMenuButton, PopupMenuItem
from flet.core.safe_area import SafeArea
from flet.core.types import MainAxisAlignment, ScrollMode, TextAlign, CrossAxisAlignment, FontWeight, \
    FloatingActionButtonLocation

import nav
from task import Task
from api_request import APIRequest
from task_detail import TaskDetail


class TaskListControl(Column):
    def __init__(self, page, list_id):
        super().__init__()
        self.page = page
        self.adaptive = True
        self.alignment = MainAxisAlignment.START

        self.str_task_date = datetime.today().strftime('%Y-%m-%d')
        self.n_task_level = 0
        self.n_task_repeat = 0

        self.list_name = list_id
        self.list_title = self.page.client_storage.get('list_title')
        self.show_finished = self.page.client_storage.get('list_show_finished')

        # 左侧drawer
        self.drawer = NavigationDrawer(
            position=NavigationDrawerPosition.START,
            controls=[Container(content=nav.NavControl(page),
                                expand=1,
                                padding=padding.only(right=10, top=10, bottom=10),
                                # margin=margin.only(right=10, bottom=10),
                                bgcolor=Colors.WHITE,
                                )]
        )

        # 右侧drawer
        detail_info = TaskDetail(self.page, self, {})
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
        floating_btn = FloatingActionButton(
            icon=Icons.ADD,
            bgcolor=Colors.BLUE,
            foreground_color=Colors.WHITE,
            data=0,
            on_click=self.on_fab_pressed,
        )
        self.pagelet = Pagelet(
            # appbar=AppBar(
            #     title=Text(self.list_title),
            #     color=Colors.WHITE,
            #     bgcolor=Colors.BLUE,
            #     center_title=True,
            #     toolbar_height=40,
            # ),
            content=Container(task_list_controls, padding=padding.all(0)),
            drawer=self.drawer,
            end_drawer=self.end_drawer,
            floating_action_button=floating_btn,
            # floating_action_button_location=FloatingActionButtonLocation.END_CONTAINED,
            width=self.page.width,
            height=self.page.height
        )

        self.controls = [self.pagelet]
        self.page.drawer = self.drawer
        self.page.end_drawer = self.end_drawer

    def query_tasks_by_list(self, list_name):
        lst_ret = []
        token = self.page.client_storage.get('token')
        str_today = datetime.now().strftime('%Y-%m-%d')
        # headers = {'Authorization': f'Bearer {token}'}
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
        self.input_task.value = e.data
        task_name = self.input_task.value
        str_today = datetime.today().strftime('%Y-%m-%d')
        if len(task_name) == 0:
            snack_bar = SnackBar(Text("任务信息不允许为空!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        token = self.page.client_storage.get('token')
        req_result = APIRequest.add_task(token,
                                         task_name,
                                         0,
                                         str_today,
                                         self.list_name,
                                         3)
        if req_result is False:
            snack_bar = SnackBar(Text("添加任务失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        # self.query_tasks_by_list(self.list_name)
        # e.control.value = ''
        snack_bar = SnackBar(Text("任务添加成功!"))
        e.control.page.overlay.append(snack_bar)
        snack_bar.open = True
        e.control.update()
        e.control.page.update()
        e.control.focus()

        # 这种方法比较重，后面看看有没有局部更新的办法
        # task_list_controls = self.build()
        # pagelet = Pagelet(
        #     appbar=AppBar(
        #         title=Text(self.list_title),
        #         bgcolor=Colors.BLUE,
        #         center_title=True,
        #         toolbar_height=40,
        #     ),
        #     content=Container(task_list_controls, padding=padding.all(0)),
        #     bgcolor=Colors.WHITE24,
        #     drawer=self.drawer,
        #     end_drawer=self.end_drawer,
        #     width=self.page.width,
        #     height=self.page.height
        # )
        # self.controls.clear()
        # self.controls = [pagelet]

        # 这种方法相对轻量一点
        self.update_list()

        # nav_control = self.page.controls[0].content.controls[0].content
        # nav_control.update_todolist()
        # nav_control.col_nav.update()
        # nav_control.update()
        # self.input_task.focus()

    def on_menu_click(self, e):
        self.drawer.open = True
        e.control.page.update()

    def on_fab_pressed(self, e):
        def on_input_task_submit(ex):
            input_task.value = ex.data
            task_name = input_task.value
            if len(task_name) == 0:
                snack_bar = SnackBar(Text("任务信息不允许为空!"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
                return
            token = self.page.client_storage.get('token')
            req_result = APIRequest.add_task(token,
                                             task_name,
                                             self.n_task_repeat,
                                             self.str_task_date,
                                             self.list_name,
                                             self.n_task_level)
            if req_result is False:
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
            self.update_list()

        # def on_input_task_blue(ex):
        #     str_task_name = input_task.value

        def on_btn_add_clicked(ex):
            str_task_name = input_task.value
            # 提交任务
            if len(str_task_name) == 0:
                snack_bar = SnackBar(Text("任务信息不允许为空!"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
                return
            token = self.page.client_storage.get('token')
            req_result = APIRequest.add_task(token,
                                             str_task_name,
                                             self.n_task_repeat,
                                             self.str_task_date,
                                             self.list_name,
                                             self.n_task_level)
            if req_result is False:
                snack_bar = SnackBar(Text("添加任务失败!"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
                return
            # 关闭BottomSheet
            bs.open = False
            ex.page.overlay.clear()
            ex.control.update()
            ex.control.page.update()
            # 更新列表
            self.update_list()

        def on_select_task_date_by_picker(ex):
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
            dt_selected_date = ex.data
            self.str_task_date = dt_selected_date.strftime('%Y-%m-%d')
            btn_level.content.controls[1].value = self.str_task_date
            btn_level.content.controls[1].color = Colors.RED
            ex.control.update()
            ex.control.page.update()

        input_task = TextField(hint_text='添加任务',
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
        btn_add = IconButton(icon=Icons.ARROW_UPWARD,
                             on_click=on_btn_add_clicked)
        btn_due_date = PopupMenuButton(icon=Icons.CALENDAR_MONTH_OUTLINED,
                                       content=Row([Icon(name=Icons.CALENDAR_MONTH),
                                                    Text('截止日期')]),
                                       items=[PopupMenuItem(text='今天', icon=Icons.CALENDAR_TODAY),
                                              PopupMenuItem(text='明天', icon=Icons.CALENDAR_VIEW_DAY),
                                              PopupMenuItem(text='下周一', icon=Icons.CALENDAR_VIEW_WEEK),
                                              PopupMenuItem(text='选择日期',
                                                            icon=Icons.CALENDAR_MONTH,
                                                            on_click=on_select_task_date_by_picker,
                                                            )],
                                       on_select=on_select_task_date
                                       )
        btn_level = PopupMenuButton(icon=Icons.LABEL_IMPORTANT,
                                    content=Row([Icon(name=Icons.LABEL_IMPORTANT),
                                                 Text('重要程度')]),
                                    items=[PopupMenuItem(text='重要紧急', icon=Icons.LABEL_IMPORTANT_OUTLINED),
                                           PopupMenuItem(text='重要不紧急', icon=Icons.LABEL_IMPORTANT_OUTLINE),
                                           PopupMenuItem(text='不重要紧急', icon=Icons.WARNING),
                                           PopupMenuItem(text='不重要不紧急', icon=Icons.JOIN_FULL_OUTLINED)],
                                    on_select=on_select_task_level
                                    )
        btn_repeat = PopupMenuButton(icon=Icons.REPEAT,
                                     content=Row([Icon(name=Icons.REPEAT),
                                                  Text('重复')]),
                                     items=[PopupMenuItem(text='无', icon=Icons.REPEAT_OUTLINED),
                                            PopupMenuItem(text='每天', icon=Icons.EVENT_REPEAT),
                                            PopupMenuItem(text='每周工作日', icon=Icons.EVENT_REPEAT_OUTLINED),
                                            PopupMenuItem(text='每周', icon=Icons.EVENT_REPEAT_OUTLINED),
                                            PopupMenuItem(text='每月', icon=Icons.CALENDAR_MONTH),
                                            PopupMenuItem(text='每年', icon=Icons.YOUTUBE_SEARCHED_FOR)],
                                     on_select=on_select_task_repeat
                                     )
        row_input = Row(
            controls=[input_task, btn_add],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )
        row_ex = Row(
            controls=[btn_due_date, btn_level, btn_repeat],
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
        # e.page.open(bs)
        # page.add(
        #     ft.ElevatedButton("Display bottom sheet", on_click=lambda e: page.open(bs))
        # )
        task_date_picker = DatePicker(
            first_date=datetime(2023, 10, 1),
            last_date=datetime(2024, 12, 1),
            open=True,
            on_change=on_change_date,
        )

    def update_list(self):
        task_list_controls = self.build()
        self.pagelet.content = Container(task_list_controls, padding=padding.all(0))

        self.drawer.controls = [Container(content=nav.NavControl(self.page),
                                expand=1,
                                padding=padding.only(right=10, top=10, bottom=10),
                                # margin=margin.only(right=10, bottom=10),
                                bgcolor=Colors.WHITE,
                                )]
        self.page.update()

    def build(self):
        dct_title = {"today": "今天",
                     "future": "未来七天",
                     "expired": "已过期",
                     "all": "全部",
                     self.list_name: self.list_title}

        # self.input_task = TextField(hint_text='添加任务',
        #                             prefix_icon=Icons.ADD,
        #                             expand=True,
        #                             filled=True,
        #                             border=InputBorder.NONE,
        #                             border_radius=5,
        #                             height=40,
        #                             bgcolor='#CEE8E8',
        #                             autofocus=True,
        #                             adaptive=True,
        #                             on_submit=self.on_input_task_submit)

        self.col_task = Column(alignment=MainAxisAlignment.START,
                               # expand=True,
                               spacing=15,
                               height=620,
                               scroll=ScrollMode.HIDDEN)
        self.lv_task = ListView(expand=True,
                                spacing=5,
                                padding=5,
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
                IconButton(Icons.MENU, on_click=self.on_menu_click),
                Container(content=Row(
                    controls = [
                        Container(content=Text(dct_title.get(self.list_name), size=24, weight=FontWeight.BOLD)),
                        Switch(label='显示已完成',
                            value=False,
                            on_change=self.on_switch_show_finished,
                            expand=True,
                            adaptive=True,
                            # scale=0.9
                            )],
                        alignment=MainAxisAlignment.START,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                        # vertical_alignment='start',
                        spacing=5,
                        # height=50,
                        expand=1),
                    # height=80,
                    # padding=padding.only(top=2, bottom=2)
                ),
                # self.container_empty,
                self.lv_task,
                # Container(content=Row(controls=[self.input_task],
                #                       # alignment=MainAxisAlignment.END,
                #                       # vertical_alignment='end',
                #                       ),
                #           alignment=alignment.top_left,
                #           height=70,
                #           # margin=margin.only(bottom=20,),
                #           padding=padding.only(bottom=20),
                #           # expand=1,
                #           ),
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
