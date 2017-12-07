import csv

from boac import db
from boac.merged import calnet
from boac.models.team_member import TeamMember

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


def load_cohort_from_csv(app, csv_file='tmp/FilteredAscStudents.csv'):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['AcadYr'] != THIS_ACAD_YR or r['SportActiveYN'] != 'Yes':
                continue
            asc_sport_code_core = r['cSportCodeCore']
            if asc_sport_code_core not in SPORT_TRANSLATIONS:
                app.logger.error('Unmapped Sport Code {} has SportActiveYN for SID {}'.format(
                    asc_sport_code_core,
                    r['SID'],
                ))
                continue
            sis_sport_code = SPORT_TRANSLATIONS[asc_sport_code_core]
            record = TeamMember(
                member_csid=r['SID'],
                member_name=r['cName'],
                code=sis_sport_code,
                asc_sport_code=r['SportCode'],
                asc_sport=r['Sport'],
                asc_sport_code_core=asc_sport_code_core,
                asc_sport_core=r['acSportCore'],
                in_intensive_cohort=False,
            )
            db.session.add(record)
    app.logger.info('Loaded {} TeamMember records from {}'.format(
        len(db.session.new),
        csv_file,
    ))
    db.session.commit()


def fill_empty_uids_from_calnet(app):
    to_update = TeamMember.query.filter(TeamMember.member_uid.is_(None)).all()
    calnet.refresh_cohort_attributes(app, to_update)
    app.logger.info('Modified {} Team records from calnet'.format(len(db.session.dirty)))
    db.session.commit()
