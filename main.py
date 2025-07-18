# coding:utf-8
from urllib.parse import urlparse, parse_qs

import flet
from flet import Page, Theme, Row, Container, padding, Colors
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.navigation_drawer import NavigationDrawer
from flet.core.types import VisualDensity, MainAxisAlignment, CrossAxisAlignment, ThemeMode, AppView
from flet.core.view import View

from login import LoginControl
from nav import NavControl
from dashboard import DashboardControl
from api_request import APIRequest
from tasklist import TaskListControl


def login_interface(page: Page):
    return LoginControl(page)

def dashboard_interface(page: Page):
    return DashboardControl(page)

def tasklist_interface(page: Page, list_id):
    return TaskListControl(page, list_id)

def show_login_interface(page):
    page.add(LoginControl())

def show_main_interface(page, token):
    page.clean()
    page.horizontal_alignment = CrossAxisAlignment.START
    page.vertical_alignment = MainAxisAlignment.START
    page.padding = padding.all(10)

    left_drawer = NavigationDrawer(
        controls=[Container(content=NavControl(token),
                            expand=1,
                            padding=padding.only(right=10, top=10, bottom=10),
                            # margin=margin.only(right=10, bottom=10),
                            bgcolor=Colors.WHITE,
                            )]
    )

    btn_show_drawer = IconButton(icon=Icons.MENU,
                                 on_click=lambda e: page.open(left_drawer))

    rows_main = Row([
                    Container(content=NavControl(token),
                               expand=1,
                               padding=padding.only(right=10, top=10, bottom=10),
                               # margin=margin.only(right=10, bottom=10),
                               bgcolor=Colors.WHITE,
                               ),
                    Container(content=DashboardControl(token),
                               expand=4,
                               padding=padding.only(left=10, top=10, bottom=20, right=20),
                               ),
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.STRETCH,
                    )
    ctn_main = Container(content=rows_main,
                         expand=True,
                         )
    page.add(btn_show_drawer)
    page.add(ctn_main)


def main(page: Page):
    # 页面属性
    page.title = '布尔清单'
    page.bgcolor = '#f2f4f8'
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.theme_mode = ThemeMode.SYSTEM
    page.theme = Theme(color_scheme_seed="blue",
                             font_family='微软雅黑',
                             visual_density=VisualDensity.COMPACT,
                             use_material3=False)
    page.dark_theme = Theme(color_scheme_seed="green",
                                  font_family='微软雅黑',
                                  visual_density=VisualDensity.COMPACT,
                                  use_material3=False)

    # 路由处理
    def route_change(e):
        page.views.clear()
        match e.route:
            case '/':
                page.views.append(View('/',
                                       [login_interface(page)]))
            case '/login':
                page.views.append(View('/login',
                                       [login_interface(page)]))
            case '/dashboard':
                page.views.append(View('/dashboard',
                                       [dashboard_interface(page)]))
            # case '/tasklist':
            #     page.views.append(View('/tasklist',
            #                            [tasklist_interface(page)]))
        if e.route.startswith('/tasklist'):
            parsed_url = urlparse(e.route)
            query_params = parse_qs(parsed_url.query)
            list_id = query_params.get('id', [None])[0]
            if list_id not in ['today', 'all', 'future', 'expired']:
                list_id = int(list_id)
            page.views.append(View(e.route,
                                   [tasklist_interface(page, list_id)]))
        page.update()
    page.on_route_change = route_change

    # 初始页面
    token = page.client_storage.get('token')
    if token is not None:
        token = token.strip('"')
        dct_ret = APIRequest.query_user_info(token)
        if dct_ret is not None:
            # show_main_interface(page, token)
            page.go('/dashboard')
        else:
            # show_login_interface(page)
            page.go('/login')
    else:
        # show_login_interface(page)
        page.go('/')

    page.window.center()


flet.app(
    target=main,
    assets_dir='assets',
    view=flet.AppView.WEB_BROWSER)
