import argparse
import datetime
import json
import os

from lxml import etree as et
from lxml.html import builder as e


PERF_LINK = (
    'https://github.com/lbragstad/keystone-performance/tree/master/results'
)
BOT_LINK = (
    'https://github.com/lbragstad/keystone-performance'
)
KEYSTONE_LINK = (
    'https://github.com/openstack/keystone/commit/'
)
OSA_LINK = (
    'https://github.com/openstack/openstack-ansible-os_keystone/commit/'
)


def CLASS(v):
    # helper function, 'class' is a reserved word
    return {'class': v}


def main(results_file):
    summary = {}
    with open(results_file, 'r') as f:
        summary = json.loads(f.read())
        summary['directory'] = os.path.dirname(results_file)

    date = datetime.datetime.fromtimestamp(
        summary['timestamp']
    ).strftime('%Y-%M-%d-%H:%M:%S')

    token_create_rps = summary['token_creation']['requests_per_second']
    token_create_tps = summary['token_creation']['time_per_request']
    token_validate_rps = summary['token_validation']['requests_per_second']
    token_validate_tps = summary['token_validation']['time_per_request']

    index = e.HTML(
        e.HEAD(
            e.LINK(rel='stylesheet', type='text/css', href='theme.css'),
            e.TITLE('OpenStack Keystone Performance')
        ),
        e.BODY(
            e.DIV(
                e.H1('OpenStack Keystone Performance'),
                e.P(
                    'Published reports after each merged patch.',
                    CLASS('subtitle')
                ),
                id='header'
            ),
            e.DIV(
                e.P(
                    'Last run date: ' + date,
                ),
                e.P(
                    'keystone SHA: ',
                    e.A(
                        summary['sha'],
                        target='_blank',
                        href=KEYSTONE_LINK + summary['sha']
                    )
                ),
                e.P(
                    'os_keystone SHA: ',
                    e.A(
                        summary['osa_sha'],
                        target='_blank',
                        href=OSA_LINK + summary['osa_sha']
                    )
                ),
                e.P(
                    e.A('Performance Data', href=PERF_LINK, target='_blank')
                ),
                e.DIV(
                    CLASS('left'),
                    e.H2('Create Token'),
                    e.P(e.STRONG(token_create_rps), ' requests per second'),
                    e.P(e.STRONG(token_create_tps), ' ms per request')
                ),
                e.DIV(
                    CLASS('right'),
                    e.H2('Validate Token'),
                    e.P(e.STRONG(token_validate_rps), ' requests per second'),
                    e.P(e.STRONG(token_validate_tps), ' ms per request')
                ),
                id='content'
            ),
            e.DIV(
                e.P(
                    'Results provided by the ',
                    e.A(
                        'OSIC Performance Bot',
                        target='_blank',
                        href=BOT_LINK
                    )
                ),
                id='footer'
            )
        )
    )

    with open(os.path.join(summary['directory'], 'index.html'), 'w') as f:
        f.write(et.tostring(index))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='specific results file to process')
    args = parser.parse_args()

    main(args.file)
