# scheduler

The scheduler consists of two separate processes. The first listens to the
Gerrit event stream from `review.openstack.org`. If any events come through for
the `openstack/keystone` project with the keywords `check performance` in a
comment, the listener will pull metadata about the change and persist it as
JSON to a file in `/tmp/perf/`. The second process is a scheduler that will
read files from `/tmp/perf/`, pull out needed information, and start
orchestrating a deployment for specific patches on a bare metal host using LXD
containers.
