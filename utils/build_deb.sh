fpm -s dir -t deb -n booltodo -v 2.2.1 --description "BoolHub Todo App." \
	--maintainer "Hunter Zhang <riverbird@aliyun.com>" \
	--architecture amd64 \
	-C /home/riverbird/project/shuqu-todo/build/linux \
	.=usr/local/bool-todo \
	bool-todo.desktop=/usr/share/applications/bool-todo.desktop
