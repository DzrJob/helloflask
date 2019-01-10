# 密码散列化测试
import unittest

from app.models import User


class UserModelTestCase(unittest.TestCase):
    # 测试密码是否正确设置
    def test_password_setter(self):
        u =  User(password = 'cat')
        self.assertTrue(u.password_hash is not None)
    # 测试不可读
    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password
    # 测试加密密码与密码对比
    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
    # 测试密码随机
    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)
