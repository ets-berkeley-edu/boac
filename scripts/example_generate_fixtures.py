import os
from scriptpath import scriptify


os.environ['FIXTURE_OUTPUT_PATH'] = os.path.expanduser('~/tmp')


@scriptify.in_app
def main(app):
    from boac.externals import canvas
    for uid in range(1, 20):
        canvas.get_user_for_uid(app.canvas_instance, uid)


main()
