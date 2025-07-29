# coding:utf-8
from urllib.parse import urlparse, parse_qs

import flet
from flet import Page, Theme
from flet.core import padding
from flet.core.safe_area import SafeArea
from flet.core.types import VisualDensity, MainAxisAlignment, CrossAxisAlignment, ThemeMode, PagePlatform, ScrollMode
from flet.core.view import View

from login import LoginControl
from dashboard import DashboardControl
from api_request import APIRequest
from tasklist import TaskListControl

def login_interface(page: Page):
    return SafeArea(LoginControl(page),
                    maintain_bottom_view_padding=True,
                    expand=True)

def dashboard_interface(page: Page):
    return SafeArea(DashboardControl(page),
                    maintain_bottom_view_padding=True,
                    expand=True)

def tasklist_interface(page: Page, list_id):
    return SafeArea(
        TaskListControl(page, list_id),
        bottom=True,
        expand=True)

def main(page: Page):
    # 页面属性
    page.adaptive = True
    page.title = '布尔清单'
    page.window.icon = '/icons/app_icon.png'
    # page.bgcolor = Colors.WHITE
    page.scroll = ScrollMode.ADAPTIVE
    # page.padding=padding.only(bottom=28)
    # page.margin=margin.all(0)
    page.platform=PagePlatform.ANDROID
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    # page.appbar = AppBar(title=Text("主页"), bgcolor=Colors.BLUE_GREY_100)
    page.theme_mode = ThemeMode.SYSTEM
    page.theme = Theme(
        color_scheme_seed="blue",
        font_family='微软雅黑',
        visual_density=VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
        use_material3=False)
    page.dark_theme = Theme(
        color_scheme_seed="green",
        font_family='微软雅黑',
        visual_density=VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
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
                                   [tasklist_interface(page, list_id)],
                                   adaptive=True))
        page.update()

    page.on_route_change = route_change

    # 初始页面
    token = page.client_storage.get('token')
    if token is not None:
        token = token.strip('"')
        dct_ret = APIRequest.query_user_info(token)
        if dct_ret is not None:
            page.go('/dashboard')
        else:
            page.go('/login')
    else:
        page.go('/')

    page.window.center()


flet.app(
    target=main,
    assets_dir='assets',
    view=flet.AppView.WEB_BROWSER)
