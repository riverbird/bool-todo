# coding:utf-8
import json
from enum import Enum

from flet import Text, Card, Container, Column, Row, TextButton, TextField, Image, \
    FilledButton, Tabs, Tab, Colors, border, margin, border_radius, \
    padding, SnackBar
from flet.core.form_field_control import InputBorder
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.navigation_drawer import NavigationDrawer
from flet.core.types import MainAxisAlignment, CrossAxisAlignment, ImageFit, FontWeight

from nav import NavControl
from dashboard import DashboardControl
from api_request import APIRequest

class LoginViewStatus(Enum):
    ViewLoginUsername = 0,
    ViewLoginSmsView = 1,
    ViewRegistration = 2


class LoginControl(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.view_status:LoginViewStatus = LoginViewStatus.ViewLoginUsername  # 用于甄别具体是何登录注册视图
        container_login = self.build()
        self.controls = [container_login]

    def on_tab_change(self, e):
        match self.tabs_login.selected_index:
            case 0:
                self.view_status = LoginViewStatus.ViewLoginUsername
            case 1:
                self.view_status = LoginViewStatus.ViewRegistration

    def on_id_code_login_click(self, e):
        self.view_status = LoginViewStatus.ViewLoginSmsView
        # self.tabs_login.tabs[0].content.content = self.card_login_id_code
        self.tabs_login.tabs[0] = Tab(
                    text="登录",
                    content=Container(
                        content=self.card_login_id_code,
                        # alignment=alignment.center,
                        padding=10,
                        margin=10,
                    ),
                )
        # self.tabs_login.update()
        # e.page.update()

    def on_password_login_click(self, e):
        self.view_status = LoginViewStatus.ViewLoginUsername
        self.tabs_login.tabs[0].content = Container(
            content=self.card_login,
            padding=10,
            margin=10)
        # self.tabs_login.update()

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
        if self.view_status != LoginViewStatus.ViewLoginUsername:
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

        # self.show_main_interface(dct_ret.get('token'))

        # self.left_drawer = NavigationDrawer(
        #     controls=[Container(content=NavControl(dct_ret.get('token')),
        #                         expand=1,
        #                         padding=padding.only(right=10, top=10, bottom=10),
        #                         # margin=margin.only(right=10, bottom=10),
        #                         bgcolor=Colors.WHITE,
        #                         )]
        # )
        # self.page.add(left_drawer)
        # self.page.drawer = self.left_drawer

        self.page.go('/dashboard')

    def on_code_login_click(self, e):
        if self.view_status != LoginViewStatus.ViewLoginSmsView:
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
        self.page.horizontal_alignment = CrossAxisAlignment.START
        self.page.vertical_alignment = MainAxisAlignment.START
        self.page.padding = 0
        # self.page.scroll = 'auto'
        # self.page.auto_scroll = True

        left_drawer = NavigationDrawer(
            controls=[Container(content=NavControl(token),
                                expand=1,
                                padding=padding.only(right=10, top=10, bottom=10),
                                # margin=margin.only(right=10, bottom=10),
                                bgcolor=Colors.WHITE,
                                )]
        )

        btn_show_drawer = IconButton(icon=Icons.MENU,
                                     on_click=lambda e: self.page.open(left_drawer))

        rows_main = Row([Container(content=NavControl(token),
                                   # width=300,
                                   # height=self.page.window_height + 10,
                                   # height=800,
                                   expand=1,
                                   padding=padding.only(right=10, top=10, bottom=10),
                                   # margin=margin.only(right=10, bottom=10),
                                   # bgcolor=colors.WHITE if self.page.theme_mode == 'light' else colors.BLACK87,
                                   bgcolor=Colors.WHITE,
                                   ),
                         Container(content=DashboardControl(token),
                                   expand=4,
                                   # height=600,
                                   padding=padding.only(left=10, top=10, bottom=20, right=20),
                                   # bgcolor='#f2f4f8' if self.page.theme_mode == 'light' else colors.BLACK87,
                                   ),
                         ],
                        alignment=MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=CrossAxisAlignment.START,
                        )
        ctn_main = Container(content=rows_main,
                             expand=True)

        self.page.add(btn_show_drawer)
        # self.page.add(ctn_main)

    def build(self):
        self.tf_phone_num = TextField(label='手机号',
                                      # icon=Icons.PHONE,
                                      border=InputBorder.OUTLINE,
                                      value='13588459825',
                                      )
        self.tf_password = TextField(label='密码',
                                     # icon=Icons.PASSWORD,
                                     border=InputBorder.OUTLINE,
                                     value='iloveyou365',
                                     password=True,
                                     can_reveal_password=True)
        self.tf_verify_code = TextField(label='验证码',
                                        # icon=Icons.CODE,
                                        border=InputBorder.OUTLINE)
        self.tf_pass_1 = TextField(label='请输入密码',
                                   # icon=Icons.PASSWORD,
                                   border=InputBorder.OUTLINE,
                                   password=True,
                                   can_reveal_password=True)
        self.tf_pass_2 = TextField(label='请确认密码',
                                   # icon=Icons.PASSWORD,
                                   border=InputBorder.OUTLINE,
                                   password=True,
                                   can_reveal_password=True)
        self.card_login = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        self.tf_password,
                        FilledButton(text='登录',
                                     icon=Icons.LOGIN,
                                     width=400,
                                     on_click=self.on_login_click),
                        TextButton('验证码登录', on_click=self.on_id_code_login_click)
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=Colors.WHITE,
            )
        )

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
                        FilledButton(text='登录', width=400, on_click=self.on_code_login_click),
                        TextButton('密码登录', on_click=self.on_password_login_click)
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=Colors.WHITE,
            )
        )

        self.card_reg = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        self.tf_pass_1,
                        self.tf_pass_2,
                        FilledButton(text='注册',
                                     width=400,
                                     icon=Icons.APP_REGISTRATION,
                                     on_click=self.on_reg_click),
                    ]
                ),
                width=400,
                padding=10,
                bgcolor=Colors.WHITE,
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
                        # alignment=alignment.center,
                        padding=10,
                        margin=10,
                    ),
                ),
                Tab(
                    text="注册",
                    content=Container(
                        content=self.card_reg,
                        # alignment=alignment.center,
                        padding=10,
                        margin=10,
                    ),
                ),
            ],
            expand=True,
            on_change=self.on_tab_change,
        )

        container_login = Container(
            content=Column(
                [
                    Row([
                        Image(src=f'/icons/shiqu-todo-logo.png',
                              width=64, height=64,
                              fit=ImageFit.CONTAIN,
                              border_radius=border_radius.all(30)),
                        Text('布尔清单', size=24, color=Colors.BLUE,
                             weight=FontWeight.BOLD,
                             ),
                    ]),
                    self.tabs_login,
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER
            ),
            padding=20,
            margin=margin.all(20),
            width=self.page.width,
            height=450,
            border=border.all(1, Colors.BLACK12),
            bgcolor=Colors.WHITE
        )

        return container_login
