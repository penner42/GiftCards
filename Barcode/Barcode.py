from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import re

class Barcode(BoxLayout):
    def focus_pin_inputfield(self, dt):
        self.ids.pin_inputfield.focus = True

    def focus_code_inputfield(self, dt):
        self.ids.code_inputfield.focus = True

    def selected(self):
        Clock.schedule_once(self.focus_pin_inputfield, -1)

    def detect(self, pin, code):
        # kohl's. others?
        code = code.replace('%B', '')

        if len(code) == 30:
            code = code[-19:]
        # cabela's
        elif re.search("^\d{10}[a-zA-Z]{6}$", code):

            pin = code[-6:]
            code = code[:9]
        elif len(code) != 19 and len(code) != 16:
            self.ids.code_inputfield.text = ''
            Clock.schedule_once(self.focus_code_inputfield, -1)
            return

        self.children[0].ids.csv_output.text += ' '.join(code[i:i+4] for i in range(0,len(code), 4)) + "," \
                                    + pin + "\r\n"
        self.ids.pin_inputfield.text = ''
        self.ids.code_inputfield.text = ''
        Clock.schedule_once(self.focus_pin_inputfield, -1)

    def pin_inputfield_entered(self):
        if "%B" in self.ids.pin_inputfield.text:
            # pin + code in one field
            pin, code = self.ids.pin_inputfield.text.split('%B')
            self.detect(pin, code)
        else:
            Clock.schedule_once(self.focus_code_inputfield, -1)

    def code_inputfield_entered(self):
        self.detect(self.ids.pin_inputfield.text, self.ids.code_inputfield.text)
