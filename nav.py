import requests, json
from requests.auth import HTTPBasicAuth
from flet import Text, Container, Column, Icon, Row, TextButton, TextField, Image, \
    icons, alignment, colors, border, margin, border_radius, padding, \
    UserControl, ListTile, IconButton, CircleAvatar, PopupMenuButton, PopupMenuItem, \
    AlertDialog, Divider, SnackBar
import login
from api_request import APIRequest
from tasklist import TaskListControl
from dashboard import DashboardControl


class NavControl(UserControl):
    def __init__(self, page_width, page_height, token):
        super().__init__()
        self.page_width = page_width
        self.page_height = page_height
        self.token = token

    def on_dashboard_click(self, e):
        right_ctn = self.page.controls[0].controls[1]
        self.page.controls[0].controls.remove(right_ctn)
        dashboard = Container(content=DashboardControl(self.token),
                              expand=4,
                              height=600,
                              padding=padding.only(left=10, top=10, bottom=20, right=20),
                              )
        self.page.controls[0].controls.append(dashboard)
        self.page.update()

    def on_list_click(self, e):
        list_title_text = e.control.title.value.split(' ')[0]
        list_name = 'today'
        if list_title_text == '今天':
            list_name = 'today'
        elif list_title_text == '未来七天':
            list_name = 'future'
        elif list_title_text == '已过期':
            list_name = 'expired'
        right_ctn = self.page.controls[0].controls[1]
        self.page.controls[0].controls.remove(right_ctn)
        ctn_today = Container(content=TaskListControl(self.page.width,
                                                      self.page.height,
                                                      self.token,
                                                      list_name,
                                                      False),
                              expand=4,
                              padding=padding.only(left=10, top=10, bottom=20, right=20),
                              )
        self.page.controls[0].controls.append(ctn_today)
        self.col_nav.update()
        self.page.update()

    def on_today_click(self, e):
        self.lt_today.selected = False
        self.col_nav.update()

    def on_about_ok_click(self, e):
        self.dlg_about.open = False
        # self.update()
        self.page.update()

    def on_about_click(self, e):
        self.page.dialog = self.dlg_about
        self.dlg_about.open = True
        # self.update()
        self.page.update()

    def on_dark_click(self, e):
        self.page.theme_mode = 'dark'
        self.page.update()

    def on_logout(self, e):
        req_result = APIRequest.logout(self.token)
        if req_result is True:
            self.page.clean()
            self.page.bgcolor = '#f2f4f8'
            self.page.vertical_alignment = 'center'
            self.page.horizontal_alignment = 'center'
            self.page.add(login.LoginControl())
            self.page.update()
            return
        self.page.snack_bar = SnackBar(Text("用户退出登录请求失败!"))
        self.page.snack_bar.open = True
        self.page.update()

    def on_cate_click(self, e):
        cate_id = self.dct_cate.get(e.control)
        right_ctn = self.page.controls[0].controls[1]
        self.page.controls[0].controls.remove(right_ctn)
        ctn_tasks = Container(content=TaskListControl(self.page.width,
                                                      self.page.height,
                                                      self.token,
                                                      cate_id,
                                                      False),
                              expand=4,
                              padding=padding.only(left=10, top=10, bottom=20, right=20),
                              )
        self.page.controls[0].controls.append(ctn_tasks)
        self.col_nav.update()
        self.page.update()

    def update_user_info(self):
        headers = {'Authorization': f'jwt {self.token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/user_info/',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('results')
        self.text_user.value = dct_ret.get('nick_name', '用户名')
        self.img_avatar.src = dct_ret.get('avatar_url', f'/icons/head.png')

    def update_todolist(self):
        headers = {'Authorization': f'jwt {self.token}'}
        req = requests.get(url='https://restapi.10qu.com.cn/todo_profile/?show_expired=1',
                           headers=headers)
        json_req = json.loads(req.text)
        dct_ret = json_req.get('result')

        todo_data = dct_ret[0].get('todo_data')
        self.lt_today.title = Text(f'今天 {todo_data[1].get("count")}')
        self.lt_week.title = Text(f'未来七天 {todo_data[3].get("count")}')
        self.lt_pass.title = Text(f'已过期 {todo_data[2].get("count")}')
        self.lt_all.title = Text(f'全部 {todo_data[0].get("count")}')

        todo_data = dct_ret[1].get('todo_data')
        self.dct_cate = {}
        for itm in todo_data:
            lt_cate = ListTile(leading=Icon(icons.LIST),
                               title=Text(f'{itm.get("name")} {itm.get("count")}'),
                               selected=False,
                               dense=True,
                               on_click=self.on_cate_click)
            self.col_nav.controls.append(lt_cate)
            self.dct_cate[lt_cate] = itm.get('from_id')

    def build(self):
        self.dlg_about = AlertDialog(modal=True,
                                     title=Text('关于'),
                                     content=Column(controls=[Divider(height=1, color='gray'),
                                                              Text('拾趣清单v2.0(alpha)'),
                                                              Text('西安鸿途四海网络科技有限公司 出品'),
                                                              Text('官网: http://www.10qu.com.cn'),
                                                              ],
                                                    alignment='start',
                                                    width=300,
                                                    height=100,
                                                    ),
                                     actions=[TextButton("确定", on_click=self.on_about_ok_click), ],
                                     actions_alignment="end",
                                     title_padding=20,
                                     on_dismiss=lambda e: print("Modal dialog dismissed!"),

                                     )

        self.lt_today = ListTile(leading=Icon(icons.TODAY),
                                 title=Text("今天"),
                                 selected=False,
                                 dense=True,
                                 on_click=self.on_list_click)
        self.lt_week = ListTile(leading=Icon(icons.CALENDAR_VIEW_WEEK),
                                title=Text("近七天"),
                                selected=False,
                                dense=True,
                                on_click=self.on_list_click)
        self.lt_pass = ListTile(leading=Icon(icons.HEXAGON_OUTLINED),
                                title=Text("已过期"),
                                selected=False,
                                dense=True,
                                on_click=self.on_list_click)
        self.lt_all = ListTile(leading=Icon(icons.ALL_INBOX),
                               title=Text("全部"),
                               selected=False,
                               dense=True,
                               on_click=self.on_list_click)
        self.img_avatar = Image(src=f'/icons/head.png', width=32, height=32, fit='contain',
                                border_radius=border_radius.all(30))
        # self.img_avatar = CircleAvatar(foreground_image_url=f'/icons/head.png',
        #                                bgcolor=colors.BLACK38,
        #                                radius=5,
        #                                content=Text('头像'))

        self.text_user = Text('用户名', size=14)
        self.pmb_option = PopupMenuButton(items=[PopupMenuItem(icon=icons.DARK_MODE,
                                                               text='深色模式',
                                                               on_click=self.on_dark_click),
                                                 PopupMenuItem(icon=icons.HELP,
                                                               text='关于我们',
                                                               on_click=self.on_about_click),
                                                 PopupMenuItem(icon=icons.ACCOUNT_BOX, text='账户安全'),
                                                 PopupMenuItem(icon=icons.LOGOUT,
                                                               text='退出登录',
                                                               on_click=self.on_logout),
                                                 ],
                                          icon=icons.HELP,
                                          )
        self.row_head = Row(controls=[self.img_avatar,
                                      self.text_user,
                                      self.pmb_option],
                            alignment='spaceEvenly',
                            vertical_alignment='center',
                            spacing=10)

        self.col_cate = Column()
        self.col_nav = Column(
            [
                self.row_head,
                ListTile(
                    title=Text("仪表盘", weight='bold'),
                    leading=Icon(icons.DASHBOARD),
                    on_click=self.on_dashboard_click,
                ),
                ListTile(
                    title=Text("列表", weight='bold'),
                    leading=Icon(icons.LIST_ALT_SHARP)
                ),
                self.lt_today,
                self.lt_week,
                self.lt_pass,
                self.lt_all,
                ListTile(
                    title=Text("清单", weight='bold'),
                    leading=Icon(icons.LIST_ALT)
                ),
                self.col_cate,
            ],
            spacing=0,
            # expand=True,
            alignment='start',
            scroll='hidden',
        )

        self.update_user_info()
        self.update_todolist()

        return [self.col_nav, self.dlg_about]
