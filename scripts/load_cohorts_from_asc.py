from scriptpath import scriptify


@scriptify.in_app
def main(app):
    from boac.externals import asc_cohorts
    asc_cohorts.load_cohort_from_csv(app)
    asc_cohorts.fill_empty_uids_from_calnet(app)


main()
