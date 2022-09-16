import requests, json
from datetime import datetime
from flet import Text, Container, Column, Icon, Row, TextButton, TextField, Image, \
    icons, alignment, colors, border, margin, border_radius, padding, \
    UserControl, ListTile, Switch, VerticalDivider, Checkbox, Card, GridView


class DashboardControl(UserControl):
    def __init__(self, token):
        super().__init__()
        self.token = token

    def query_summary_info(self):
        dct_info = {}
        headers = {'Authorization': f'jwt {self.token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/user_info/',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('results')
        dct_info['nickname'] = dct_ret.get('nick_name', '用户名')

        req = requests.get(url='https://restapi.10qu.com.cn/todo_profile/?show_expired=1',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('result')

        todo_data = dct_ret[0].get('todo_data')
        dct_info['num_all'] = todo_data[0].get("count")
        dct_info['num_today'] = todo_data[1].get("count")
        dct_info['num_7days'] = todo_data[3].get("count")
        dct_info['num_expired'] = todo_data[2].get("count")
        return dct_info

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
            expand=True
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
            expand=True
        ),
            width=200,
            height=120,
            elevation=2,
        )
        card_7days = Card(content=Container(
            content=Column([Text('未来七天', weight='bold', size=16, color=colors.WHITE54),
                            Row([Text(f'{dct_info.get("num_7days")}', color=colors.WHITE, size=24),
                                 Icon(icons.WEEKEND_ROUNDED, color='white')], alignment='spaceBetween')
                            ]),
            bgcolor=colors.RED_400,
            padding=padding.all(10),
            border_radius=5,
            expand=True
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
            expand=True
        ),
            width=200,
            height=120,
            elevation=2,
        )
        row_info = Row([card_all, card_today, card_7days, card_expired],
                       expand=True,
                       alignment='center')
        col_dash = Column([Text(f'欢迎您，{dct_info.get("nickname")}', weight='bold', size=24,),
                           Text('以下是当前任务统计数据', weight='bold', size=18, color=colors.BLACK38,),
                           Container(content=row_info, expand=True)]
                          )

        return col_dash
