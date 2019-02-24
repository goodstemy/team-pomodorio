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
MINUTE_IN_SECONDS = 60
PERIOD_TIME_IN_MINUTES = 25
REST_TIME_IN_MINUTES = 5
LONG_REST_IN_MINUTES = 15
PERIOD_TIME_IN_SECONDS = PERIOD_TIME_IN_MINUTES * MINUTE_IN_SECONDS
REST_TIME_IN_SECONDS = PERIOD_TIME_IN_MINUTES * MINUTE_IN_SECONDS
LONG_REST_IN_SECONDS = LONG_REST_IN_MINUTES * MINUTE_IN_SECONDS
MAX_PERIODS_COUNT = 4

class MainWindow(GridLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.is_started = False
        self.seconds = 0
        self.interval = None
        self.heartbeat_interval = None
        self.periods_count = 0
        self.is_rest = False
        self.is_long_rest = False

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

        remaining_seconds = int(self.seconds % PERIOD_TIME_IN_SECONDS)
        minutes = int(remaining_seconds / 60)
        seconds = int(remaining_seconds % 60)
        periods_without_long_rest = int(self.seconds / (PERIOD_TIME_IN_SECONDS + REST_TIME_IN_SECONDS))
        long_rests_in_seconds = int(periods_without_long_rest / MAX_PERIODS_COUNT) * LONG_REST_IN_SECONDS

        self.periods_count = int((self.seconds - long_rests_in_seconds) / (PERIOD_TIME_IN_SECONDS + REST_TIME_IN_SECONDS))

        is_rest = (self.is_rest and self.is_long_rest)

        if not is_rest and minutes == PERIOD_TIME_IN_MINUTES and self.periods_count % 4 == 0:
            self.is_long_rest = True
            self.seconds = 0
        elif not is_rest and minutes == PERIOD_TIME_IN_MINUTES:
            self.is_rest = True
            self.seconds = 0
        elif is_rest and self.is_rest and not self.is_long_rest and minutes == REST_TIME_IN_MINUTES:
            self.is_rest = False
            self.seconds = 0
        elif is_rest and self.is_long_rest and not self.is_rest and minutes == LONG_REST_IN_MINUTES:
            self.is_long_rest = False
            self.seconds = 0

        # print(periods_without_long_rest)
        # print(long_rests_in_seconds)

        print('total seconds', self.seconds)
        print('periods', self.periods_count)
        print('minutes', minutes)
        print('seconds', seconds)
        print('is rest', self.is_rest)
        print('is long rest', self.is_long_rest)

        # if self.seconds >= 1500:
        #     self.seconds = 0
        #     self.is_rest = True

        # if self.seconds >= 300 and self.is_rest == True:
        #     self.seconds = 0
        #     self.periods_count += 1
        #     self.is_rest = False

        self.display_time()

    def display_time(self):
        if self.seconds == 0:
            self.timer_label.text = '00:00'
            return

        minutes = int(self.seconds / 60)
        seconds = self.seconds % 60

        if len(str(seconds)) == 1:
            seconds = '0{}'.format(seconds)

        if len(str(minutes)) == 1:
            minutes = '0{}'.format(minutes)

        self.timer_label.text = '{}:{}'.format(minutes, seconds)

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
