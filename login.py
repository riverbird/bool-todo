import requests, json
from flet import Text, Card, Container, Column, Row, TextButton, TextField, Image, \
    FilledButton, Tabs, Tab, icons, alignment, colors, border, margin, border_radius, \
    UserControl, padding
from nav import NavControl
from dashboard import DashboardControl
from api_request import APIRequest


class LoginControl(UserControl):
    def on_tab_change(self, e):
        if self.tabs_login.selected_index == 0:
            self.view_status = 0
        elif self.tabs_login.selected_index == 1:
            self.view_status = 2

    def on_id_code_login_click(self, e):
        self.view_status = 1
        self.tabs_login.tabs[0].content = Container(content=self.card_login_id_code,
                                                    alignment=alignment.center)
        self.tabs_login.update()

    def on_password_login_click(self, e):
        self.view_status = 0
        self.tabs_login.tabs[0].content = Container(content=self.card_login,
                                                    alignment=alignment.center)
        self.tabs_login.update()

    def on_login_click(self, e):
        if self.view_status == 0:
            req = APIRequest.login_by_password(self.tf_phone_num.value, self.tf_password.value)
            json_req = json.loads(req.text)
            if req.status_code == 200 and json_req.get('code') == '0':
                dct_ret = json_req.get('result')
                self.page.client_storage.set('username', dct_ret.get('username'))
                self.page.client_storage.set('nickname', dct_ret.get('nickname'))
                self.page.client_storage.set('avatar', dct_ret.get('avatar'))
                self.page.client_storage.set('token', dct_ret.get('token'))
                # x = self.page.client_storage.get('nickname')
                # self.page.client_storage.update()

                self.page.clean()
                self.page.horizontal_alignment = 'start'
                self.page.vertical_alignment = 'start'
                self.page.padding = 0
                # self.page.scroll = 'auto'
                # self.page.auto_scroll = True
                rows_main = Row([Container(content=NavControl(self.page.width,
                                                              self.page.height,
                                                              dct_ret.get('token')),
                                           # width=300,
                                           # height=self.page.window_height + 10,
                                           # height=800,
                                           expand=1,
                                           padding=padding.only(right=10, top=10),
                                           # margin=margin.only(bottom=10),
                                           bgcolor=colors.WHITE,
                                           ),
                                 Container(content=DashboardControl(dct_ret.get('token')),
                                           expand=4,
                                           height=600,
                                           padding=padding.only(left=10, top=10, bottom=20, right=20),
                                           ),
                                 ],
                                alignment='spaceAround',
                                vertical_alignment='start',
                                )
                self.page.add(rows_main)

    def build(self):
        self.view_status = 0  # 用于甄别具体是何登录注册视图
        self.tf_phone_num = TextField(label='手机号',
                                      value='13588459825')
        self.tf_password = TextField(label='密码',
                                     value='123456',
                                     password=True,
                                     can_reveal_password=True)
        self.card_login = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        Row(
                            [self.tf_password,
                             TextButton('忘记密码')]
                        ),
                        FilledButton(text='登录', width=300, on_click=self.on_login_click),
                        TextButton('验证码登录', on_click=self.on_id_code_login_click)
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=colors.WHITE,
            )
        )

        self.card_login_id_code = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        TextField(label='手机号'),
                        Row(
                            [TextField(label='验证码'),
                             TextButton('获取码')]
                        ),
                        FilledButton(text='登录', width=300),
                        TextButton('密码登录', on_click=self.on_password_login_click)
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=colors.WHITE,
            )
        )

        self.card_reg = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        TextField(label='手机号'),
                        TextField(label='请输入密码', password=True, can_reveal_password=True),
                        TextField(label='请确认密码', password=True, can_reveal_password=True),
                        FilledButton(text='注册', width=300, expand=False),
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=colors.WHITE,
            )
        )

        self.tabs_login = Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    text="登录",
                    content=Container(
                        content=self.card_login,
                        alignment=alignment.center,
                        padding=10,
                        margin=10,
                    ),
                ),
                Tab(
                    text="注册",
                    content=Container(
                        content=self.card_reg,
                        alignment=alignment.center,
                        padding=10,
                        margin=10,
                    ),
                ),
            ],
            expand=1,
            on_change=self.on_tab_change,
        )

        container_login = Container(
            content=Column(
                [
                    Row([
                        Image(src=f'/icons/shiqu-todo-logo.png',
                              width=64, height=64,
                              fit='contain',
                              border_radius=border_radius.all(30)),
                        Text('拾趣清单', size=24, color=colors.BLUE,
                             weight='bold',
                             ),
                    ]),
                    self.tabs_login,
                ]
            ),
            padding=20,
            margin=margin.all(20),
            width=500,
            height=440,
            border=border.all(1, colors.BLACK12),
            bgcolor=colors.WHITE,
            alignment=alignment.center,
        )

        return container_login
