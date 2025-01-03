from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):
    def setUp(self):
        # 这个数会在个 test function 执⾏的时候被执⾏
        self.client = APIClient()
        self.user = self.createUser(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )
    def createUser(self, username, email, password):
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进⾏⼀些 normalize 处理
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # 个测试数必须以 test_ 开头，才会被⾃动调⽤进⾏测试
        # 测试必须⽤ post ⽽不是 get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 登失败，http status code 回 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)
        # ⽤了 post 但是密码错了
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)
        # 验证还没有登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # ⽤正确的密码
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')
        # 验证已经登录了
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # 先登录
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 验证⽤户已经登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
        # 测试必须⽤ post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)
        # 改⽤ post 成功 logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # 验证⽤户已经登出
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # 测试 get 请求失败
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)
        # 测试错误的邮箱
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        # 测试密码太
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        # 测试⽤户名太
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        # 成功注册
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # 验证⽤户已经登⼊
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)