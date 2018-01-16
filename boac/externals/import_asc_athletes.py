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


def load_student_athletes(app, rows):
    athletics = {}
    students = {}
    for r in rows:
        if r['AcadYr'] == THIS_ACAD_YR and r['SportActiveYN'] == 'Yes':
            asc_code = r['cSportCodeCore']
            if asc_code in SPORT_TRANSLATIONS:
                sid = r['SID']
                if sid in students:
                    student = students[sid]
                else:
                    name_split = r['cName'].split(',') if 'cName' in r else ''
                    full_name = [name.strip() for name in reversed(name_split)]
                    student = Student(
                        sid=sid,
                        first_name=full_name[0].strip() if len(full_name) else '',
                        last_name=full_name[1].strip() if len(full_name) > 1 else '',
                        in_intensive_cohort=False,
                    )
                    std_commit()
                    students[sid] = student
                # Load team group (e.g., 'Football, Defensive Backs')
                group_code = r['SportCode']
                if group_code in athletics:
                    team_group = athletics[group_code]
                else:
                    team_group = Athletics(
                        group_code=group_code,
                        group_name=r['Sport'],
                        team_code=SPORT_TRANSLATIONS[asc_code],
                        team_name=r['acSportCore'],
                    )
                    db.session.add(team_group)
                    athletics[group_code] = team_group

                team_group.athletes.append(student)
                std_commit()
            else:
                app.logger.error('Unmapped asc_code {} has SportActiveYN for sid {}'.format(asc_code, r['SID']))
    return athletics, students


def merge_in_calnet_data(app):
    students = Student.query.filter(Student.uid.is_(None)).all()
    update_student_attributes(app, students)
    app.logger.info('Modified {} Team records from calnet'.format(len(db.session.dirty)))
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
