import kivy

kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

class MainWindow(GridLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.is_started = False
        self.seconds = 0
        self.interval = None

        self.cols = 1
        self.timer_label = Label(text='00:00')
        self.button = Button(text='Start', on_press=self.click_callback)

        self.add_widget(self.timer_label)
        self.add_widget(self.button)

    def click_callback(self, instance):
        if self.is_started:
            self.is_started = not self.is_started
            self.stop_timer()
        else:
            self.is_started = not self.is_started
            self.start_timer()

    def start_timer(self):
        print('started')
        self.interval = Clock.schedule_interval(self.tick, 1)
        self.button.text = 'Stop'

    def stop_timer(self):
        print('stoped')
        self.interval.cancel()
        self.timer_label.text = '00:00' 
        self.button.text = 'Start'

    def tick(self, dt):
        self.seconds += 1
        if len(str(self.seconds)) == 2:
            self.timer_label.text = "00:{}".format(self.seconds)
        else:
            self.timer_label.text = "00:0{}".format(self.seconds)

class PomodoroApp(App):
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    PomodoroApp().run()
