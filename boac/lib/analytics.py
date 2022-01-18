"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


import math
from statistics import mean


def mean_metrics_across_sites(canvas_sites, key):
    """Mimic Data Loch's term-wide analytics summary, but restricted to a list of course sites."""
    # Adapted from nessie.lib.analytics
    mean_values = {}
    for metric in ['assignmentsSubmitted', 'currentScore', 'lastActivity']:
        percentiles = []
        rounded_up_percentiles = []
        for site in canvas_sites:
            metric_for_key = site['analytics'].get(metric, {}).get(key)
            if not metric_for_key:
                continue
            percentile = metric_for_key.get('matrixyPercentile')
            if percentile is not None and not math.isnan(percentile):
                percentiles.append(percentile)
                rounded_up_percentiles.append(metric_for_key.get('roundedUpPercentile'))
        if len(percentiles):
            mean_percentile = mean(percentiles)
            rounded_up_percentile = mean(rounded_up_percentiles)
            mean_values[metric] = {
                'displayPercentile': ordinal(rounded_up_percentile),
                'percentile': mean_percentile,
            }
        else:
            mean_values[metric] = None
    return mean_values


def ordinal(nbr):
    # Copied from nessie.lib.analytics
    rounded = round(nbr)
    mod_ten = rounded % 10
    if (mod_ten == 1) and (rounded != 11):
        suffix = 'st'
    elif (mod_ten == 2) and (rounded != 12):
        suffix = 'nd'
    elif (mod_ten == 3) and (rounded != 13):
        suffix = 'rd'
    else:
        suffix = 'th'
    return f'{rounded}{suffix}'
