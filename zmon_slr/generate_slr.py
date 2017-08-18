#!/usr/bin/env python3

import datetime
import os

import jinja2

from collections import defaultdict

from zmon_slr.client import Client

from zmon_slr.plot import plot


AGGS_MAP = {
    'average': 'avg',
    'weighted': 'avg',
    'sum': 'sum',
    'minimum': 'min',
    'min': 'min',
    'maximum': 'max',
    'max': 'max',
}


def title(s):
    return s.title().replace('_', ' ').replace('.', ' ')


def human_time(minutes):
    days = minutes // (60 * 24)
    remainder = minutes % (60 * 24)
    hours = remainder // 60
    minutes = remainder % 60
    s = []

    if days:
        s.append('{} day(s)'.format(days))
    if hours:
        s.append('{} hour(s)'.format(hours))
    if minutes:
        s.append('{} minute(s)'.format(minutes))

    return ' '.join(s)


def generate_directory_index(output_dir, path='/'):
    dirs = []
    reverse = False
    for entry in sorted(os.listdir(output_dir)):
        if '.' not in entry:
            entry.split()
            if not entry.startswith('20'):
                # leaf directory with actual report
                generate_directory_index(os.path.join(output_dir, entry), os.path.join(path, entry))
                dirs.append((entry, entry))
            else:
                from_date, to_date = entry.split('-')
                start = datetime.datetime.strptime(from_date, '%Y%m%d')
                end = datetime.datetime.strptime(to_date, '%Y%m%d')
                dirs.append(('{} - {}'.format(start.strftime('%A, %d %B %Y'), end.strftime('%A, %d %B %Y')), entry))
                reverse = True

    if reverse:
        dirs.reverse()
    data = {'path': path, 'dirs': dirs}

    loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = jinja2.Environment(loader=loader)
    template = env.get_template('directory_index.html')
    template.stream(**data).dump(os.path.join(output_dir, 'index.html'))


def generate_weekly_report(client: Client, product: dict, output_dir: str) -> None:
    report_data = client.product_report(product)

    product_group = report_data['product_group_slug']

    period_from = period_to = None
    for slo in report_data['slo']:
        if slo['days']:
            period_from = min(slo['days'].keys())[:10]
            period_to = max(slo['days'].keys())[:10]
            break

    if not period_from or not period_to:
        raise RuntimeError('Can not determine "period_from" and "period_to" for the report. Aborting!')

    period_id = '{}-{}'.format(period_from.replace('-', ''), period_to.replace('-', ''))

    report_dir = os.path.join(output_dir, product_group, product['slug'], period_id)
    os.makedirs(report_dir, exist_ok=True)

    loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = jinja2.Environment(loader=loader)

    data = {
        'product': {
            'name': report_data['product_name'],
            'product_group_name': report_data['product_group_name'],
        },
        'period': '{} - {}'.format(period_from, period_to),
        'slos': []
    }

    for slo in report_data['slo']:
        slo['slis'] = {}
        slo['data'] = []

        breaches_by_sli = defaultdict(int)
        counts_by_sli = defaultdict(int)
        values_by_sli = defaultdict(lambda: defaultdict(list))

        for day, day_data in sorted(slo['days'].items()):
            slis = {}

            for sli, sli_data in day_data.items():
                breaches_by_sli[sli] += sli_data['breaches']
                counts_by_sli[sli] += sli_data['count']

                values_by_sli[sli]['avg'].append(sli_data['avg'])
                values_by_sli[sli]['min'].append(sli_data['min'])
                values_by_sli[sli]['max'].append(sli_data['max'])
                values_by_sli[sli]['sum'].append(sli_data['sum'])

                classes = set()
                unit = ''

                if sli_data['breaches']:
                    classes.add('orange')

                for target in slo['targets']:
                    sli_name = target['sli_name']

                    if sli_name == sli:
                        unit = target['unit']
                        if target['to'] and sli_data['avg'] > target['to']:
                            classes.add('red')
                        elif target['from'] and sli_data['avg'] < target['from']:
                            classes.add('red')

                if not classes:
                    classes.add('ok')

                if sli_data['count'] < 1400:
                    classes.add('not-enough-samples')

                if sli == 'requests':
                    # interpolate total number of requests per day from average per sec
                    sli_data['total'] = int(sli_data['avg'] * sli_data['count'] * 60)

                slis[sli] = sli_data
                slis[sli]['unit'] = unit
                slis[sli]['classes'] = classes

            dt = datetime.datetime.strptime(day[:10], '%Y-%m-%d')
            dow = dt.strftime('%a')

            slo['data'].append({'caption': '{} {}'.format(dow, day[5:10]), 'slis': slis})

        slo['breaches'] = max(breaches_by_sli.values())
        slo['count'] = max(counts_by_sli.values())

        for target in slo['targets']:
            sli_name = target['sli_name']
            aggregation = target['aggregation']

            val = None

            slo['slis'][sli_name] = {
                'unit': target['unit'],
            }

            if aggregation in ('average', 'weighted'):
                values = values_by_sli[sli_name]['avg']
                val = sum(values) / len(values) if len(values) > 0 else None
            elif aggregation in ('max', 'maximum'):
                values = values_by_sli[sli_name]['max']
                val = max(values) if len(values) > 0 else None
            elif aggregation in ('min', 'minimum'):
                values = values_by_sli[sli_name]['min']
                val = min(values) if len(values) > 0 else None
            elif aggregation == 'sum':
                values = values_by_sli[sli_name]['sum']
                val = sum(values) if len(values) > 0 else None

            ok = True
            if val is not None and target['to'] and val > target['to']:
                ok = False
            if val is not None and target['from'] and val < target['from']:
                ok = False

            slo['slis'][sli_name]['aggregate'] = '-' if val is None else '{:.2f} {}'.format(val, target['unit'])
            slo['slis'][sli_name]['ok'] = ok

        fn = os.path.join(report_dir, 'chart-{}.png'.format(slo['id']))

        plot(client, product, slo['id'], fn)

        slo['chart'] = os.path.basename(fn)
        data['slos'].append(slo)

    data['now'] = datetime.datetime.utcnow()

    env.filters['sli_title'] = title
    env.filters['human_time'] = human_time

    template = env.get_template('slr-weekly.html')
    template.stream(**data).dump(os.path.join(report_dir, 'index.html'))

    generate_directory_index(output_dir)
