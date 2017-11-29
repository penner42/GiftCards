from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock

class InputWindow(BoxLayout):

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

        if (t1[-4:] == t2[-4:]) and (t1[-4:] != "0000"):
            cardno = sec1[0]+sec3[12:14]+sec1[6:15]+sec3[14:18]
        else:
            cardno = sec1[0:20]

        return ' '.join(cardno[i:i+4] for i in range(0,len(cardno), 4))

class SwiperApp(App):
    def build(self):
        return InputWindow()

SwiperApp().run()
