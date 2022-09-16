from flet import Text, Container, Column, Icon, Row, TextButton, TextField, Image, \
    icons, alignment, colors, border, margin, border_radius, padding, \
    UserControl, ListTile, Switch, VerticalDivider, Checkbox


class Task(UserControl):
    def __init__(self, task_name, task_time, finished):
        super().__init__()
        self.task_name = task_name
        self.task_time = task_time
        self.finished = finished

    def build(self):
        row_task = Row(controls=[VerticalDivider(width=8, thickness=3),
                                 Checkbox(value=self.finished),
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
