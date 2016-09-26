from utils import MitopoTestCase


class LoginLogoutTest(MitopoTestCase):

    def test_login_logout(self):

        # uncomment this to add an artifical slow down of X milliseconds to every call
        # of self.ensure_present or self.ensure_absent. You can also put additional slow
        # downs in the code by using self.try_slow_down() at the locations where you want
        # to add waits.
        #
        # The idea is to make it easier for humans to observe the selenium interactions
        # during test development. When you finished developing the test comment it out
        # so the test runs with maximum speed.
        #
        self.slow_down = 1000

        # GIVEN is the start page of the application with login and register buttons
        #       present

        self.browser.get('http://localhost:8000')

        self.ensure_present("#register_button")
        self.ensure_absent("span.loginname")
        self.ensure_absent("#logout_button")

        # WHEN the loginbutton is clicked
        # AND the user credentials are input and submitted

        login_button = self.ensure_present("#login_button")
        login_button.click()

        username_input = self.ensure_present("input#id_username")
        username_input.send_keys("root")

        password_input = self.ensure_present("input#id_password")
        password_input.send_keys("root")

        submit_login = self.ensure_present("input#submit_login")
        submit_login.click()

        # THEN the user should be logged in (name instead of loginbutton visible)
        # AND after logout should be back to the start page

        self.ensure_absent("#login_button")

        span_loginname = self.ensure_present("span.loginname")
        self.assertEqual(span_loginname.text, "User: root <myemail@example.com>")

        logout_button = self.ensure_present("#logout_button")
        logout_button.click()

        self.ensure_present("#login_button")
        self.ensure_present("#register_button")
        self.ensure_absent("span.loginname")
        self.ensure_absent("#logout_button")

if __name__ == "__main__":
    import unittest
    unittest.main()
