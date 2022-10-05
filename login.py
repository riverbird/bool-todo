import json
from flet import Text, Card, Container, Column, Row, TextButton, TextField, Image, \
    FilledButton, Tabs, Tab, alignment, colors, border, margin, border_radius, \
    UserControl, padding, SnackBar
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

    def on_send_sms(self, e):
        req_result = APIRequest.send_sms(self.tf_phone_num.value)
        # if req_result.status_code in [200, 201, 202]:
        str_msg = req_result.text.replace('"', '')
        self.page.snack_bar = SnackBar(Text(f"{str_msg}"))
        self.page.snack_bar.open = True
        self.page.update()

    # 用户名密码登录
    def on_login_click(self, e):
        # self.page.bgcolor = '#f2f4f8' if self.page.theme_mode == 'light' else colors.BLACK87
        if self.view_status != 0:
            return
        req = APIRequest.login_by_password(self.tf_phone_num.value, self.tf_password.value)
        json_req = json.loads(req.text)

        if req.status_code != 200 or json_req.get('code') != '0':
            self.page.snack_bar = SnackBar(Text(f"{json_req.get('msg')}"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        dct_ret = json_req.get('result')
        self.page.client_storage.set('username', dct_ret.get('username'))
        self.page.client_storage.set('nickname', dct_ret.get('nickname'))
        self.page.client_storage.set('avatar', dct_ret.get('avatar'))
        self.page.client_storage.set('token', dct_ret.get('token'))
        # x = self.page.client_storage.get('nickname')
        # self.page.client_storage.update()

        self.show_main_interface(dct_ret.get('token'))

    def on_code_login_click(self, e):
        if self.view_status != 1:
            return
        req = APIRequest.login_by_code(self.tf_phone_num.value, self.tf_verify_code.value)
        json_req = req
        if json_req.get('code') != '0':
            self.page.snack_bar = SnackBar(Text(f"{json_req.get('msg')}"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        dct_ret = json_req.get('result')
        self.page.client_storage.set('username', dct_ret.get('username'))
        self.page.client_storage.set('nickname', dct_ret.get('nickname'))
        self.page.client_storage.set('avatar', dct_ret.get('avatar'))
        self.page.client_storage.set('token', dct_ret.get('token'))
        # x = self.page.client_storage.get('nickname')
        # self.page.client_storage.update()

        self.show_main_interface(dct_ret.get('token'))

    # 用户通过用户名密码进行注册
    def on_reg_click(self, e):
        if len(self.tf_phone_num.value) == 0 or len(self.tf_pass_1.value) == 0 or len(self.tf_pass_2.value) == 0:
            self.page.snack_bar = SnackBar(Text("用户名或密码不得为空！"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        if self.tf_pass_1.value != self.tf_pass_2.value:
            self.page.snack_bar = SnackBar(Text("两次输入的密码不一致！"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        ret_result = APIRequest.registry(self.tf_phone_num.value, self.tf_pass_1.value)
        if ret_result.get('code') != '0':
            self.page.snack_bar = SnackBar(Text(f"{ret_result.get('msg')}"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.page.snack_bar = SnackBar(Text(f"{ret_result.get('msg')}, 请跳转至登录页进行登录！"))
        self.page.snack_bar.open = True
        self.page.update()

    def show_main_interface(self, token):
        self.page.clean()
        self.page.horizontal_alignment = 'start'
        self.page.vertical_alignment = 'start'
        self.page.padding = 0
        # self.page.scroll = 'auto'
        # self.page.auto_scroll = True
        rows_main = Row([Container(content=NavControl(self.page.width,
                                                      self.page.height,
                                                      token),
                                   # width=300,
                                   # height=self.page.window_height + 10,
                                   # height=800,
                                   expand=1,
                                   padding=padding.only(right=10, top=10, bottom=10),
                                   # margin=margin.only(right=10, bottom=10),
                                   # bgcolor=colors.WHITE if self.page.theme_mode == 'light' else colors.BLACK87,
                                   bgcolor=colors.WHITE,
                                   ),
                         Container(content=DashboardControl(token),
                                   expand=4,
                                   # height=600,
                                   padding=padding.only(left=10, top=10, bottom=20, right=20),
                                   # bgcolor='#f2f4f8' if self.page.theme_mode == 'light' else colors.BLACK87,
                                   ),
                         ],
                        alignment='spaceAround',
                        vertical_alignment='start',
                        )
        ctn_main = Container(content=rows_main,
                             expand=True,
                             )
        self.page.add(ctn_main)

    def build(self):
        self.view_status = 0  # 用于甄别具体是何登录注册视图
        self.tf_phone_num = TextField(label='手机号',
                                      border='underline',
                                      value='13588459825',
                                      )
        self.tf_password = TextField(label='密码',
                                     border='underline',
                                     value='123456',
                                     password=True,
                                     can_reveal_password=True)
        self.card_login = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        # Row(
                        #     [self.tf_password,
                        #      TextButton('忘记密码'),
                        #      ]
                        # ),
                        self.tf_password,
                        FilledButton(text='登录', width=300, on_click=self.on_login_click),
                        TextButton('验证码登录', on_click=self.on_id_code_login_click)
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=colors.WHITE,
            )
        )

        self.tf_verify_code = TextField(label='验证码',
                                        border='underline',)
        self.card_login_id_code = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        Row(
                            [self.tf_verify_code,
                             TextButton('获取验证码', on_click=self.on_send_sms)]
                        ),
                        FilledButton(text='登录', width=300, on_click=self.on_code_login_click),
                        TextButton('密码登录', on_click=self.on_password_login_click)
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=colors.WHITE,
            )
        )

        self.tf_pass_1 = TextField(label='请输入密码',
                                   border='underline',
                                   password=True,
                                   can_reveal_password=True)
        self.tf_pass_2 = TextField(label='请确认密码',
                                   border='underline',
                                   password=True,
                                   can_reveal_password=True)
        self.card_reg = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        self.tf_pass_1,
                        self.tf_pass_2,
                        FilledButton(text='注册', width=400, on_click=self.on_reg_click),
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
