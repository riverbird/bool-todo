from flet import Text, Container, Column, Row, \
    colors, border_radius, padding, \
    UserControl, Checkbox, Card
from api_request import APIRequest
from task_detail import TaskDetail


class Task(UserControl):
    def __init__(self, task_control, token, task_info):
        super().__init__()
        self.task_control = task_control
        self.token = token
        self.task_info = task_info

    def on_checkbox_change(self, e):
        if self.cb_task.value is True:
            ret_result = APIRequest.update_task_status(self.token, self.task_info.get('id'))
            if ret_result is True:
                self.update()
                self.task_control.query_tasks_by_list(self.task_control.list_name)
                self.task_control.update()

                nav_control = self.page.controls[0].controls[0].content
                nav_control.update_todolist()
                nav_control.col_nav.update()
                nav_control.update()

    def on_detail_hover(self, e):
        if e.data == "false":
            if len(self.page.controls[0].controls) == 3:
                detail_control = self.page.controls[0].controls[2]
                self.page.controls[0].controls.remove(detail_control)
                self.page.update()

    def on_task_item_click(self, e):
        if len(self.page.controls[0].controls) == 3:
            detail_control = self.page.controls[0].controls[2]
            self.page.controls[0].controls.remove(detail_control)
            self.page.update()
            return
        detail_info = TaskDetail(self)
        ctn_detail = Container(content=detail_info,
                               width=300,
                               # on_hover=self.on_detail_hover,
                               )
        self.page.controls[0].controls.append(ctn_detail)
        self.page.update()

    def build(self):
        self.tt_task_time = Text(self.task_info.get('task_time'), size=12)
        self.cb_task = Checkbox(value=self.task_info.get('task_status'), on_change=self.on_checkbox_change)
        line_colors = [colors.RED_200, colors.ORANGE_200, colors.BLUE_200, colors.GREEN_200]
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
                             self.tt_task_time])
        ],
            alignment='start',
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
