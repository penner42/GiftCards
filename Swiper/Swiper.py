from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.clipboard import Clipboard
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
import os

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def get_path(self):
        return os.path.expanduser("~")

class InputWindow(TabbedPanel):
    pass

class Swipe(BoxLayout):
    def focus_inputfield(self, dt):
        self.ids.inputfield.focus = True

    def inputfield_entered(self):
        # card not swiped
        if "%B" not in self.ids.inputfield.text:
            Clock.schedule_once(self.focus_inputfield, -1)
        else:
            pin, data = self.ids.inputfield.text.split("%B")
            self.card_swiped(pin, data)

    def card_swiped(self, pin, data):
        if data.count('?') != 2:
            self.ids.inputfield.text = pin
            Clock.schedule_once(self.focus_inputfield, -1)
        else:
            card_no = self.detect(data)
            self.ids.csv_output.text += card_no + "," + pin + "\r\n"
            self.ids.inputfield.text = ""
            Clock.schedule_once(self.focus_inputfield, -1)

    def clear_release(self, value):
        if value == "normal":
            self.ids.csv_output.text = ""
            Clock.schedule_once(self.focus_inputfield, -1)

    def copy_output(self, value):
        if value == "normal":
            Clipboard.copy(self.ids.csv_output.text)

    def detect(self, data):
        sec1, sec2, sec3 = data.split('^')
        [t1,t2,t3] = [x.strip() for x in data.split('?')]

        # if (t1[-4:] == t2[-4:]) and (t1[-4:] != "0000"):
        if len(sec1) != 19:
            cardno = sec1[0]+sec3[14:16]+sec1[6:15]+sec3[16:20]
        else:
            cardno = sec1[0:20]

        return ' '.join(cardno[i:i+4] for i in range(0,len(cardno), 4))

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.ids.csv_output.text)

        self.dismiss_popup()

class Barcode(BoxLayout):
    def focus_pin_inputfield(self, dt):
        self.ids.pin_inputfield.focus = True

    def focus_code_inputfield(self, dt):
        self.ids.code_inputfield.focus = True

    def pin_inputfield_entered(self):
        Clock.schedule_once(self.focus_code_inputfield, -1)

    def code_inputfield_entered(self):
        code = self.ids.code_inputfield.text
        # kohl's. others?
        if len(code) == 30:
            code = code[-19:]
        elif len(code) != 19 and len(code) != 16:
            self.ids.code_inputfield.text = ''
            Clock.schedule_once(self.focus_code_inputfield, -1)
            return

        self.ids.csv_output.text += ' '.join(code[i:i+4] for i in range(0,len(code), 4)) + "," \
                                    + self.ids.pin_inputfield.text + "\r\n"
        self.ids.pin_inputfield.text = ''
        self.ids.code_inputfield.text = ''
        Clock.schedule_once(self.focus_pin_inputfield, -1)

    def clear_release(self, value):
        if value == "normal":
            self.ids.csv_output.text = ""
            Clock.schedule_once(self.focus_pin_inputfield, -1)

    def copy_output(self, value):
        if value == "normal":
            Clipboard.copy(self.ids.csv_output.text)


class SwiperApp(App):
    def build(self):
        inp = InputWindow()
        th = TabbedPanelHeader(text='Swipe')
        th.content = Swipe()
        inp.add_widget(th)
        th = TabbedPanelHeader(text='Barcode')
        th.content = Barcode()
        inp.add_widget(th)
        return inp

SwiperApp().run()
