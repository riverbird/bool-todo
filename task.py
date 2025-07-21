from flet import Text, Container, Column, Row, \
    Colors, border_radius, padding, \
    Checkbox, Card, alignment, Alignment, Icon, Icons, border
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.page import Page
from flet.core.types import MainAxisAlignment

from api_request import APIRequest
from task_detail import TaskDetail


class Task(Row):
    def __init__(self, page:Page, task_control, token, task_info):
        super().__init__()
        self.page = page
        self.task_control = task_control
        self.token = token
        self.task_info = task_info
        task_control = self.build()
        self.controls = [task_control]

    def on_checkbox_change(self, e):
        if self.cb_task.value is True:
            ret_result = APIRequest.update_task_status(self.token, self.task_info.get('id'))
            if ret_result is True:
                self.update()
                self.task_control.query_tasks_by_list(self.task_control.list_name)
                self.task_control.update()

                nav_control = self.page.controls[0].content.controls[0].content
                nav_control.update_todolist()
                nav_control.col_nav.update()
                nav_control.update()

    def on_detail_hover(self, e):
        if e.data == "false":
            if len(self.page.controls[0].content.controls) == 3:
                detail_control = self.page.controls[0].content.controls[2]
                self.page.controls[0].content.controls.remove(detail_control)
                self.page.update()

    def on_task_item_click(self, e):
        # if len(self.page.controls[0].content.controls) == 3:
        #     detail_control = self.page.controls[0].content.controls[2]
        #     self.page.controls[0].content.controls.remove(detail_control)
        #     self.page.update()
        #     return
        # detail_info = TaskDetail(self)
        # ctn_detail = Container(content=detail_info,
        #                        width=300,
        #                        # bgcolor=colors.WHITE,
        #                        bgcolor='#f2f4f8',
        #                        border=border.all(1, Colors.BLACK12),
        #                        # on_hover=self.on_detail_hover,
        #                        )
        # self.page.controls[0].content.controls.append(ctn_detail)
        # self.page.update()

        # detail_info = TaskDetail(self.page, self.task_info)
        # self.end_drawer = NavigationDrawer(
        #     position=NavigationDrawerPosition.END,
        #     controls=[Container(content=detail_info,
        #                         width=300,
        #                         # bgcolor=colors.WHITE,
        #                         bgcolor='#f2f4f8',
        #                         border=border.all(1, Colors.BLACK12),
        #                         # on_hover=self.on_detail_hover,
        #                         )]
        # )
        # self.page.end_drawer = self.end_drawer

        # task_detail = self.page.end_drawer.controls[0].content
        # task_detail.set_title(self.task_info.get('task_name'))
        # task_detail.set_title('我不好')
        # task_detail.update()
        # 右侧drawer
        detail_info = TaskDetail(self.page, self.task_info)
        self.page.end_drawer.controls = [Container(content=detail_info,
                                width=300,
                                # bgcolor=colors.WHITE,
                                bgcolor='#f2f4f8',
                                border=border.all(1, Colors.BLACK12),
                                # on_hover=self.on_detail_hover,
                                )]
        self.page.end_drawer.open = True
        self.page.update()

    def build(self):
        self.tt_task_time = Text(self.task_info.get('task_time'), size=12)
        self.cb_task = Checkbox(value=self.task_info.get('task_status'), on_change=self.on_checkbox_change)
        line_colors = [Colors.RED_200, Colors.ORANGE_200, Colors.BLUE_200, Colors.GREEN_200]
        row_task = Row(controls=[
            Container(bgcolor=line_colors[self.task_info.get('type')],
                      width=3,
                      height=20,
                      padding=padding.only(left=20, top=3, right=10, bottom=3),
                      ),
            self.cb_task,
            Column(controls=[Text(self.task_info.get('task_name'),
                                  size=16,
                                  italic=self.task_info.get('task_status')),
                             Row([self.tt_task_time,
                                  Icon(name=Icons.REPEAT,
                                       size=12,
                                       color=Colors.BLACK54,
                                       visible=self.task_info.get('task_repeat') > 0),
                                  ]),
                             ]),
        ],
            alignment=MainAxisAlignment.START,
        )
        # container_task = Container(content=row_task,
        #                            # bgcolor=colors.WHITE,
        #                            border_radius=border_radius.all(5),
        #                            # margin=margin.all(10),
        #                            padding=padding.all(5),
        #                            on_click=self.on_task_item_click,
        #                            )
        container_task = Card(content=Container(content=row_task,
                                                # bgcolor=colors.WHITE,
                                                border_radius=border_radius.all(5),
                                                # margin=margin.all(10),
                                                padding=padding.all(5),
                                                on_click=self.on_task_item_click,
                                                ),
                              elevation=0.5,
                              )
        return container_task
