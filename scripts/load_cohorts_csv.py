import os
from scriptpath import scriptify


@scriptify.in_app
def main(app):
    from boac.models.team import Team
    cohorts_csv = '{}/cohorts.csv'.format(os.path.expanduser('~/tmp/fixtures'))
    Team.load_csv(cohorts_csv)
    print('\nDone. Data inserted in BOAC db.'.format(cohorts_csv), end='\n\n')


main()
