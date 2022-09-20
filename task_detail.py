from flet import Text, Container, Column, Icon, Row, TextButton, TextField, Image, \
    icons, alignment, colors, border, margin, border_radius, padding, \
    UserControl, ListTile, Switch, VerticalDivider, Checkbox, AnimatedSwitcher, Card, \
    Dropdown, IconButton, dropdown
from api_request import APIRequest
from datetime import datetime


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

    def build(self):
        cb_name = Checkbox(
                           # label=self.task.task_info.get('task_name'),
                           value=self.task.task_info.get('task_status'))
        tf_task_name = TextField(value=self.task.task_info.get('task_name'),
                                 expand=True,
                                 border_width=0,)
        dpd_cate = Dropdown(width=300,
                            height=50,
                            hint_text='清单',
                            icon=icons.LIST,
                            )
        dct_cates = self.query_tasks_cate()
        lst_cates = dct_cates.values()
        for itm in lst_cates:
            dpd_cate.options.append(dropdown.Option(itm))
        cate_id = self.task.task_info.get('todo_from')
        dpd_cate.value = dct_cates.get(cate_id)

        dpd_date = Dropdown(width=300,
                            height=50,
                            hint_text='日期',
                            icon=icons.DATE_RANGE,
                            options=[dropdown.Option('今天'),
                                     dropdown.Option('明天'),
                                     dropdown.Option('下周一'),
                                     dropdown.Option(self.task.task_info.get('task_time'))]
                            )
        dpd_date.value = self.task.task_info.get('task_time')

        lst_repeat = ['无', '每天', '每周工作日', '每周', '每月', '每年']
        dpd_repeat = Dropdown(width=300,
                              height=50,
                              hint_text='重复',
                              icon=icons.REPEAT,
                              )
        for itm in lst_repeat:
            dpd_repeat.options.append(dropdown.Option(itm))
        dpd_repeat.value = lst_repeat[self.task.task_info.get('task_repeat')]

        lst_level = ['重要紧急', '重要不紧急', '不重要紧急', '不重要不紧急']
        dpd_level = Dropdown(width=300,
                             height=50,
                             hint_text='象限',
                             icon=icons.LABEL_IMPORTANT,
                             )
        for itm in lst_level:
            dpd_level.options.append(dropdown.Option(itm))
        dpd_level.value = lst_level[self.task.task_info.get('type')]

        card_basic = Card(
            content=Container(
                content=Column(
                    [dpd_cate,
                     dpd_date,
                     dpd_repeat,
                     dpd_level,
                     ],
                ),
                bgcolor='white',
                # expand=True,
                padding=padding.only(left=10, right=10, top=20, bottom=20),
            )
        )

        card_comment = Card(
            content=Container(
                content=TextField(hint_text='添加备注',
                                  multiline=True,
                                  expand=True,
                                  value=self.task.task_info.get('task_desc'),
                                  # height=180,
                                  ),
                # expand=True,
                bgcolor='white',
                # height=200,
                padding=padding.all(10),
            )
        )

        row_top = Row(
            [cb_name, tf_task_name],
        )

        # create_time = datetime.strptime(self.task.task_info.get('create_time'),
        #                                 "%Y-%m-%d %H:%M:%S")
        create_time = self.task.task_info.get('create_time').split('.')[0]
        row_bottom = Row(
            [Icon(name=icons.FORWARD, color=colors.BLACK38),
             Text(f"{create_time}  创建", color=colors.BLACK38),
             IconButton(icon=icons.DELETE, icon_color=colors.BLACK38),
             ],
        )

        col_detail = Column(
            [
                Container(content=IconButton(icon=icons.CLOSE, icon_size=24, icon_color=colors.BLACK38,
                                             on_click=self.on_close_click),
                          alignment=alignment.top_right,
                          ),
                Container(content=row_top,
                          height=100,
                          bgcolor='white',
                          alignment=alignment.center_left,
                          padding=padding.only(left=10, right=10),
                          ),
                card_basic,
                card_comment,
                Container(content=row_bottom,
                          bgcolor='white',
                          padding=padding.all(10),
                          alignment=alignment.bottom_left)

            ],
            # alignment='spaceBetween',
        )

        return col_detail
