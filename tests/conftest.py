import collections

import pytest


class Device:
    def __init__(self):
        self.basic_status = type('basic_status', (), {'on': 'On'})
        self.volume = -50
        self.mute = False
        self.input = 'HDMI1'

    @property
    def on(self):
        return self.basic_status.on == 'On'

    @on.setter
    def on(self, value):
        self.basic_status.on = "On" if value else "Standby"
        return value


@pytest.fixture()
def device():
    return Device()

