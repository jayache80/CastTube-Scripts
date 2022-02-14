#!/usr/bin/env python

import sys
import threading

import pychromecast
from pychromecast.controllers import BaseController
from pychromecast.error import UnsupportedNamespace

TYPE_GET_SCREEN_ID = "getMdxSessionStatus"
TYPE_STATUS = "mdxSessionStatus"
ATTR_SCREEN_ID = "screenId"
MESSAGE_TYPE = "type"


class ScreenIdController(BaseController):
    def __init__(self):
        super(ScreenIdController, self).__init__("urn:x-cast:com.google.youtube.mdx", "233637DE")
        self.status_update_event = threading.Event()

    def update_screen_id(self):
        """
        Sends a getMdxSessionStatus to get the screenId and waits for response.
        This function is blocking
        If connected we should always get a response
        (send message will launch app if it is not running).
        """
        self.status_update_event.clear()
        # This gets the screenId but always throws. Couldn't find a better way.
        try:
            self.send_message({MESSAGE_TYPE: TYPE_GET_SCREEN_ID})
        except UnsupportedNamespace:
            pass
        self.status_update_event.wait()
        self.status_update_event.clear()

    def receive_message(self, message, data):
        """ Called when a media message is received. """
        if data[MESSAGE_TYPE] == TYPE_STATUS:
            self._process_status(data.get("data"))
            return True

        return False

    def _process_status(self, status):
        """ Process latest status update. """
        print(status.get(ATTR_SCREEN_ID))
        self.status_update_event.set()

def find_chromecast(name):
    """ Find a Chromecast by name. """
    chromecasts = pychromecast.get_chromecasts()

    for chromecast_list in chromecasts:
        try:
            iter(chromecast_list)
        except TypeError:
            continue

        for chromecast in chromecast_list:
            if chromecast.name == name:
                return chromecast

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Provide name of Chromecast device as first and only arg")
        exit(1)

    name = sys.argv[1]
    cast = find_chromecast(name)

    if not cast:
        print(f"Error: could not find Chromecast device named {name}")
        exit(1)

    cast.wait()
    controller = ScreenIdController()
    cast.register_handler(controller)
    controller.update_screen_id()
