from flet import Column, Icon, Row, \
    Icons, Colors, padding, Card
from flet.core.app_bar import AppBar
from flet.core.container import Container
from flet.core.icon_button import IconButton
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.pagelet import Pagelet
from flet.core.text import Text
from flet.core.types import FontWeight, MainAxisAlignment, CrossAxisAlignment

from api_request import APIRequest
from tasklist import TaskListControl
import nav


class DashboardControl(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page

        token = self.page.client_storage.get('token')
        self.drawer = NavigationDrawer(
            position=NavigationDrawerPosition.START,
            controls=[Container(content=nav.NavControl(page, token),
                                expand=1,
                                padding=padding.only(right=10, top=10, bottom=10),
                                # margin=margin.only(right=10, bottom=10),
                                bgcolor=Colors.WHITE,
                                )]
        )

        count_cards = self.build()

        pagelet = Pagelet(
            appbar=AppBar(
                title=Text("仪表盘"),
                bgcolor=Colors.BLUE,
                center_title=True,
            ),
            content=Container(count_cards, padding=padding.all(0)),
            bgcolor=Colors.WHITE,
            drawer=self.drawer,
            width=self.page.width,
            height=self.page.height
        )

        self.controls = [pagelet]

    def query_summary_info(self):
        dct_info = {}
        token = self.page.client_storage.get('token')
        dct_ret = APIRequest.query_user_info(token)
        dct_info['nickname'] = dct_ret.get('nick_name', '用户名')

        dct_ret = APIRequest.query_todolist(token)
        todo_data = dct_ret[0].get('todo_data')
        dct_info['num_all'] = todo_data[0].get("count")
        dct_info['num_today'] = todo_data[1].get("count")
        dct_info['num_7days'] = todo_data[3].get("count")
        dct_info['num_expired'] = todo_data[2].get("count")
        return dct_info

    def nav_to_list(self, selected_nav):
        self.page.clean()
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
        token = self.page.client_storage.get('token')
        ctn_tasklist = Container(content=TaskListControl(token,
                                                         list_name,
                                                         list_title,
                                                         False),
                                 expand=4,
                                 # height=600,
                                 padding=padding.only(left=10, top=10, right=20),
                                 )
        ctn_nav = Container(content=nav.NavControl(token),
                            # width=300,
                            expand=1,
                            padding=padding.only(right=10, top=10),
                            bgcolor=Colors.WHITE,
                            )
        rows_main = Row([ctn_nav,
                         ctn_tasklist,
                         ],
                        alignment=MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=CrossAxisAlignment.START,
                        )
        ctn_main = Container(content=rows_main,
                             expand=True,
                             )
        self.page.add(ctn_main)
        self.page.update()

    def on_today_click(self, e):
        self.nav_to_list('today')

    def on_all_click(self, e):
        self.nav_to_list('all')

    def on_future_click(self, e):
        self.nav_to_list('future')

    def on_expired_click(self, e):
        self.nav_to_list('expired')

    def open_drawer(self, e):
        if self.page:
            if self.drawer not in self.page.controls:
                # self.page.add(self.drawer)
                # self.page.views.append(self.drawer)
                # self.page.controls.append(self.drawer)
                # self.page.overlay.append(self.drawer)
                pass
            # self.drawer.open = True
            # self.page.open(self.drawer)
            # self.drawer.open = True
            # self.page.drawer = self.drawer
            # self.page.drawer.open = True
            # self.page.open(self.page.drawer)
            self.drawer.open = True
            self.page.update()
            # self.drawer.update()

    # def did_mount(self):
    #     self.page.drawer = self.drawer

    def build(self):
        dct_info = self.query_summary_info()
        btn_show_drawer = IconButton(icon=Icons.MENU,
                                     on_click=self.open_drawer)

        card_all = Card(content=Container(
            content=Column([Text('全部待办', weight=FontWeight.BOLD, size=16, color=Colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_all")}', color=Colors.WHITE, size=24),
                                 Icon(Icons.ALL_INBOX, color='white')],
                                alignment=MainAxisAlignment.SPACE_BETWEEN)
                            ]),
            bgcolor=Colors.BLUE_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_all_click,
        ),
            width=200,
            height=120,
            elevation=2,
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
            width=200,
            height=120,
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
            width=200,
            height=120,
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
            width=200,
            height=120,
            elevation=2,
        )
        row_stat_1 = Row([card_all, card_today],
                       expand=True,
                       alignment=MainAxisAlignment.START)
        row_stat_2 = Row([card_future, card_expired],
                       expand=True,
                       alignment=MainAxisAlignment.START)
        col_dash = Column([
            # btn_show_drawer,
            Text(f'欢迎您，{dct_info.get("nickname")}',
                                weight=FontWeight.BOLD, size=24, ),
            Text('以下是当前任务统计数据',
                                weight=FontWeight.BOLD,
                                size=18,
                                color=Colors.BLACK38),
                           # Container(content=row_info, expand=True)]
            row_stat_1,
            row_stat_2],
            alignment=MainAxisAlignment.START)

        return col_dash
