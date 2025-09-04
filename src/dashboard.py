from datetime import date

import httpx
from flet import Column, Icon, Row, \
    Icons, Colors, padding, Card
from flet.core.app_bar import AppBar
from flet.core.container import Container
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.progress_ring import ProgressRing
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.types import FontWeight, MainAxisAlignment, CrossAxisAlignment
from nav import NavControl

class DashboardControl(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.adaptive = True
        self.alignment = MainAxisAlignment.START

        self.page.drawer = NavigationDrawer(
            position=NavigationDrawerPosition.START,
            controls=[Container(
                content=NavControl(page),
                expand=1,
                padding=0,
                margin=0,
                )]
        )

        self.page.appbar = AppBar(
            title=Text('布尔清单', color=Colors.WHITE),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            actions=[],
        )
        # count_cards = self.build_interface()
        # self.controls = [count_cards]
        self.page.run_task(self.build_interface)

    async def query_summary_info(self):
        dct_info = {}
        token = await self.page.client_storage.get_async('token')
        # dct_ret = APIRequest.query_user_info(token)
        url = 'https://restapi.10qu.com.cn/user_info/'
        headers = {'Authorization': f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("获取用户信息失败."))
                    self.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    self.page.update()
                    return {}
                else:
                    data = resp.json()
                    user_info = data.get('results')
                    dct_info['avatar_url'] = user_info.get('avatar_url', 'assets/default_avatar.png')
                    dct_info['nickname'] = user_info.get('nick_name', '用户名')

                    # dct_ret = APIRequest.query_todolist(token)
                    url = 'https://restapi.10qu.com.cn/todo_profile/?show_expired=1'
                    resp_todo = await client.get(
                        url,
                        headers=headers,
                    )
                    resp_todo.raise_for_status()
                    if resp_todo.status_code != 200:
                        snack_bar = SnackBar(Text("获取清单失败."))
                        self.page.overlay.append(snack_bar)
                        snack_bar.open = True
                        self.page.update()
                        return {}
                    else:
                        data = resp_todo.json()
                        dct_ret = data.get('result')
                        todo_data = dct_ret[0].get('todo_data')
                        dct_info['num_all'] = todo_data[0].get("count")
                        dct_info['num_today'] = todo_data[1].get("count")
                        dct_info['num_7days'] = todo_data[3].get("count")
                        dct_info['num_expired'] = todo_data[2].get("count")
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"获取用户统计信息异常：{str(ex)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
        return dct_info

    async def nav_to_list(self, selected_nav, e):
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        e.control.page.overlay.append(progress_ring)
        e.control.page.update()

        list_name = selected_nav
        if selected_nav == 'today':
            list_title = '今天'
        elif selected_nav == 'all':
            list_title = '所有'
        elif selected_nav == 'future':
            list_title = '未来七天'
        elif selected_nav == 'expired':
            list_title = '已过期'
        else:
            list_title = '未知'

        await self.page.client_storage.set_async('list_name', list_name)
        await self.page.client_storage.set_async('list_title', list_title)
        await self.page.client_storage.set_async('list_show_finished', False)

        # self.page.go(f'/tasklist?id={list_name}')
        self.page.controls.clear()
        from tasklist import TaskListControl
        page_view = SafeArea(
            TaskListControl(self.page, list_name),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        progress_ring.visible = False
        self.page.update()

    async def on_today_click(self, e):
        await self.nav_to_list('today', e)

    async def on_all_click(self, e):
        await self.nav_to_list('all', e)

    async def on_future_click(self, e):
        await self.nav_to_list('future', e)

    async def on_expired_click(self, e):
        await self.nav_to_list('expired', e)

    # def did_mount(self):
    #     self.page.drawer = self.drawer

    async def build_interface(self):
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        self.page.overlay.append(progress_ring)
        self.page.update()

        dct_info = await self.query_summary_info()

        card_all = Card(
            # width=200,
            height=120,
            expand=True,
            elevation=2,
            content=Container(
                bgcolor=Colors.BLUE_400,
                padding=padding.all(10),
                border_radius=5,
                expand=True,
                on_click=self.on_all_click,
                content=Column(
                    [
                        Text(
                        '全部待办',
                             weight=FontWeight.BOLD,
                             size=16,
                             color=Colors.WHITE54
                        ),
                        Row(
                        [
                            Text(
                            f'{dct_info.get("num_all")}',
                                  color=Colors.WHITE,
                                  size=24
                            ),
                            Icon(Icons.ALL_INBOX, color='white')
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN)
                    ]
                ),
            ),
        )

        card_today = Card(content=Container(
            content=Column([Text('今天', weight=FontWeight.BOLD, size=16, color=Colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_today")}', color=Colors.WHITE, size=24),
                                 Icon(Icons.TODAY, color='white')], alignment=MainAxisAlignment.SPACE_BETWEEN)
                            ]),
            bgcolor=Colors.ORANGE_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_today_click,
        ),
            # width=200,
            height=120,
            expand=True,
            elevation=2,
        )

        card_future = Card(content=Container(
            content=Column([Text('未来七天', weight=FontWeight.BOLD, size=16, color=Colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_7days")}', color=Colors.WHITE, size=24),
                                 Icon(Icons.WEEKEND_ROUNDED, color='white')], alignment=MainAxisAlignment.SPACE_BETWEEN)
                            ]),
            bgcolor=Colors.RED_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_future_click,
        ),
            # width=200,
            height=120,
            expand=True,
            elevation=2,
        )

        card_expired = Card(content=Container(
            content=Column([Text('已过期', weight=FontWeight.BOLD, size=16, color=Colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_expired")}', color=Colors.WHITE, size=24),
                                 Icon(Icons.ACCOUNT_BOX, color='white')], alignment=MainAxisAlignment.SPACE_BETWEEN)
                            ]),
            bgcolor=Colors.GREEN_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_expired_click,
        ),
            # width=200,
            height=120,
            expand=True,
            elevation=2,
        )
        row_stat_1 = Row([card_all, card_today],
                       # expand=True,
                       alignment=MainAxisAlignment.START)
        row_stat_2 = Row([card_future, card_expired],
                       # expand=True,
                       alignment=MainAxisAlignment.START)

        today = date.today()
        str_today = f'{today.year}年{today.month}月{today.day}日,{['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][today.weekday()]}'
        col_dash = Column(
            controls = [
                Text(f'欢迎您，{dct_info.get("nickname")}',
                                    weight=FontWeight.BOLD, size=20, ),
                Text(str_today, size=16),
                Text('以下是当前任务统计数据',
                                    weight=FontWeight.BOLD,
                                    size=16,
                                    color=Colors.BLACK38),
                               # Container(content=row_info, expand=True)]
                row_stat_1,
                row_stat_2
        ],
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.START,
            adaptive=True,
            width=self.page.width,
            # spacing=1,
        )
        # return col_dash
        self.controls = [col_dash]
        progress_ring.visible = False
        self.page.update()
