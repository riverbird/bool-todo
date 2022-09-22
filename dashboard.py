from flet import Text, Container, Column, Icon, Row,  \
    icons, colors, padding, \
    UserControl,  Card
from api_request import APIRequest
from tasklist import TaskListControl
import nav


class DashboardControl(UserControl):
    def __init__(self, token):
        super().__init__()
        self.token = token

    def query_summary_info(self):
        dct_info = {}
        dct_ret = APIRequest.query_user_info(self.token)
        dct_info['nickname'] = dct_ret.get('nick_name', '用户名')

        dct_ret = APIRequest.query_todolist(self.token)
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
        ctn_tasklist = Container(content=TaskListControl(self.page.width,
                                                         self.page.height,
                                                         self.token,
                                                         list_name,
                                                         list_title,
                                                         False),
                                 expand=4,
                                 # height=600,
                                 padding=padding.only(left=10, top=10, right=20),
                                 )
        rows_today = Row([Container(content=nav.NavControl(self.page.width,
                                                           self.page.height,
                                                           self.token),
                                    # width=300,
                                    expand=1,
                                    padding=padding.only(right=10, top=10),
                                    bgcolor=colors.WHITE,
                                    ),
                          ctn_tasklist,
                          ],
                         alignment='spaceAround',
                         vertical_alignment='start',
                         )
        self.page.add(rows_today)
        self.page.update()

    def on_today_click(self, e):
        self.nav_to_list('today')

    def on_all_click(self, e):
        self.nav_to_list('all')

    def on_future_click(self, e):
        self.nav_to_list('future')

    def on_expired_click(self, e):
        self.nav_to_list('expired')

    def build(self):
        dct_info = self.query_summary_info()

        card_all = Card(content=Container(
            content=Column([Text('全部待办', weight='bold', size=16, color=colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_all")}', color=colors.WHITE, size=24),
                                 Icon(icons.ALL_INBOX, color='white')], alignment='spaceBetween')
                            ]),
            bgcolor=colors.BLUE_400,
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
            content=Column([Text('今天', weight='bold', size=16, color=colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_today")}', color=colors.WHITE, size=24),
                                 Icon(icons.TODAY, color='white')], alignment='spaceBetween')
                            ]),
            bgcolor=colors.ORANGE_400,
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
            content=Column([Text('未来七天', weight='bold', size=16, color=colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_7days")}', color=colors.WHITE, size=24),
                                 Icon(icons.WEEKEND_ROUNDED, color='white')], alignment='spaceBetween')
                            ]),
            bgcolor=colors.RED_400,
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
            content=Column([Text('已过期', weight='bold', size=16, color=colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_expired")}', color=colors.WHITE, size=24),
                                 Icon(icons.ACCOUNT_BOX, color='white')], alignment='spaceBetween')
                            ]),
            bgcolor=colors.GREEN_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True,
            on_click=self.on_expired_click,
        ),
            width=200,
            height=120,
            elevation=2,
        )
        row_info = Row([card_all, card_today, card_future, card_expired],
                       expand=True,
                       alignment='center')
        col_dash = Column([Text(f'欢迎您，{dct_info.get("nickname")}', weight='bold', size=24, ),
                           Text('以下是当前任务统计数据',
                                weight='bold',
                                size=18,
                                color=colors.BLACK38,
                                ),
                           Container(content=row_info, expand=True)]
                          )

        return col_dash
