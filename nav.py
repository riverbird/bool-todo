# coding:utf-8
from flet import Text, Container, Column, Icon, Row, TextButton, \
    Icons, border_radius, Image,  \
    ListTile, PopupMenuButton, PopupMenuItem, \
    AlertDialog, Divider, SnackBar, TextField, Colors
from flet.core.progress_ring import ProgressRing
from flet.core.types import MainAxisAlignment, CrossAxisAlignment, FontWeight, ScrollMode, ImageFit

from api_request import APIRequest

class NavControl(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.token = self.page.client_storage.get('token')

        self.dct_cate = {}  # ListTile:CateId
        self.dct_cate_title = {}  # CateId: CateName

        self.dlg_about = AlertDialog(
             modal=True,
             title=Text('关于'),
             content=Column(controls=[Divider(height=1, color='gray'),
                                      Text('布尔清单v2.1.0'),
                                      Text('浙江舒博特网络科技有限公司 出品'),
                                      Text('官网: http://https://www.zjsbt.cn/service/derivatives'),
                                      ],
                            alignment=MainAxisAlignment.START,
                            width=300,
                            height=100,
                            ),
             # content=Markdown(md_info,
             #                  expand=True),
             actions=[TextButton("确定", on_click=self.on_about_ok_click), ],
             actions_alignment=MainAxisAlignment.END,
             # title_padding=20,
             # on_dismiss=lambda e: print("对话框已关闭!"),
        )

        self.tf_cate = TextField(hint_text='请输入清单名称')
        self.dlg_add_cate = AlertDialog(
            modal=True,
            title=Text('添加清单'),
            content=Column(controls=[self.tf_cate,
                                     ],
                           alignment=MainAxisAlignment.START,
                           width=300,
                           height=100,
                           ),
            actions=[TextButton("确定", on_click=self.on_dlg_add_cate_ok_click),
                     TextButton("取消", on_click=self.on_dlg_add_cate_cancel_click)],
            actions_alignment=MainAxisAlignment.END,
            title_padding=20,
            # on_dismiss=lambda e: print("Modal dialog dismissed!"),
            )

        nav_controls = self.build_interface()
        self.controls = [nav_controls, self.dlg_about, self.dlg_add_cate]

    def on_dashboard_click(self, e):
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        e.control.page.overlay.append(progress_ring)
        e.control.page.update()
        self.page.go('/dashboard')
        progress_ring.visible = False

    def on_list_click(self, e):
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        e.control.page.overlay.append(progress_ring)
        e.control.page.update()

        list_title_text = e.control.title.value.split(' ')[0]
        list_name = 'today'
        match list_title_text:
            case '今天':
                list_name = 'today'
            case '未来七天':
                list_name = 'future'
            case '已过期':
                list_name = 'expired'
        self.page.client_storage.set('list_name', list_name)
        self.page.client_storage.set('list_title', list_title_text)
        self.page.client_storage.set('list_show_finished', False)
        self.page.go(f'/tasklist?id={list_name}')
        progress_ring.visible = False

    def on_about_ok_click(self, e):
        self.dlg_about.open = False
        self.page.update()

    def on_about_click(self, e):
        self.page.dialog = self.dlg_about
        self.dlg_about.open = True
        self.page.update()

    def on_dlg_add_cate_click(self, e):
        self.page.dialog = self.dlg_add_cate
        self.dlg_add_cate.open = True
        self.page.update()

    def on_dark_click(self, e):
        if self.page.theme_mode == 'light':
            self.page.theme_mode = 'dark'
            self.pmi_color.text = '浅色模式'
        else:
            self.page.theme_mode = 'light'
            self.pmi_color.text = '深色模式'
        self.pmi_color.update()
        self.page.update()

    def on_logout(self, e):
        req_result = APIRequest.logout(self.token)
        if req_result is True:
            # self.page.clean()
            # self.page.bgcolor = '#f2f4f8'
            # self.page.vertical_alignment = 'center'
            # self.page.horizontal_alignment = 'center'
            # self.page.update()
            self.page.go('/login')
            return
        self.page.snack_bar = SnackBar(Text("用户退出登录请求失败!"))
        self.page.snack_bar.open = True
        self.page.update()

    def on_cate_click(self, e):
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        e.control.page.overlay.append(progress_ring)
        e.control.page.update()

        cate_id = self.dct_cate.get(e.control.data)
        cate_title = self.dct_cate_title.get(e.control.data)
        self.page.client_storage.set('list_name', cate_id)
        self.page.client_storage.set('list_title', cate_title)
        self.page.client_storage.set('list_show_finished', False)
        self.page.go(f'/tasklist?id={cate_id}')

        progress_ring.visible = False

    def on_list_tile_hover(self, e):
        e.control.bgcolor = Colors.BLACK12 if e.data == "true" else Colors.WHITE
        e.control.update()

    def update_user_info(self):
        dct_ret = APIRequest.query_user_info(self.token)
        self.text_user.value = dct_ret.get('nick_name', '用户名')
        self.img_avatar.src = dct_ret.get('avatar_url', f'/icons/head.png')

    def update_todolist(self):
        dct_ret = APIRequest.query_todolist(self.token)

        todo_data = dct_ret[0].get('todo_data')
        self.lt_today.title = Text(f'今天 {todo_data[1].get("count")}')
        self.lt_week.title = Text(f'未来七天 {todo_data[3].get("count")}')
        self.lt_pass.title = Text(f'已过期 {todo_data[2].get("count")}')
        self.lt_all.title = Text(f'全部 {todo_data[0].get("count")}')

        todo_data = dct_ret[1].get('todo_data')
        self.dct_cate.clear()
        self.dct_cate_title.clear()
        self.col_cate.controls.clear()
        for itm in todo_data:
            lt_cate = ListTile(leading=Icon(Icons.LIST),
                               title=Text(f'{itm.get("name")} {itm.get("count")}'),
                               selected=False,
                               dense=True,
                               data=itm.get('from_id'),
                               on_click=self.on_cate_click)
            ctn_cate = Container(content=lt_cate,
                                 on_hover=self.on_list_tile_hover)
            # self.col_nav.controls.append(lt_cate)
            self.col_cate.controls.append(ctn_cate)
            self.dct_cate[lt_cate.data] = itm.get('from_id')
            self.dct_cate_title[lt_cate.data] = itm.get("name")

        # self.col_nav.height = self.page.window_height

    def on_dlg_add_cate_ok_click(self, e):
        update_status = APIRequest.add_task_list(
            self.token,
            self.tf_cate.value)
        if update_status is False:
            snack_bar = SnackBar(Text("添加清单失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return

        # nav_control = self.page.controls[0].controls[0].content
        # nav_control.update_todolist()
        # nav_control.col_nav.update()
        # nav_control.update()

        self.update_todolist()

        self.dlg_add_cate.open = False
        self.page.update()

    def on_dlg_add_cate_cancel_click(self, e):
        self.dlg_add_cate.open = False
        self.page.update()

    def build_interface(self):
        self.lt_today = ListTile(leading=Icon(Icons.TODAY),
                                 title=Text("今天"),
                                 selected=False,
                                 dense=True,
                                 on_click=self.on_list_click)
        self.lt_week = ListTile(leading=Icon(Icons.CALENDAR_VIEW_WEEK),
                                title=Text("近七天"),
                                selected=False,
                                dense=True,
                                on_click=self.on_list_click)
        self.lt_pass = ListTile(leading=Icon(Icons.HEXAGON_OUTLINED),
                                title=Text("已过期"),
                                selected=False,
                                dense=True,
                                on_click=self.on_list_click)
        self.lt_all = ListTile(leading=Icon(Icons.ALL_INBOX),
                               title=Text("全部"),
                               selected=False,
                               dense=True,
                               on_click=self.on_list_click)

        dct_ret = APIRequest.query_user_info(self.token)
        avatar_url = dct_ret.get('avatar_url', f'/icons/head.png')
        self.img_avatar = Image(src=avatar_url,
                                width=32, height=32,
                                fit=ImageFit.CONTAIN,
                                border_radius=border_radius.all(30))
        # self.img_avatar = CircleAvatar(foreground_image_url=f'/icons/head.png',
        #                                bgcolor=colors.BLACK38,
        #                                radius=5,
        #                                content=Text('头像'))

        self.text_user = Text(dct_ret.get('nick_name', '用户名'), size=14)
        self.pmi_color = PopupMenuItem(icon=Icons.DARK_MODE,
                                       text='深色模式',
                                       on_click=self.on_dark_click)
        self.pmb_option = PopupMenuButton(
            items=[  # self.pmi_color,
                PopupMenuItem(icon=Icons.HELP,
                              text='关于我们',
                              on_click=self.on_about_click),
                # PopupMenuItem(icon=icons.ACCOUNT_BOX, text='账户安全'),
                PopupMenuItem(icon=Icons.LOGOUT,
                              text='退出登录',
                              on_click=self.on_logout),
            ],
            icon=Icons.SETTINGS,
        )
        self.row_head = Row(controls=[self.img_avatar,
                                      self.text_user,
                                      self.pmb_option],
                            alignment=MainAxisAlignment.SPACE_EVENLY,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                            spacing=10)

        # def on_draw_close(e):
        #     self.page.drawer.open = False
        #     self.page.update()

        # btn_show_drawer = IconButton(icon=Icons.MENU,
        #                              on_click=on_draw_close)

        self.col_cate = Column(spacing=1)
        self.col_nav = Column(
            [
                # btn_show_drawer,
                self.row_head,
                Container(content=ListTile(
                    title=Text("仪表盘", weight=FontWeight.BOLD),
                    leading=Icon(Icons.DASHBOARD),
                    on_click=self.on_dashboard_click,
                ),
                    on_hover=self.on_list_tile_hover
                ),
                ListTile(
                    title=Text("列表", weight=FontWeight.BOLD),
                    leading=Icon(Icons.LIST_ALT_SHARP)
                ),
                Container(content=self.lt_today,
                          on_hover=self.on_list_tile_hover,
                          ),
                Container(content=self.lt_week,
                          on_hover=self.on_list_tile_hover),
                Container(content=self.lt_pass,
                          on_hover=self.on_list_tile_hover),
                # self.lt_all,
                ListTile(
                    title=Text("清单", weight=FontWeight.BOLD),
                    leading=Icon(Icons.LIST_ALT)
                ),
                self.col_cate,
                Container(content=ListTile(
                    title=Text('添加清单'),
                    leading=Icon(Icons.ADD),
                    dense=True,
                    on_click=self.on_dlg_add_cate_click,
                ),
                    on_hover=self.on_list_tile_hover
                ),
            ],
            spacing=0,
            expand=True,
            # height=780,
            # alignment='start',
            scroll=ScrollMode.HIDDEN,
        )

        # self.update_user_info()
        self.update_todolist()

        return self.col_nav
