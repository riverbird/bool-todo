import flet
from flet import Page, Theme, Row, Container, padding, Colors
from flet.core.types import VisualDensity, MainAxisAlignment, CrossAxisAlignment

from login import LoginControl
from nav import NavControl
from dashboard import DashboardControl
from api_request import APIRequest


def show_login_interface(page):
    page.add(LoginControl())


def show_main_interface(page, token):
    page.clean()
    page.horizontal_alignment = 'start'
    page.vertical_alignment = 'start'
    page.padding = 0
    rows_main = Row([Container(content=NavControl(token),
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
    page.add(ctn_main)


def main(page: Page):
    page.title = '拾趣清单'
    page.bgcolor = '#f2f4f8'
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'
    page.theme_mode = 'light'

    # page.fonts = {
    #     'Sarasa': '/fonts/sarasa-regular.ttc'
    # }
    page.theme = Theme(color_scheme_seed="blue",
                             font_family='微软雅黑',
                             visual_density=VisualDensity.COMPACT,
                             use_material3=False
                             )
    page.dark_theme = Theme(color_scheme_seed="green",
                                  font_family='微软雅黑',
                                  visual_density=VisualDensity.COMPACT,
                                  use_material3=False
                                  )
    token = page.client_storage.get('token')
    # print(token)
    if token is not None:
        token = token.strip('"')
        dct_ret = APIRequest.query_user_info(token)
        if dct_ret is not None:
            show_main_interface(page, token)
        else:
            show_login_interface(page)
    else:
        show_login_interface(page)
    # page.window_center()


flet.app(
    target=main,
    assets_dir='assets',
    # view=flet.WEB_BROWSER,
)
