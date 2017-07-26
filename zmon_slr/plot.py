#!/usr/bin/env python3

import collections
import subprocess

from zmon_slr.client import Client

precision = {'ms': 0, '%': 2}


def plot(client: Client, product: dict, slo_id: int, output_file):
    slos = client.slo_list(product, id=slo_id)
    slo = slos[0]

    targets = client.target_list(slo)

    targets_by_unit = collections.defaultdict(list)

    for i, target in enumerate(targets):
        fn = '/tmp/data{}.tsv'.format(i)
        target['fn'] = fn

        sli_name = target['sli_name']
        slis = client.sli_list(product, name=sli_name)
        sli = slis[0]

        data = client.sli_values(sli, sli_from=10080)

        target['unit'] = sli['unit']
        targets_by_unit[sli['unit']].append(target)

        with open(fn, 'w') as fd:
            values = [row['value'] for row in data]
            maxval = max(values)
            minval = min(values)
            for row in data:
                fd.write('{}\t{}\n'.format(row['timestamp'], row['value']))

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

    i = 0
    for unit, _targets in reversed(sorted(targets_by_unit.items())):
        if unit:
            if i == 0:
                suff = ''
            else:
                suff = '2'
            gnuplot_data += 'set format y{} "%.{}f {}"\n'.format(suff, precision.get(unit, 0), unit.replace('%', '%%'))

            from_list = [t['from'] for t in _targets if t['from'] is not None and t['from'] != float('-inf')] or [0]
            to_list = [t['to'] for t in _targets if t['to'] is not None and t['to'] != float('inf')] or [0]

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

                if target['from'] and target['from'] != float('-inf'):
                    gnuplot_data += (
                        'set arrow from graph 0,{} {} to graph 1, {} {} head linecolor rgb "#ffcece" linewidth 2\n'
                    ).format(coord, target['from'], coord, target['from'])
                if target['to'] and target['to'] != float('inf'):
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
