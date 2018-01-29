import csv

from boac import db, std_commit
from boac.externals import calnet
from boac.models.athletics import Athletics
from boac.models.student import Student

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


def load_csv(app, csv_file='tmp/FilteredAscStudents.csv'):
    with open(csv_file) as f:
        athletics, students = load_student_athletes(app, csv.DictReader(f))
        app.logger.info(f'{len(athletics)} rows added to \'athletics\' table; {len(students)} rows added to \'students\' table; CSV file: {csv_file}')


def merge_tsv(app, tsv_file='tmp/AscStudents.tsv'):
    with open(tsv_file) as f:
        athletics, students = merge_student_athletes(app, csv.DictReader(f, dialect='excel-tab'))
        app.logger.info(f'{len(athletics)} Athletics rows; {len(students)} Students rows; TSV file: {tsv_file}')
    merge_in_calnet_data(app)


def sorted_tsv(tsv_file):
    f = open(tsv_file)
    rows = sorted(csv.DictReader(f, dialect='excel-tab'), key=lambda row: (row['SID'], row['SportCode']))
    f.close()
    return rows


def compare_tsvs(app, old_tsv='tmp/AscStudentsOrig.tsv', new_tsv='tmp/AscStudents.tsv'):
    old_rows = sorted_tsv(old_tsv)
    new_rows = sorted_tsv(new_tsv)
    old_only = {r['SID'] + '/' + r['SportCode']: dict(r) for r in old_rows if r not in new_rows}
    new_only = {r['SID'] + '/' + r['SportCode']: dict(r) for r in new_rows if r not in old_rows}
    app.logger.warning(f'Comparing {old_tsv} to {new_tsv}')
    for k in (old_only.keys() & new_only.keys()):
        app.logger.warning(f'Changed old: {old_only[k]}\n  to new: {new_only[k]}')
    for k in (old_only.keys() - new_only.keys()):
        app.logger.warning(f'Removed: {old_only[k]}')
    for k in (new_only.keys() - old_only.keys()):
        app.logger.warning(f'Added: {new_only[k]}')
    return (old_only, new_only)


def load_student_athletes(app, rows):
    return merge_student_athletes(app, rows, delete_students=False)


def merge_student_athletes(app, rows, delete_students=True):
    # We want to remove any existing students who are absent from the new TSV.
    # We also want to remove any existing team memberships which have gone away.
    # So long as all data fits in memory, the simplest approach is to collect the current states and compare.
    (import_athletics, import_students) = parse_all_rows(app, rows)
    nbr_team_definition_changes = merge_athletics_import(app, import_athletics)
    app.logger.warning(f'{nbr_team_definition_changes} Athletics rows changed')
    nbr_student_changes = merge_students_import(app, import_students, delete_students)
    app.logger.warning(f'{nbr_student_changes} Students rows changed')
    return import_athletics, import_students


def merge_athletics_import(app, import_athletics):
    team_definition_changes = 0
    for team_group in import_athletics.values():
        app.logger.debug(f'team_group = {team_group}')
        group_code = team_group['group_code']
        existing_group = Athletics.query.filter(Athletics.group_code == group_code).first()
        app.logger.debug(f'athletics_row = {existing_group}')
        if not existing_group:
            app.logger.warning(f'Adding new Athletics row: {team_group}')
            team_definition_changes += 1
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
            team_definition_changes += 1
            existing_group.group_name = team_group['group_name']
            existing_group.team_code = team_group['team_code']
            existing_group.team_name = team_group['team_name']
            db.session.merge(existing_group)
            std_commit()
    return team_definition_changes


def merge_students_import(app, import_students, delete_students):
    student_changes = 0
    existing_students = {row['sid']: row for row in Student.get_all('sid')}
    remaining_sids = set(existing_students.keys())
    for student_import in import_students.values():
        app.logger.debug(f'student_import = {student_import}')
        sid = student_import['sid']
        in_intensive_cohort = student_import['in_intensive_cohort']
        is_active_asc = student_import['is_active_asc']
        status_asc = student_import['status_asc']
        team_group_codes = set(student_import['athletics'])
        student_data = existing_students.get(sid, None)
        app.logger.debug(f'student_data = {student_data}')
        if not student_data:
            app.logger.warning(f'Adding new Student row: {student_import}')
            student_changes += 1
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
            merge_memberships(app, sid, set([]), team_group_codes)
        else:
            remaining_sids.remove(sid)
            if (
                    student_data['inIntensiveCohort'] is not in_intensive_cohort
            ) or (
                    student_data['is_active_asc'] is not is_active_asc

            ) or (
                    student_data['status_asc'] != status_asc
            ):
                app.logger.warning(f'Modifying Student row to {student_import} from {student_data}')
                student_changes += 1
                student_row = Student.find_by_sid(sid)
                student_row.in_intensive_cohort = in_intensive_cohort
                student_row.is_active_asc = is_active_asc
                student_row.status_asc = status_asc
                db.session.merge(student_row)
                std_commit()
            existing_group_codes = {mem['groupCode'] for mem in student_data['athletics']}
            if team_group_codes != existing_group_codes:
                student_changes += merge_memberships(app, sid, existing_group_codes, team_group_codes)
    if delete_students:
        for sid in remaining_sids:
            app.logger.warning(f'Deleting Student SID {sid}')
            student_changes += 1
            Student.delete_student(sid)
    else:
        app.logger.warning(f'Will not delete unspecified Students: {remaining_sids}')
    return student_changes


def merge_memberships(app, sid, old_group_codes, new_group_codes):
    student_changes = 0
    student_row = Student.find_by_sid(sid)
    for removed_group_code in (old_group_codes - new_group_codes):
        team_group = Athletics.query.filter(Athletics.group_code == removed_group_code).first()
        app.logger.warning(f'Removing SID {sid} from team group {team_group}')
        student_changes += 1
        team_group.athletes.remove(student_row)
    for added_group_code in (new_group_codes - old_group_codes):
        team_group = Athletics.query.filter(Athletics.group_code == added_group_code).first()
        app.logger.warning(f'Adding SID {sid} to team group {team_group}')
        student_changes += 1
        team_group.athletes.append(student_row)
    std_commit()
    return student_changes


def parse_all_rows(app, rows):
    import_athletics = {}
    import_students = {}
    for r in rows:
        if r['AcadYr'] == THIS_ACAD_YR and r['SportCode']:
            in_intensive_cohort = r.get('IntensiveYN', 'No') == 'Yes'
            is_active_asc = r.get('ActiveYN', 'No') == 'Yes'
            status_asc = r.get('TeamStatus', '')
            asc_code = r['SportCodeCore']
            if asc_code in SPORT_TRANSLATIONS:
                sid = r['SID']
                if sid in import_students:
                    student = import_students[sid]
                    if (
                            student['in_intensive_cohort'] is not in_intensive_cohort
                    ) or (
                            student['is_active_asc'] is not is_active_asc
                    ) or (
                            student['status_asc'] != status_asc
                    ):
                        app.logger.error(f'Unexpected conflict in import rows for SID {sid}')
                else:
                    student = {
                        'sid': sid,
                        'in_intensive_cohort': in_intensive_cohort,
                        'is_active_asc': is_active_asc,
                        'status_asc': status_asc,
                        'athletics': [],
                    }
                    import_students[sid] = student
                group_code = r['SportCode']
                student['athletics'].append(group_code)
                if group_code not in import_athletics:
                    import_athletics[group_code] = {
                        'group_code': group_code,
                        'group_name': r['Sport'],
                        'team_code': SPORT_TRANSLATIONS[asc_code],
                        'team_name': r['SportCore'],
                    }
            else:
                app.logger.error('Unmapped asc_code {} has ActiveYN for sid {}'.format(asc_code, r['SID']))
    return import_athletics, import_students


def merge_in_calnet_data(app):
    students = Student.query.filter(Student.uid.is_(None)).all()
    update_student_attributes(app, students)
    app.logger.info('Modified {} Student records from calnet'.format(len(db.session.dirty)))
    std_commit()


def update_student_attributes(app, students=None):
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
