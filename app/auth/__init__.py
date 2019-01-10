from flask import Blueprint
# 使当前文件夹 创建蓝本（app）auth
auth = Blueprint('auth',__name__)
# 当前文件夹导入views模块
from . import views
