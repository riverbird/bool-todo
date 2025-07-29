from flet import Text, Container, Column, Icon, Row, TextField, \
    Icons, alignment,  padding, Checkbox,  Card, Page, \
    Dropdown, IconButton, dropdown, SnackBar
from flet.core.colors import Colors
from flet.core.cupertino_bottom_sheet import CupertinoBottomSheet
from flet.core.cupertino_colors import CupertinoColors
from flet.core.cupertino_date_picker import CupertinoDatePickerMode, CupertinoDatePicker
from flet.core.outlined_button import OutlinedButton
from flet.core.types import MainAxisAlignment

from api_request import APIRequest


class TaskDetail(Row):
    def __init__(self, page:Page, task_control, task_info):
        super().__init__()
        self.page = page
        self.task_control = task_control
        self.task_info = task_info
        detail_control = self.build_interface()
        self.controls = [detail_control]

    def on_close_click(self, e):
        self.page.end_drawer.open = False
        self.page.update()

    def query_tasks_cate(self):
        token = self.page.client_storage.get('token')
        ret_result = APIRequest.query_todolist(token)
        dct_result = {}
        todo_data = ret_result[1].get('todo_data')
        for itm in todo_data:
            dct_result[itm.get('from_id')] = itm.get('name')
        return dct_result

    def refresh(self):
        self.task_control.update_list()

    def on_task_date_change(self, e):
        # 计算日期
        # new_date = self.task_info.get('task_time')
        # selected_value = e.control.value
        # if selected_value == '今天':
        #     new_date = datetime.today().strftime('%Y-%m-%d')
        # elif selected_value == '明天':
        #     new_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        # elif selected_value == '下周一':
        #     delta = 1 - datetime.today().isoweekday()
        #     if delta <= 0:
        #         delta += 7
        #     new_date = (datetime.today() + timedelta(delta)).strftime('%Y-%m-%d')
        # 调用更新任务日期接口
        token = self.page.client_storage.get('token')
        sel_date = e.control.value.date()
        new_date = sel_date.strftime('%Y-%m-%d')
        update_status = APIRequest.update_task_time(token,
                                                    self.task_info.get('id'),
                                                    new_date)

        # 如果任务日期更新失败
        if update_status is False:
            snack_bar = SnackBar(Text("更新任务时间失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        # self.btn_sel_date.text = new_date
        btn_sel_date = self.controls[0].controls[2].content.content.controls[1]
        if btn_sel_date:
            btn_sel_date.text = new_date
            e.control.page.update()
        self.refresh()

    def on_task_cate_change(self, e):
        selected_cate = e.control.value
        new_cate = list(self.dct_cates.keys())[list(self.dct_cates.values()).index(selected_cate)]
        token = self.page.client_storage.get('token')
        update_status = APIRequest.update_task_cate(token,
                                                    self.task_info.get('task_time'),
                                                    self.task_info.get('id'),
                                                    new_cate)
        if update_status is False:
            snack_bar = SnackBar(Text("更新任务目录失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        self.refresh()

    def on_task_repeat_change(self, e):
        selected_repeat = e.control.value
        lst_repeat = ['无', '每天', '每周工作日', '每周', '每月', '每年']
        idx = lst_repeat.index(selected_repeat)
        token = self.page.client_storage.get('token')
        update_status = APIRequest.update_task_repeat(token,
                                                      self.task_info.get('id'),
                                                      self.task_info.get('task_time'),
                                                      idx)
        if update_status is False:
            snack_bar = SnackBar(Text("更新任务重复状态失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        self.refresh()

    def on_task_level_change(self, e):
        selected_level = e.control.value
        lst_level = ['重要紧急', '重要不紧急', '不重要紧急', '不重要不紧急']
        idx = lst_level.index(selected_level)
        token = self.page.client_storage.get('token')
        update_status = APIRequest.update_task_level(token,
                                                     self.task_info.get('id'),
                                                     self.task_info.get('task_time'),
                                                     idx)
        if update_status is False:
            snack_bar = SnackBar(Text("更新任务象限失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        self.refresh()

    def on_task_name_change(self, e):
        token = self.page.client_storage.get('token')
        update_status = APIRequest.update_task_name(token,
                                                    self.task_info.get('id'),
                                                    e.control.value)
        if update_status is False:
            snack_bar = SnackBar(Text("更新任务失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        self.refresh()

    def on_task_status_change(self, e):
        if e.control.value is True:
            token = self.page.client_storage.get('token')
            ret_result = APIRequest.update_task_status(token,
                                                       self.task_info.get('id'))
            if ret_result is True:
                self.refresh()

    def on_task_desc_change(self, e):
        comment_str = e.control.value
        token = self.page.client_storage.get('token')
        update_status = APIRequest.update_task_desc(token,
                                                    self.task_info.get('id'),
                                                    self.task_info.get('task_time'),
                                                    comment_str)
        if update_status is False:
            snack_bar = SnackBar(Text("更新任务描述信息失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        self.refresh()

    def on_task_delete(self, e):
        token = self.page.client_storage.get('token')
        update_status = APIRequest.delete_task(token,
                                               self.task_info.get('id'))
        if update_status is False:
            snack_bar = SnackBar(Text("删除失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        self.page.end_drawer.open = False
        self.refresh()
        # if len(self.page.controls[0].controls) == 3:
        #     detail_control = self.page.controls[0].controls[2]
        #     self.page.controls[0].controls.remove(detail_control)
        #     self.page.update()

    def build_interface(self):
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
        self.dct_cates = self.query_tasks_cate()
        lst_cates = self.dct_cates.values()
        for itm in lst_cates:
            self.dpd_cate.options.append(dropdown.Option(itm))
        self.dct_cates[-1] = '--'
        self.dpd_cate.options.append(dropdown.Option('--'))
        cate_id = self.task_info.get('todo_from', -1)
        self.dpd_cate.value = self.dct_cates.get(cate_id)

        # 任务日期
        self.btn_sel_date = OutlinedButton(
            text=self.task_info.get('task_time', '--'),
            width=280,
            on_click=lambda e: e.control.page.open(
               CupertinoBottomSheet(
                   CupertinoDatePicker(
                       on_change=self.on_task_date_change,
                       date_picker_mode=CupertinoDatePickerMode.DATE),
                   height=216,
                   bgcolor=CupertinoColors.SYSTEM_BACKGROUND,
                   padding=padding.only(top=6))
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
            # padding=padding.only(left=10),
            # expand=True,
            # icon=Icons.PRIORITY_HIGH,
            on_change=self.on_task_level_change)
        for itm in lst_level:
            self.dpd_level.options.append(dropdown.Option(itm))
        self.dpd_level.value = lst_level[self.task_info.get('type', 0)]

        self.tf_comment = TextField(hint_text='添加备注',
                                    multiline=True,
                                    width=280,
                                    # expand=True,
                                    border_width=1,
                                    border_radius=2,
                                    value=self.task_info.get('task_desc', ''),
                                    on_blur=self.on_task_desc_change)

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
                Icon(name=Icons.FORWARD,
                  # color=colors.BLACK38
                  ),
                Text(f"{create_time}  创建",
                  # color=colors.BLACK38,
                  expand=True,
                  ),
                IconButton(icon=Icons.DELETE,
                        # icon_color=colors.BLACK38,
                        on_click=self.on_task_delete),
                ],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )

        col_detail = Column(
            controls = [
                Container(
                    content=IconButton(
                        icon=Icons.CLOSE,
                        icon_size=24,
                        icon_color=Colors.BLUE_500,
                        on_click=self.on_close_click),
                    alignment=alignment.top_right,
                    # bgcolor=Colors.BLACK12
                ),
                row_top,
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
                    # margin=margin.only(10, 2, 2, 5)
                    padding=padding.only(left=10, right=0, top=2, bottom=2),
                ),
                Container(
                    adaptive=True,
                    content=row_bottom,
                    # bgcolor='white',
                    padding=padding.only(left=10),
                    alignment=alignment.bottom_left
                )
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            adaptive=True
        )

        return col_detail
