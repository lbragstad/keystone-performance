import json
import os

from lxml import html
from lxml.html import builder as E


def main():
    results = os.walk('../results/')
    for result_dir in results:
        import ipdb
        ipdb.set_trace()


if __name__ == '__main__':
    main()
