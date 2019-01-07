# 导入蓝本
from flask import Blueprint

main = Blueprint('main',__name__)
# 当前目录下导入views，errors
from . import views, errors
