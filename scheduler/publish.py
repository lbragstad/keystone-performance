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
CHANGE_LINK = (
    'https://github.com/openstack/keystone/commit/'
)


def CLASS(v):
    # helper function, 'class' is a reserved word
    return {'class': v}


def main():
    results = os.walk('../results/')
    summary_files = list()
    for result in results:
        if 'summary.json' in result[2]:
            summary_files.append(os.path.join(result[0], 'summary.json'))

    data = {}
    for file_path in summary_files:
        with open(file_path, 'r') as f:
            contents = json.loads(f.read())
            contents['directory'] = os.path.dirname(file_path)
            data[contents['timestamp']] = contents

    latest = data[sorted(data.keys(), reverse=True)[0]]
    date = datetime.datetime.fromtimestamp(
        latest['timestamp']
    ).strftime('%Y-%M-%d-%H:%M:%S')

    token_create_rps = latest['token_creation']['requests_per_second']
    token_create_tps = latest['token_creation']['time_per_request']
    token_validate_rps = latest['token_validation']['requests_per_second']
    token_validate_tps = latest['token_validation']['time_per_request']

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
                    'SHA: ',
                    e.A(
                        latest['sha'],
                        target='_blank',
                        href=CHANGE_LINK + latest['sha']
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

    with open(os.path.join(latest['directory'], 'index.html'), 'w') as f:
        f.write(et.tostring(index))


if __name__ == '__main__':
    main()
