import os
# Boilerplate allowing scripts in the /scripts directory to find the boac module.
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from boac.lib import scriptify

os.environ['FIXTURE_OUTPUT_PATH'] = os.path.expanduser('~/tmp')

@scriptify.in_app
def main(app):
    from boac.externals import canvas
    for uid in range(1, 20):
        canvas.get_user_for_uid(app.canvas_instance, uid)

main()
