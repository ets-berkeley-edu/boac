"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from copy import deepcopy
import json
import os
import sys

from boac.lib import scriptify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


@scriptify.in_app  # noqa: C901
def main(app):  # noqa: C901
    from boac import std_commit
    from boac.models.cohort_filter import CohortFilter

    # GPA filter:
    #   Old format: { "gpaRanges": ["numrange(3.5, 4, '[]')", "numrange(0, 2, '[)')"] }
    #   New format: { "gpaRanges": [{'min': 3.5, 'max': 4}, {'min': 0, 'max': 1.999}] }

    # Last Name filter:
    #   Old format: { "lastNameRange": ["F", "M"] }
    #   New format: { "lastNameRanges": [ {'min': 'F', 'max': 'M'} ] }

    errors = []

    for cohort in CohortFilter.query.all():
        db_update_needed = False
        criteria = deepcopy(cohort.filter_criteria)
        if not isinstance(criteria, dict):
            criteria = json.loads(criteria)

        for key in ['gpaRanges', 'lastNameRange']:
            if criteria.get(key, False):
                old_value = criteria.pop(key)
                old_values_joined = ', '.join(old_value)

                if key == 'gpaRanges':
                    converted_values = []
                    for old_format in old_value:
                        def _append_converted_value(_min, _max):
                            converted_values.append({'min': _min, 'max': _max})

                        if 'numrange(0, 2,' in old_format:
                            _append_converted_value(0, 1.999)
                        elif 'numrange(2, 2.5,' in old_format:
                            _append_converted_value(2, 2.499)
                        elif 'numrange(2.5, 3,' in old_format:
                            _append_converted_value(2.5, 2.999)
                        elif 'numrange(3, 3.5,' in old_format:
                            _append_converted_value(3, 3.499)
                        elif 'numrange(3.5, 4,' in old_format:
                            _append_converted_value(3.5, 4)
                        else:
                            errors.append(f'  {cohort.id}: {old_format}')

                    if len(converted_values):
                        criteria[key] = converted_values
                        joined = ', '.join([str(r) for r in converted_values])
                        print(f"""
                            [INFO] Cohort {cohort.id}:
                                'gpaRanges'=[{old_values_joined}] converted to 'gpaRanges'=[{joined}]
                        """)
                        db_update_needed = True

                elif key == 'lastNameRange':
                    criteria['lastNameRanges'] = [{'min': old_value[0], 'max': old_value[1]}]
                    print(f"""
                        [INFO] Cohort {cohort.id}:
                            'lastNameRange'={old_values_joined} converted to
                            'lastNameRanges'=[{criteria['lastNameRanges']}]
                    """)
                    db_update_needed = True

        if db_update_needed:
            # Update db
            cohort.filter_criteria = criteria
            std_commit()

    if errors:
        print('\n[ERROR] Invalid ranges were found (see below) and not migrated.')
        print('\n'.join(errors))


main()
