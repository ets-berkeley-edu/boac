from boac.externals import calnet
from boac.models.cohort import Cohort


def refresh_cohort_attributes(app, cohorts=None):
    members = cohorts or Cohort.query.all()
    # Search LDAP.
    csids = [member.member_csid for member in members]
    member_map = {member.member_csid: member for member in members}
    all_attrs = calnet.client(app).search_csids(csids)
    for attrs in all_attrs:
        csid = attrs.get('csid', None)
        # If LDAP didn't find this csid, skip it.
        if csid:
            member = member_map[csid]
            member.member_uid = attrs['uid']
            member.member_name = attrs['name']
    return cohorts
