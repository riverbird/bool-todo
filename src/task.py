# coding:utf-8
import httpx
from flet import Text, Container, Column, Row, Colors, border_radius, padding, \
    Checkbox, Card, Icon, Icons, border
from flet.core.page import Page
from flet.core.snack_bar import SnackBar
from flet.core.types import MainAxisAlignment
from task_detail import TaskDetail


class Task(Row):
    def __init__(self, page:Page, task_control, token, task_info):
        super().__init__()
        self.page = page
        self.task_control = task_control
        self.token = token
        self.task_info = task_info
        task_component = self.build_interface()
        self.controls = [task_component]

    async def on_checkbox_change(self, e):
        if e.control.value is False:
            return
        # ret_result = APIRequest.update_task_status(self.token, self.task_info.get('id'))
        # if ret_result is True:
        #     self.task_control.update_list()
        token = await self.page.client_storage.get_async('token')
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {'todo_id': self.task_info.get('id')}
        url = 'https://restapi.10qu.com.cn/update_todo_status/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input
                )
                resp.raise_for_status()
                if resp.status_code != 202:
                    snack_bar = SnackBar(Text("更新任务状态失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                await self.task_control.update_list()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新任务状态失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    def on_task_item_click(self, e):
        # 右侧drawer
        detail_info = TaskDetail(self.page, self.task_control, self.task_info)
        self.page.end_drawer.controls = [
            Container(
                content=detail_info,
                width=300,
                # bgcolor=colors.WHITE,
                bgcolor='#f2f4f8',
                border=border.all(1, Colors.BLACK12),
                # on_hover=self.on_detail_hover,
            )
        ]
        self.page.end_drawer.open = True
        self.page.update()

    def build_interface(self):
        self.tt_task_time = Text(self.task_info.get('task_time'),
                                 color=Colors.BLACK38,
                                 size=12)
        self.cb_task = Checkbox(value=self.task_info.get('task_status'),
                                on_change=self.on_checkbox_change)
        line_colors = [Colors.RED_200, Colors.ORANGE_200, Colors.BLUE_200, Colors.GREEN_200]
        row_task = Row(controls=[
            Container(
                bgcolor=line_colors[self.task_info.get('type')],
                width=3,
                height=20,
                padding=padding.only(left=20, top=3, right=10, bottom=3)),
            self.cb_task,
            Column(controls=[Text(self.task_info.get('task_name'),
                                  size=14,
                                  italic=self.task_info.get('task_status')),
                             Row(controls=[
                                 self.tt_task_time,
                                 Icon(name=Icons.REPEAT,
                                       size=12,
                                       color=Colors.BLACK54,
                                       visible=self.task_info.get('task_repeat') > 0),
                                 ]),
                             ]),
        ],
            alignment=MainAxisAlignment.START,
            spacing=2,
        )

        container_task = Card(
            content=Container(
                content=row_task,
                border_radius=border_radius.all(2),
                padding=padding.only(5, 2, 0, 2),
                on_click=self.on_task_item_click,
            ),
            elevation=0.5,
            expand=True
        )
        return container_task
