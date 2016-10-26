import ConfigParser
import json
import time

from pygerrit import client
from pygerrit import events


class Listener(object):

    def __init__(self, gerrit_user):
        self.gerrit_user = gerrit_user

    def start_listening(self):
        self.gerrit = client.GerritClient(
            host='review.openstack.org',
            username=self.gerrit_user,
            port=29418
        )
        print self.gerrit.gerrit_version()

    def write_event(self, event):
        print event
        path = '/tmp/perf/'
        fname = (path + event.change.number + '-' +
                 event.patchset.number + '.json')
        with open(fname, 'w') as f:
            f.write(json.dumps(event.json))

    def listen_for_events(self):
        self.gerrit.start_event_stream()
        while True:
            event = self.gerrit.get_event()
            if event:
                if isinstance(event, events.CommentAddedEvent):
                    if event.change.project == 'openstack/keystone':
                        if 'check performance' in event.comment:
                            self.write_event(event)
                if isinstance(event, events.ChangeMergedEvent):
                    if event.change.project == 'openstack/keystone':
                        self.write_event(event)
            else:
                time.sleep(1)

if __name__ == '__main__':
    config_parser = ConfigParser.ConfigParser()
    config_parser.read('performance.conf')
    gerrit_user = config_parser.get('global', 'gerrit_user')

    listener = Listener(gerrit_user)
    listener.start_listening()
    listener.listen_for_events()
