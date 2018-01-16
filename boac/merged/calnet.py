from boac import std_commit
from boac.externals import calnet
from boac.models.json_cache import stow
from boac.models.student import Student


@stow('calnet_user_for_uid_{uid}')
def get_calnet_user_for_uid(app, uid):
    persons = calnet.client(app).search_uids([uid])
    p = persons[0] if len(persons) > 0 else None
    return {
        'uid': uid,
        'firstName': p and p['first_name'],
        'lastName': p and p['last_name'],
    }


def refresh_cohort_attributes(app, cohorts=None):
    members = cohorts or Student.query.all()
    # Students who play more than one sport will have multiple records.
    member_map = {}
    for m in members:
        member_map.setdefault(m.sid, []).append(m)
    csids = list(member_map.keys())

    # Search LDAP.
    all_attrs = calnet.client(app).search_csids(csids)
    if len(csids) != len(all_attrs):
        app.logger.warning(f'Looked for {len(csids)} CSIDS but only found {len(all_attrs)}')

    # Update the DB.
    for attrs in all_attrs:
        # Since we searched LDAP by CSID, we can be fairly sure that the results have CSIDs.
        csid = attrs['csid']
        name_split = attrs['sortable_name'].split(',') if 'sortable_name' in attrs else ''
        full_name = [name.strip() for name in reversed(name_split)]
        for m in member_map[csid]:
            m.uid = attrs['uid']
            # A manually-entered ASC name may be more nicely formatted than a student's CalNet default.
            # For now, don't overwrite it.
            m.first_name = m.first_name or (full_name[0] if len(full_name) else '')
            m.last_name = m.last_name or (full_name[1] if len(full_name) > 1 else '')
    return members


def fill_cohort_uids(app):
    to_update = Student.query.filter(Student.uid.is_(None)).all()
    refresh_cohort_attributes(app, to_update)
    std_commit()
    return to_update
