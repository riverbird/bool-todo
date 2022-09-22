from flet import Text, Container, Column, Icon, Row, TextField, \
    icons, alignment,  padding, \
    UserControl, Checkbox,  Card, \
    Dropdown, IconButton, dropdown, SnackBar
from api_request import APIRequest
from datetime import datetime, timedelta


class TaskDetail(UserControl):
    def __init__(self, task):
        super().__init__()
        self.task = task

    def on_close_click(self, e):
        if len(self.page.controls[0].controls) == 3:
            detail_control = self.page.controls[0].controls[2]
            self.page.controls[0].controls.remove(detail_control)
            self.page.update()

    def query_tasks_cate(self):
        ret_result = APIRequest.query_todolist(self.task.token)
        dct_result = {}
        todo_data = ret_result[1].get('todo_data')
        for itm in todo_data:
            dct_result[itm.get('from_id')] = itm.get('name')
        return dct_result

    def refresh(self):
        # 更新导航栏
        nav_control = self.page.controls[0].controls[0].content
        nav_control.update_todolist()
        nav_control.col_nav.update()
        nav_control.update()

        # 更新任务列表
        self.task.task_control.query_tasks_by_list(self.task.task_control.list_name)
        self.task.task_control.update()

    def on_task_date_change(self, e):
        # 计算日期
        new_date = self.task.task_info.get('task_time')
        selected_value = self.dpd_date.value
        if selected_value == '今天':
            new_date = datetime.today().strftime('%Y-%m-%d')
        elif selected_value == '明天':
            new_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif selected_value == '下周一':
            delta = 1 - datetime.today().isoweekday()
            if delta <= 0:
                delta += 7
            new_date = (datetime.today() + timedelta(delta)).strftime('%Y-%m-%d')
        # 调用更新任务日期接口
        update_status = APIRequest.update_task_time(self.task.token,
                                                    self.task.task_info.get('id'),
                                                    new_date)

        # 如果任务日期更新失败
        if update_status is False:
            self.page.snack_bar = SnackBar(Text("更新任务时间失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.refresh()

    def on_task_cate_change(self, e):
        selected_cate = self.dpd_cate.value
        new_cate = list(self.dct_cates.keys())[list(self.dct_cates.values()).index(selected_cate)]
        update_status = APIRequest.update_task_cate(self.task.token,
                                                    self.task.task_info.get('task_time'),
                                                    self.task.task_info.get('id'),
                                                    new_cate)
        if update_status is False:
            self.page.snack_bar = SnackBar(Text("更新任务目录失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.refresh()

    def on_task_repeat_change(self, e):
        selected_repeat = self.dpd_repeat.value
        lst_repeat = ['无', '每天', '每周工作日', '每周', '每月', '每年']
        idx = lst_repeat.index(selected_repeat)
        update_status = APIRequest.update_task_repeat(self.task.token,
                                                      self.task.task_info.get('id'),
                                                      self.task.task_info.get('task_time'),
                                                      idx)
        if update_status is False:
            self.page.snack_bar = SnackBar(Text("更新任务重复状态失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.refresh()

    def on_task_level_change(self, e):
        selected_level = self.dpd_level.value
        lst_level = ['重要紧急', '重要不紧急', '不重要紧急', '不重要不紧急']
        idx = lst_level.index(selected_level)
        update_status = APIRequest.update_task_level(self.task.token,
                                                     self.task.task_info.get('id'),
                                                     self.task.task_info.get('task_time'),
                                                     idx)
        if update_status is False:
            self.page.snack_bar = SnackBar(Text("更新任务象限失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.refresh()

    def on_task_name_change(self, e):
        update_status = APIRequest.update_task_name(self.task.token,
                                                    self.task.task_info.get('id'),
                                                    self.tf_task_name.value
                                                    )
        if update_status is False:
            self.page.snack_bar = SnackBar(Text("更新任务失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.refresh()

    def on_task_status_change(self, e):
        if self.cb_name.value is True:
            ret_result = APIRequest.update_task_status(self.task.token,
                                                       self.task.task_info.get('id'))
            if ret_result is True:
                self.update()
                self.refresh()
                if len(self.page.controls[0].controls) == 3:
                    detail_control = self.page.controls[0].controls[2]
                    self.page.controls[0].controls.remove(detail_control)
                    self.page.update()

    def on_task_desc_change(self, e):
        update_status = APIRequest.update_task_desc(self.task.token,
                                                    self.task.task_info.get('id'),
                                                    self.task.task_info.get('task_time'),
                                                    self.tf_comment.value)
        if update_status is False:
            self.page.snack_bar = SnackBar(Text("更新任务描述信息失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.refresh()

    def on_task_delete(self, e):
        update_status = APIRequest.delete_task(self.task.token,
                                               self.task.task_info.get('id'))
        if update_status is False:
            self.page.snack_bar = SnackBar(Text("删除失败!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.refresh()
        if len(self.page.controls[0].controls) == 3:
            detail_control = self.page.controls[0].controls[2]
            self.page.controls[0].controls.remove(detail_control)
            self.page.update()

    def build(self):
        self.cb_name = Checkbox(
            # label=self.task.task_info.get('task_name'),
            value=self.task.task_info.get('task_status'),
            on_change=self.on_task_status_change)
        self.tf_task_name = TextField(value=self.task.task_info.get('task_name'),
                                      expand=True,
                                      border_width=0,
                                      on_blur=self.on_task_name_change)
        self.dpd_cate = Dropdown(width=300,
                                 height=50,
                                 hint_text='清单',
                                 icon=icons.LIST,
                                 on_change=self.on_task_cate_change,
                                 )
        self.dct_cates = self.query_tasks_cate()
        lst_cates = self.dct_cates.values()
        for itm in lst_cates:
            self.dpd_cate.options.append(dropdown.Option(itm))
        cate_id = self.task.task_info.get('todo_from')
        self.dpd_cate.value = self.dct_cates.get(cate_id)

        self.dpd_date = Dropdown(width=300,
                                 height=50,
                                 hint_text='日期',
                                 icon=icons.DATE_RANGE,
                                 options=[dropdown.Option('今天'),
                                          dropdown.Option('明天'),
                                          dropdown.Option('下周一'),
                                          dropdown.Option(self.task.task_info.get('task_time')),
                                          ],
                                 on_change=self.on_task_date_change,
                                 )
        self.dpd_date.value = self.task.task_info.get('task_time')

        lst_repeat = ['无', '每天', '每周工作日', '每周', '每月', '每年']
        self.dpd_repeat = Dropdown(width=300,
                                   height=50,
                                   hint_text='重复',
                                   icon=icons.REPEAT,
                                   on_change=self.on_task_repeat_change,
                                   )
        for itm in lst_repeat:
            self.dpd_repeat.options.append(dropdown.Option(itm))
        self.dpd_repeat.value = lst_repeat[self.task.task_info.get('task_repeat')]

        lst_level = ['重要紧急', '重要不紧急', '不重要紧急', '不重要不紧急']
        self.dpd_level = Dropdown(width=300,
                                  height=50,
                                  hint_text='象限',
                                  icon=icons.PRIORITY_HIGH,
                                  on_change=self.on_task_level_change,
                                  )
        for itm in lst_level:
            self.dpd_level.options.append(dropdown.Option(itm))
        self.dpd_level.value = lst_level[self.task.task_info.get('type')]

        card_basic = Card(
            content=Container(
                content=Column(
                    [self.dpd_cate,
                     self.dpd_date,
                     self.dpd_repeat,
                     self.dpd_level,
                     ],
                ),
                # bgcolor='white',
                # expand=True,
                padding=padding.only(left=10, right=10, top=20, bottom=20),
            )
        )

        self.tf_comment = TextField(hint_text='添加备注',
                                    multiline=True,
                                    expand=True,
                                    value=self.task.task_info.get('task_desc'),
                                    on_blur=self.on_task_desc_change,
                                    # height=180,
                                    )
        card_comment = Card(
            content=Container(
                content=self.tf_comment,
                # expand=True,
                # bgcolor='white',
                # height=200,
                padding=padding.all(10),
            )
        )

        row_top = Row(
            [self.cb_name, self.tf_task_name],
        )
        card_top = Card(
            Container(content=row_top,
                      height=100,
                      # bgcolor='white',
                      alignment=alignment.center_left,
                      padding=padding.only(left=10, right=10),
                      )
        )

        # create_time = datetime.strptime(self.task.task_info.get('create_time'),
        #                                 "%Y-%m-%d %H:%M:%S")
        create_time = self.task.task_info.get('create_time').split('.')[0]
        row_bottom = Row(
            [Icon(name=icons.FORWARD,
                  # color=colors.BLACK38
                  ),
             Text(f"{create_time}  创建",
                  # color=colors.BLACK38
                  ),
             IconButton(icon=icons.DELETE,
                        # icon_color=colors.BLACK38,
                        on_click=self.on_task_delete),
             ],
        )

        col_detail = Column(
            [
                Container(content=IconButton(icon=icons.CLOSE,
                                             icon_size=24,
                                             # icon_color=colors.BLACK38,
                                             on_click=self.on_close_click),
                          alignment=alignment.top_right,
                          ),
                card_top,
                card_basic,
                card_comment,
                Container(content=row_bottom,
                          # bgcolor='white',
                          padding=padding.all(10),
                          alignment=alignment.bottom_left)

            ],
            # alignment='spaceBetween',
        )

        return col_detail
