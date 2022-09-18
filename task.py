from flet import Text, Container, Column, Icon, Row, TextButton, TextField, Image, \
    icons, alignment, colors, border, margin, border_radius, padding, \
    UserControl, ListTile, Switch, VerticalDivider, Checkbox, AnimatedSwitcher
from api_request import APIRequest

class Task(UserControl):
    def __init__(self, task_control, token, task_name, task_id, task_time, finished):
        super().__init__()
        self.task_control = task_control
        self.token = token
        self.task_name = task_name
        self.task_id = task_id
        self.task_time = task_time
        self.finished = finished

    def on_checkbox_change(self, e):
        if self.cb_task.value is True:
            ret_result = APIRequest.update_task_status(self.token, self.task_id)
            if ret_result is True:
                self.update()
                self.task_control.query_tasks_by_list(self.task_control.list_name)
                self.task_control.update()


    def build(self):
        self.cb_task = Checkbox(value=self.finished, on_change=self.on_checkbox_change)
        row_task = Row(controls=[VerticalDivider(width=8, thickness=3, color='blue'),
                                 self.cb_task,
                                 Column(controls=[Text(self.task_name, size=16, italic=self.finished),
                                                  Text(self.task_time, size=12)])
                                 ],
                       alignment='start',
                       )
        container_task = Container(content=row_task,
                                   bgcolor=colors.WHITE,
                                   border_radius=border_radius.all(5),
                                   # margin=margin.all(10),
                                   padding=padding.all(5),
                                   )
        return container_task
