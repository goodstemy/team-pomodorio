import kivy
import os
import urllib
import json

kivy.require('1.0.7')

from dotenv import load_dotenv
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.uix.textinput import TextInput

load_dotenv()

TEAM_POMODORO_URI = os.getenv('TEAM_POMODORO_URI')

class MainWindow(GridLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.is_started = False
        self.seconds = 0
        self.interval = None
        self.heartbeat_interval = None
        self.periods_count = 0
        self.is_rest = False

        self.cols = 1
        self.timer_label = Label(text='00:00')
        self.input = TextInput(text='Connect or create a team', multiline=False, on_text_validate=self.execute_connect)

        self.add_widget(self.input)
        self.add_widget(self.timer_label)

    def start_timer(self, seconds):
        print('started')
        self.seconds = seconds
        if self.interval:
            self.interval.cancel()
        self.interval = Clock.schedule_interval(self.tick, 1)
        self.is_started = True

    def stop_timer(self):
        print('stoped')
        self.interval.cancel()
        self.timer_label.text = '00:00' 
        self.is_started = False

    def tick(self, dt):
        self.seconds += 1

        if self.seconds >= 1500:
            self.seconds = 0
            self.is_rest = True

        if self.seconds >= 300 and self.is_rest == True:
            self.seconds = 0
            self.periods_count += 1
            self.is_rest = False

        self.display_time()

    def display_time(self):
        minutes = int(self.seconds / 60)
        seconds = self.seconds % 60

        if len(str(seconds)) == 1:
            seconds = "0{}".format(seconds)

        if len(str(minutes)) == 1:
            minutes = "0{}".format(minutes)

        self.timer_label.text = "{}:{}".format(minutes, seconds)

    def execute_connect(self, instance):
        params = urllib.parse.urlencode({'name': instance.text})
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        req = UrlRequest(TEAM_POMODORO_URI, on_success=self.successed_request, on_failure=self.failure_request, req_body=params, req_headers=headers)

    def successed_request(self, req, result):
        time = json.loads(result)
        seconds = int(time['seconds'])
        if seconds > 0:
            self.start_timer(seconds)
            print('you are connected')
        else:
            self.start_timer(0)
            print('you are create new room')


    def failure_request(self, req, error):
        print(error)

class PomodoroApp(App):
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    PomodoroApp().run()
