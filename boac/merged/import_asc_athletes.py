"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


import csv

from boac import db, std_commit
from boac.externals import asc_athletes_api
from boac.externals import calnet
from boac.models.athletics import Athletics
from boac.models.student import Student
from flask import current_app as app

THIS_ACAD_YR = '2017-18'

SPORT_TRANSLATIONS = {
    'MBB': 'BAM',
    'MBK': 'BBM',
    'WBK': 'BBW',
    'MCR': 'CRM',
    'WCR': 'CRW',
    'MFB': 'FBM',
    'WFH': 'FHW',
    'MGO': 'GOM',
    'WGO': 'GOW',
    'MGY': 'GYM',
    'WGY': 'GYW',
    'WLC': 'LCW',
    'MRU': 'RGM',
    'WSF': 'SBW',
    'MSC': 'SCM',
    'WSC': 'SCW',
    'MSW': 'SDM',
    'WSW': 'SDW',
    # 'Beach Volleyball' vs. 'Sand Volleyball'.
    'WBV': 'SVW',
    'MTE': 'TNM',
    'WTE': 'TNW',
    # ASC's subsets of Track do not directly match the Athlete API's subsets. In ASC's initial data transfer,
    # all track athletes were mapped to 'TO*', 'Outdoor Track & Field'.
    'MTR': 'TOM',
    'WTR': 'TOW',
    'WVB': 'VBW',
    'MWP': 'WPM',
    'WWP': 'WPW',
}

# There are multiple groups within these teams, and the remainder group (for team members who don't fit any
# of the defined squads or specialties) is misleadingly named as if it identifies the entire team.
AMBIGUOUS_GROUP_CODES = [
    'MFB',
    'MSW',
    'MTR',
    'WSW',
    'WTR',
]


def safety_check_asc_api(feed):
    # Does the new feed have less than half the number of active athletes?
    nbr_current_active = Student.query.filter(Student.is_active_asc.is_(True)).count()
    nbr_active_in_feed = len(set(r['SID'] for r in feed if r['ActiveYN'] == 'Yes'))
    if nbr_current_active > 4 and (nbr_current_active / 2.0 > nbr_active_in_feed):
        return {
            'safe': False,
            'message': f'Import feed would remove {nbr_current_active - nbr_active_in_feed} out of {nbr_current_active} active athletes',
        }
    else:
        return {'safe': True}


def update_from_asc_api(force=False):
    status = {
        'last_sync_date': None,
        'this_sync_date': None,
        'errors': [],
        'warnings': [],
        'change_counts': {
            'new_students': 0,
            'deleted_students': 0,
            'activated_students': 0,
            'inactivated_students': 0,
            'changed_students': 0,
            'new_memberships': 0,
            'deleted_memberships': 0,
            'new_team_groups': 0,
            'changed_team_groups': 0,
        },
    }
    app.logger.info('Starting ASC athletes update job')
    api_results = asc_athletes_api.get_updates()
    if api_results.get('error'):
        app.logger.error('Error from ASC Athletes API; will not merge updates')
        status['errors'].append(api_results['error'])
        return status
    feed = api_results['feed']
    last_sync_date = status['last_sync_date'] = api_results['last_sync_date']
    sync_date = status['this_sync_date'] = api_results['this_sync_date']
    if last_sync_date == sync_date:
        last_feed = asc_athletes_api.get_past_feed(sync_date)
        app.logger.warning(f'Current and previous ASC Athletes API had the same sync date: {sync_date}')
        old_only, new_only = compare_rows(last_feed, feed)
        app.logger.warning(f'Previous feed differences: {old_only} ; current feed differences: {new_only}')
        app.logger.warning('Overwriting previous feed in cache')
        asc_athletes_api.stash_feed(feed)
    safety = safety_check_asc_api(feed)
    if not safety['safe'] and not force:
        status['errors'].append(safety['message'])
        return status
    status['change_counts'].update(update_from_asc(feed))
    asc_athletes_api.confirm_sync(sync_date)
    return status


def merge_tsv(tsv_file='tmp/AscStudents.tsv'):
    update_from_asc(rows_from_tsv(tsv_file))


def rows_from_tsv(tsv_file):
    with open(tsv_file) as f:
        reader = csv.DictReader(f, dialect='excel-tab')
        headers = reader.fieldnames
        # The TSV files have 'TeamStatus' but the API has 'SportStatus'.
        if 'TeamStatus' in headers:
            idx = headers.index('TeamStatus')
            headers[idx] = 'SportStatus'
        rows = [r for r in reader]
    return rows


def compare_tsvs(old_tsv='tmp/AscStudentsOrig.tsv', new_tsv='tmp/AscStudents.tsv'):
    app.logger.warning(f'Comparing {old_tsv} to {new_tsv}')
    return compare_rows(rows_from_tsv(old_tsv), rows_from_tsv(new_tsv))


def update_from_asc(asc_rows):
    status = merge_student_athletes(asc_rows)
    app.logger.info(f'{status}')
    merge_in_calnet_data()
    return status


def sorted_imports(import_rows):
    used_fields = [
        'SID',
        'IntensiveYN',
        'SportCode',
        'SportCodeCore',
        'Sport',
        'SportCore',
        'ActiveYN',
        'SportStatus',
    ]
    rows = [{k: v for k, v in r.items() if k in used_fields} for r in import_rows]
    rows = sorted(rows, key=lambda row: (row['SID'], row['SportCode']))
    return rows


def compare_rows(old_rows, new_rows):
    old_rows = sorted_imports(old_rows)
    new_rows = sorted_imports(new_rows)
    old_only = {r['SID'] + '/' + r['SportCode']: dict(r) for r in old_rows if r not in new_rows}
    new_only = {r['SID'] + '/' + r['SportCode']: dict(r) for r in new_rows if r not in old_rows}
    for k in (old_only.keys() & new_only.keys()):
        app.logger.warning(f'Changed old: {old_only[k]}\n  to new: {new_only[k]}')
    for k in (old_only.keys() - new_only.keys()):
        app.logger.warning(f'Removed: {old_only[k]}')
    for k in (new_only.keys() - old_only.keys()):
        app.logger.warning(f'Added: {new_only[k]}')
    return old_only, new_only


def load_student_athletes(rows):
    return merge_student_athletes(rows, delete_students=False)


def merge_student_athletes(rows, delete_students=True):
    status = {}
    # We want to remove any existing students who are absent from the new TSV.
    # We also want to remove any existing team memberships which have gone away.
    # So long as all data fits in memory, the simplest approach is to collect the current states and compare.
    (imported_team_groups, imported_students) = parse_all_rows(rows)
    status.update(merge_athletics_import(imported_team_groups))
    status.update(merge_students_import(imported_students, delete_students))
    return status


def merge_athletics_import(imported_team_groups):
    status = {
        'new_team_groups': 0,
        'changed_team_groups': 0,
    }
    for team_group in imported_team_groups.values():
        group_code = team_group['group_code']
        existing_group = Athletics.query.filter(Athletics.group_code == group_code).first()
        if not existing_group:
            app.logger.warning(f'Adding new Athletics row: {team_group}')
            status['new_team_groups'] += 1
            athletics_row = Athletics(
                group_code=group_code,
                group_name=team_group['group_name'],
                team_code=team_group['team_code'],
                team_name=team_group['team_name'],
            )
            db.session.add(athletics_row)
            std_commit()
        elif (existing_group.group_name != team_group['group_name']) or (
                existing_group.team_code != team_group['team_code']) or (
                existing_group.team_name != team_group['team_name']):
            app.logger.warning(f'Modifying Athletics row: {team_group} from {existing_group}')
            status['changed_team_groups'] += 1
            existing_group.group_name = team_group['group_name']
            existing_group.team_code = team_group['team_code']
            existing_group.team_name = team_group['team_name']
            db.session.merge(existing_group)
            std_commit()
    return status


def merge_students_import(imported_students, delete_students):
    status = {
        'new_students': 0,
        'deleted_students': 0,
        'activated_students': 0,
        'inactivated_students': 0,
        'changed_students': 0,
        'new_memberships': 0,
        'deleted_memberships': 0,
    }
    existing_students = {row['sid']: row for row in Student.get_all('sid', include_inactive=True)}
    remaining_sids = set(existing_students.keys())
    for student_import in imported_students.values():
        sid = student_import['sid']
        in_intensive_cohort = student_import['in_intensive_cohort']
        is_active_asc = student_import['is_active_asc']
        status_asc = student_import['status_asc']
        team_group_codes = set(student_import['athletics'])
        student_data = existing_students.get(sid, None)
        if not student_data:
            app.logger.warning(f'Adding new Student row: {student_import}')
            status['new_students'] += 1
            student_row = Student(
                sid=sid,
                first_name='',
                last_name='',
                in_intensive_cohort=in_intensive_cohort,
                is_active_asc=is_active_asc,
                status_asc=status_asc,
            )
            db.session.add(student_row)
            std_commit()
            merge_memberships(sid, set([]), team_group_codes, status)
        else:
            remaining_sids.remove(sid)
            if (
                    student_data['inIntensiveCohort'] is not in_intensive_cohort
            ) or (
                    student_data['isActiveAsc'] is not is_active_asc

            ) or (
                    student_data['statusAsc'] != status_asc
            ):
                app.logger.warning(f'Modifying Student row to {student_import} from {student_data}')
                if student_data['isActiveAsc'] is not is_active_asc:
                    if is_active_asc:
                        status['activated_students'] += 1
                    else:
                        status['inactivated_students'] += 1
                else:
                    status['changed_students'] += 1
                student_row = Student.find_by_sid(sid)
                student_row.in_intensive_cohort = in_intensive_cohort
                student_row.is_active_asc = is_active_asc
                student_row.status_asc = status_asc
                db.session.merge(student_row)
                std_commit()
            existing_group_codes = {mem['groupCode'] for mem in student_data.get('athletics', [])}
            if team_group_codes != existing_group_codes:
                merge_memberships(sid, existing_group_codes, team_group_codes, status)
    if delete_students:
        for sid in remaining_sids:
            app.logger.warning(f'Deleting Student SID {sid}')
            status['deleted_students'] += 1
            Student.delete_student(sid)
    else:
        app.logger.warning(f'Will not delete unspecified Students: {remaining_sids}')
    return status


def merge_memberships(sid, old_group_codes, new_group_codes, status):
    student_row = Student.find_by_sid(sid)
    for removed_group_code in (old_group_codes - new_group_codes):
        team_group = Athletics.query.filter(Athletics.group_code == removed_group_code).first()
        app.logger.warning(f'Removing SID {sid} from team group {team_group}')
        status['deleted_memberships'] += 1
        team_group.athletes.remove(student_row)
    for added_group_code in (new_group_codes - old_group_codes):
        team_group = Athletics.query.filter(Athletics.group_code == added_group_code).first()
        app.logger.warning(f'Adding SID {sid} to team group {team_group}')
        status['new_memberships'] += 1
        team_group.athletes.append(student_row)
    std_commit()
    return status


def parse_all_rows(rows):
    imported_team_groups = {}
    imported_students = {}
    for r in rows:
        if r['AcadYr'] == THIS_ACAD_YR and r['SportCode']:
            in_intensive_cohort = r.get('IntensiveYN', 'No') == 'Yes'
            is_active_asc = r.get('ActiveYN', 'No') == 'Yes'
            status_asc = r.get('SportStatus', '')
            asc_code = r['SportCodeCore']
            if asc_code in SPORT_TRANSLATIONS:
                sid = r['SID']
                group_code = r['SportCode']
                if sid in imported_students:
                    student = imported_students[sid]
                    if student['in_intensive_cohort'] is not in_intensive_cohort:
                        app.logger.error(f'Unexpected conflict in import rows for SID {sid}')
                    # Any active team membership means the student is an active athlete,
                    # even if they happen not to be an active member of a different team.
                    # Until BOAC-460 is resolved, the app will discard inactive memberships of an
                    # otherwise active student.
                    if not student['is_active_asc'] and is_active_asc:
                        app.logger.warning('Will discard inactive memberships {} for active SID {}'.format(student['athletics'], sid))
                        student['athletics'] = []
                        student['is_active_asc'] = is_active_asc
                        student['status_asc'] = status_asc
                    elif student['is_active_asc'] and not is_active_asc:
                        app.logger.warning(f'Will discard inactive memberships {group_code} for SID {sid}')
                        continue
                else:
                    student = {
                        'sid': sid,
                        'in_intensive_cohort': in_intensive_cohort,
                        'is_active_asc': is_active_asc,
                        'status_asc': status_asc,
                        'athletics': [],
                    }
                    imported_students[sid] = student
                student['athletics'].append(group_code)
                if group_code not in imported_team_groups:
                    imported_team_groups[group_code] = {
                        'group_code': group_code,
                        'group_name': unambiguous_group_name(r['Sport'], group_code),
                        'team_code': SPORT_TRANSLATIONS[asc_code],
                        'team_name': r['SportCore'],
                    }
            else:
                app.logger.error('Unmapped asc_code {} has ActiveYN for sid {}'.format(asc_code, r['SID']))
    return imported_team_groups, imported_students


def unambiguous_group_name(asc_group_name, group_code):
    if group_code in AMBIGUOUS_GROUP_CODES:
        return f'{asc_group_name} - Other'
    else:
        return asc_group_name


def merge_in_calnet_data():
    students = Student.query.filter(Student.uid.is_(None)).all()
    update_student_attributes(students)
    app.logger.info('Modified {} Student records from calnet'.format(len(db.session.dirty)))
    std_commit()


def update_student_attributes(students=None):
    sid_map = {}
    for student in students:
        sid_map.setdefault(student.sid, []).append(student)
    sids = list(sid_map.keys())

    # Search LDAP.
    all_attributes = calnet.client(app).search_csids(sids)
    if len(sids) != len(all_attributes):
        app.logger.warning('Looked for {} SIDs but only found {}'.format(len(sids), len(all_attributes)))

    # Update db
    for a in all_attributes:
        # Since we searched LDAP by SID, we can be fairly sure that the results have SIDs.
        sid = a['csid']
        name_split = a['sortable_name'].split(',') if 'sortable_name' in a else ''
        full_name = [name.strip() for name in reversed(name_split)]
        for m in sid_map[sid]:
            m.uid = a['uid']
            # Manually-entered ASC name may be more nicely formatted than a student's CalNet default.
            # For now, don't overwrite it.
            m.first_name = m.first_name or (full_name[0] if len(full_name) else '')
            m.last_name = m.last_name or (full_name[1] if len(full_name) > 1 else '')
    return students
