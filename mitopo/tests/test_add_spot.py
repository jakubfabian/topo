from utils import MitopoTestCase


class AddSpotTest(MitopoTestCase):

    def test_need_login_for_add_spot(self):

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

        spot_button = self.ensure_present("#add_spot_button")
        spot_button.click()



        #login_button = self.ensure_present("#login_button")
        #login_button.click()

        username_input = self.ensure_present("input#id_username")
        username_input.send_keys("root")

        password_input = self.ensure_present("input#id_password")
        password_input.send_keys("root")

        submit_login = self.ensure_present("input#submit_login")
        submit_login.click()

        # THEN the user should be logged in (name instead of loginbutton visible)
        # AND after logout should be back to the start page

        header = self.ensure_present(".inner_container h1")
        self.assertEqual(header.text, "Add new Spot")

        markers_before = self.browser.find_elements_by_css_selector("img.leaflet-marker-icon")

        zoom_out = self.ensure_present(".leaflet-control-zoom-out")

        from selenium import webdriver
        action = webdriver.common.action_chains.ActionChains(self.browser)
        action.move_by_offset(zoom_out.location['x'] + 100, zoom_out.location['y'])
        action.click()
        action.perform()

        markers = self.browser.find_elements_by_css_selector("img.leaflet-marker-icon")

        self.assertEqual(len(markers), len(markers_before)+1, "Marker_count should be exactly one more or we could not put a new marker on the map markercount: (after_add={0:} before_add={1:})".format(len(markers), len(markers_before)))

        import random
        rand_name = "testspot_%08x" % random.getrandbits(32)

        spot_name_input = self.ensure_present("input#id_name")
        spot_name_input.send_keys(rand_name)

        submit_button = self.ensure_present(".mapobjects-info form input[type=submit]")
        submit_button.click()

        # Find newly created spot in all spots list
        spot_label = self.browser.find_element_by_xpath("//*[contains(@class, 'spot_entry') and text()='{0:}']".format(rand_name))
        

if __name__ == "__main__":
    import unittest
    unittest.main()
