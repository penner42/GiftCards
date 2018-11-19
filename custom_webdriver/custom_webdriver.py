from selenium import webdriver


class CustomWebDriver(webdriver.Chrome):
    _toggle_browser = False

    def toggle(self):
        self._toggle_browser = not self._toggle_browser

    def _do_toggle(self):
        if self._toggle_browser:
            x = self.get_window_position()['x']
            if x == -10000:
                self.set_window_position(10,10)
            else:
                self.set_window_position(-10000, 0)
        self._toggle_browser = False

    def find_element_by_xpath(self, xpath):
        self._do_toggle()
        return super(CustomWebDriver, self).find_element_by_xpath(xpath)

    def find_element_by_id(self, id_):
        self._do_toggle()
        return super(CustomWebDriver, self).find_element_by_id(id_)

    def find_element_by_class_name(self, name):
        self._do_toggle()
        return super(CustomWebDriver, self).find_element_by_class_name(name)

    def find_element_by_name(self, name):
        self._do_toggle()
        return super(CustomWebDriver, self).find_element_by_name(name)

    def find_element_by_partial_link_text(self, link_text):
        self._do_toggle()
        return super(CustomWebDriver, self).find_element_by_partial_link_text(link_text)

    def save_screenshot(self, filename):
        self._do_toggle()
        return super(CustomWebDriver, self).save_screenshot(filename)

    def execute_script(self, script, *args):
        self._do_toggle()
        return super(CustomWebDriver, self).execute_script(script, *args)

    def get(self, url):
        self._do_toggle()
        return super(CustomWebDriver, self).get(url)
