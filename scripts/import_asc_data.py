from scriptpath import scriptify


@scriptify.in_app
def main(app):
    from boac.externals import import_asc_athletes
    import_asc_athletes.merge_tsv(app)
    import_asc_athletes.merge_in_calnet_data(app)


main()
