#!/usr/bin/env python3

import collections
import subprocess

import requests
import zign.api

precision = {'ms': 0, '%': 2}


def plot(base_url, product, slo_id, output_file):
    url = '{}/service-level-objectives/{}'.format(base_url, product)
    resp = requests.get(url, headers={'Authorization': 'Bearer {}'.format(zign.api.get_token('zmon', ['uid']))})
    resp.raise_for_status()
    slos = resp.json()
    targets = []
    for slo in slos:
        if str(slo['id']) == str(slo_id):
            for target in slo['targets']:
                targets.append(target)

    for i, target in enumerate(targets):
        fn = '/tmp/data{}.tsv'.format(i)
        target['fn'] = fn
        url = '{}/service-level-indicators/{}/{}'.format(base_url, product, target['sli_name'])
        resp = requests.get(url, headers={'Authorization': 'Bearer {}'.format(zign.api.get_token('zmon', ['uid']))})
        resp.raise_for_status()

        with open(fn, 'w') as fd:
            data = resp.json()
            values = [row[1] for row in data]
            maxval = max(values)
            minval = min(values)
            for row in data:
                fd.write('{}\t{}\n'.format(row[0], row[1]))

    plot = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)

    gnuplot_data = '''
    set output '{}'
    set term png enhanced size 1100, 400
    set xdata time
    set samples 300
    set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
    set format x "%m-%d"
    set timefmt "%Y-%m-%dT%H:%M:%SZ"
    '''.format(output_file)

    targets_by_unit = collections.defaultdict(list)
    for target in targets:
        targets_by_unit[target['unit']].append(target)

    i = 0
    for unit, _targets in reversed(sorted(targets_by_unit.items())):
        if unit:
            if i == 0:
                suff = ''
            else:
                suff = '2'
            gnuplot_data += 'set format y{} "%.{}f {}"\n'.format(suff, precision.get(unit, 0), unit.replace('%', '%%'))

            from_list = [t['from'] for t in _targets if t['from'] is not None] or [0]
            to_list = [t['to'] for t in _targets if t['to'] is not None] or [0]

            ymin, ymax = (min(from_list + [minval]), max(to_list + [maxval]))

            if ymin is not None:
                ymin = ymin - (0.2 * abs(ymin))
            if ymax is not None:
                ymax = ymax + (0.2 * abs(ymax))
            gnuplot_data += 'set y{}range [{}:{}]\n'.format(suff, ymin or '', ymax or '')
            gnuplot_data += 'set y{}tics\n'.format(suff)
            for target in _targets:
                target['yaxis'] = 'y1' if i == 0 else 'y2'
                coord = 'first' if i == 0 else 'second'
                if target['from']:
                    gnuplot_data += (
                        'set arrow from graph 0,{} {} to graph 1, {} {} head linecolor rgb "#ffcece" linewidth 2\n'
                    ).format(coord, target['from'], coord, target['from'])
                if target['to']:
                    gnuplot_data += (
                        'set arrow from graph 0,{} {} to graph 1, {} {} backhead linecolor rgb "#ffcece" linewidth 2\n'
                    ).format(coord, target['to'], coord, target['to'])
            i += 1

    gnuplot_data += 'plot '
    plots = []
    for target in sorted(targets, key=lambda t: t['unit']):
        if target['unit']:
            plots.append('"{}" using 1:2 lw 2 smooth csplines axes x1{} with lines title "{}"'.format(
                target['fn'], target['yaxis'], target['sli_name'].replace('_', ' ')))
    gnuplot_data += ', '.join(plots) + '\n'
    plot.communicate(gnuplot_data.encode('utf-8'))
