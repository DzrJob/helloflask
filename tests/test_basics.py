import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    # 测试前执行（创建一个测试环境）
    def setUp(self):
        # 创建测试app
        self.app = create_app('testing')
        # 程序实例上调用 app.app_context() 可获得一个程序上下文
        self.app_context = self.app.app_context()
        # 推送上下文
        self.app_context.push()
        # 创建数据库
        db.create_all()

    # 测试后执行（删除上下文和数据库）
    def tearDown(self):
        # 删除session中的内容
        db.session.remove()
        # 销毁数据库
        db.drop_all()
        # 删除程序上下文
        self.app_context.pop()

    # test_ 开头的函数都作为测试执行。
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
