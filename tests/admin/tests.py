from django.test import LiveServerTestCase
from selenium import webdriver

class SeleniumAdminTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(SeleniumAdminTests, cls).setUpClass()
        cls.selenium = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumAdminTests, cls).tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('admin123')
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()