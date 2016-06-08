import argparse
import json
import time

from pygerrit import client
from pygerrit import events


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process event stream from Gerrit.')
    parser.add_argument('-u', '--username', dest='username',
                        help='username', required=True)
    options = parser.parse_args()

    gerrit = client.GerritClient(host='review.openstack.org',
                                 username=options.username,
                                 port=29418)
    print gerrit.gerrit_version()
    gerrit.start_event_stream()
    try:
        while True:
            event = gerrit.get_event()
            if isinstance(event, events.CommentAddedEvent):
                if event.change.project == 'openstack/keystone':
                    if 'check performance' in event.comment:
                        print event
                        # we have a patch set to test - write it to disk!
                        path = '/tmp/perf/'
                        fname = (path + event.change.number + '-' +
                                 event.patchset.number + '.json')
                        with open(fname, 'w') as f:
                            f.write(json.dumps(event.json))
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        gerrit.stop_event_stream()
