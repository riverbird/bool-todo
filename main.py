import flet
from flet import Page, theme
from login import LoginControl


def main(page: Page):
    page.title = '拾趣清单'
    page.bgcolor = '#f2f4f8'
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'
    page.fonts = {
        'Sarasa': '/fonts/sarasa-regular.ttc'
    }
    page.theme = theme.Theme(color_scheme_seed="blue",
                             # font_family='Sarasa',
                             font_family='微软雅黑',
                             visual_density='compact')
    page.add(LoginControl())
    page.window_center()


flet.app(target=main,
         assets_dir='assets',
         # view=flet.WEB_BROWSER,
         )
