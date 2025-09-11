import json
from datetime import date, datetime

import httpx
from flet import Column, Icon, Row, \
    Icons, Colors, padding, Card
from flet.core.app_bar import AppBar
from flet.core.border import BorderSide
from flet.core.charts.bar_chart import BarChart, BarChartEvent
from flet.core.charts.bar_chart_group import BarChartGroup
from flet.core.charts.bar_chart_rod import BarChartRod
from flet.core.charts.chart_axis import ChartAxis
from flet.core.charts.chart_axis_label import ChartAxisLabel
from flet.core.charts.chart_grid_lines import ChartGridLines
from flet.core.container import Container
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.progress_ring import ProgressRing
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.types import FontWeight, MainAxisAlignment, CrossAxisAlignment
from nav import NavControl

class SampleRod(BarChartRod):
    def __init__(self, y: float, hovered: bool = False):
        super().__init__()
        self.hovered = hovered
        self.y = y
        # self.tooltip = f"{self.y}"
        self.width = 16
        self.color = Colors.WHITE
        self.bg_to_y = 6
        self.bg_color = Colors.GREEN_300

    def before_update(self):
        self.to_y = self.y + 0.5 if self.hovered else self.y
        self.color = Colors.YELLOW if self.hovered else Colors.WHITE
        self.border_side = (
            BorderSide(width=1, color=Colors.GREEN_400)
            if self.hovered
            else BorderSide(width=0, color=Colors.WHITE)
        )
        super().before_update()

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
        self.page.floating_action_button = None
        # count_cards = self.build_interface()
        # self.controls = [count_cards]
        self.page.run_task(self.build_interface)

    async def query_summary_info(self):
        dct_info = {}
        token = await self.page.client_storage.get_async('token')
        url = 'https://restapi.10qu.com.cn/user_info/'
        headers = {'Authorization': f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                # 查询用户信息
                cached_user_info_value = await self.page.client_storage.get_async('todo_user_info')
                cached_user_info = json.loads(cached_user_info_value) if cached_user_info_value else {}
                if cached_user_info:
                    dct_info = cached_user_info
                else:
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
                        return dct_info
                    data = resp.json()
                    user_info = data.get('results')
                    dct_info['avatar_url'] = user_info.get('avatar_url', 'assets/default_avatar.png')
                    dct_info['nickname'] = user_info.get('nick_name', '用户名')

                    # 查询待办清单
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
                        return dct_info
                    else:
                        data = resp_todo.json()
                        dct_ret = data.get('result')
                        todo_data = dct_ret[0].get('todo_data')
                        dct_info['num_all'] = todo_data[0].get("count")
                        dct_info['num_today'] = todo_data[1].get("count")
                        dct_info['num_7days'] = todo_data[3].get("count")
                        dct_info['num_expired'] = todo_data[2].get("count")

                        # 查询分析统计数据
                        url = 'https://restapi.10qu.com.cn/analysis_summary/'
                        resp_analysis = await client.get(
                            url,
                            headers=headers,
                        )
                        resp_analysis.raise_for_status()
                        if resp_analysis.status_code != 200:
                            snack_bar = SnackBar(Text("获取周统计数据失败."))
                            self.page.overlay.append(snack_bar)
                            snack_bar.open = True
                            self.page.update()
                            return dct_info
                        else:
                            data = resp_analysis.json()
                            dct_ret = data.get('result')
                            dct_info['analysis'] = dct_ret
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

    def build_chart(self, data_list):
        def on_chart_event(e: BarChartEvent):
            for group_index, group in enumerate(chart.bar_groups):
                for rod_index, rod in enumerate(group.bar_rods):
                    rod.hovered = e.group_index == group_index and e.rod_index == rod_index
            chart.update()

        bar_groups = []
        labels = []
        lst_count = []
        for idx, data in enumerate(data_list):
            bar_groups.append(
                BarChartGroup(
                    x = idx,
                    bar_rods= [SampleRod(data.get('task_count'))]
                )
            )
            str_time = data.get('task_time')
            dt_time = datetime.strptime(str_time, '%Y-%m-%d')
            str_day = f'{dt_time.day}号'
            labels.append(
                ChartAxisLabel(
                    value=idx,
                    label=Text(str_day)
                )
            )
            lst_count.append(data.get('task_count'))

        chart = BarChart(
            bar_groups=bar_groups,
            bottom_axis=ChartAxis(
                labels=labels
            ),
            on_chart_event=on_chart_event,
            interactive=True,
            # border=border.all(1, Colors.GREY_400),
            # left_axis=ChartAxis(
            #     labels_size=20, title=Text("近七日任务完成统计"), title_size=20
            # ),
            horizontal_grid_lines=ChartGridLines(
                color=Colors.WHITE30, width=1, dash_pattern=[3, 3]
            ),
            tooltip_bgcolor=Colors.with_opacity(0.5, Colors.GREY_300),
            max_y=max(lst_count)
        )
        return chart

    async def build_interface(self):
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        self.page.overlay.append(progress_ring)
        self.page.update()

        dct_info = await self.query_summary_info()

        card_all = Card(
            # width=200,
            height=100,
            expand=True,
            elevation=2,
            content=Container(
                bgcolor=Colors.PINK_400,
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
                            f'{dct_info.get("num_all", 0)}',
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
                            Row([Text(f'{dct_info.get("num_today", 0)}', color=Colors.WHITE, size=24),
                                 Icon(Icons.TODAY, color='white')], alignment=MainAxisAlignment.SPACE_BETWEEN)
                            ]),
            bgcolor=Colors.PURPLE_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_today_click,
        ),
            # width=200,
            height=100,
            expand=True,
            elevation=2,
        )

        card_future = Card(content=Container(
            content=Column([Text('未来七天', weight=FontWeight.BOLD, size=16, color=Colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_7days", 0)}', color=Colors.WHITE, size=24),
                                 Icon(Icons.WEEKEND_ROUNDED, color='white')], alignment=MainAxisAlignment.SPACE_BETWEEN)
                            ]),
            bgcolor=Colors.ORANGE_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_future_click,
        ),
            # width=200,
            height=100,
            expand=True,
            elevation=2,
        )

        card_expired = Card(content=Container(
            content=Column([Text('已过期', weight=FontWeight.BOLD, size=16, color=Colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_expired", 0)}', color=Colors.WHITE, size=24),
                                 Icon(Icons.ACCOUNT_BOX, color='white')], alignment=MainAxisAlignment.SPACE_BETWEEN)
                            ]),
            bgcolor=Colors.DEEP_ORANGE_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_expired_click,
        ),
            # width=200,
            height=100,
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
                # Text(
                #     '以下是当前任务统计数据',
                #      weight=FontWeight.BOLD,
                #      size=16,
                #      color=Colors.BLACK38
                # ),
                # Container(content=row_info, expand=True)]
                row_stat_1,
                row_stat_2,
            ],
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.START,
            adaptive=True,
            width=self.page.width,
            spacing=5,
            expand=True
        )
        if 'analysis' in dct_info:
            chart = self.build_chart(dct_info.get('analysis')[1].get('date_info'))
            chart_container = Container(
                chart, bgcolor=Colors.GREEN_200, padding=10, border_radius=5, expand=True
            )
            col_dash.controls.append(chart_container)
        # return col_dash
        self.controls = [col_dash]
        progress_ring.visible = False
        self.page.update()
