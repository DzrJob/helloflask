from flask import Blueprint
# 当前文件夹初始化为蓝本（app）main
main = Blueprint('main',__name__)
# 当前文件夹下导入views，errors
from . import views, errors
