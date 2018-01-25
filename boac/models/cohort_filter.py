import json
import re
from boac import db, std_commit
from boac.api.errors import InternalServerError
from boac.lib import util
from boac.models.alert import Alert
from boac.models.athletics import Athletics
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import cohort_filter_owners
from boac.models.base import Base
from boac.models.student import Student
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB


class CohortFilter(Base, UserMixin):
    __tablename__ = 'cohort_filters'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    filter_criteria = db.Column(JSONB, nullable=False)
    owners = db.relationship('AuthorizedUser', secondary=cohort_filter_owners, back_populates='cohort_filters')

    def __init__(self, label, filter_criteria):
        self.label = label
        self.filter_criteria = filter_criteria

    def __repr__(self):
        return '<CohortFilter {}, label={}, owners={}, filter_criteria={}>'.format(
            self.id,
            self.label,
            self.owners,
            self.filter_criteria,
        )

    @classmethod
    def create(
            cls,
            uid,
            label,
            gpa_ranges=None,
            group_codes=None,
            levels=None,
            majors=None,
            unit_ranges_eligibility=None,
            unit_ranges_pacing=None,
    ):
        criteria = cls.compose_filter_criteria(
            gpa_ranges=gpa_ranges,
            group_codes=group_codes,
            levels=levels,
            majors=majors,
            unit_ranges_eligibility=unit_ranges_eligibility,
            unit_ranges_pacing=unit_ranges_pacing,
        )
        cf = CohortFilter(label=label, filter_criteria=json.dumps(criteria))
        user = AuthorizedUser.find_by_uid(uid)
        user.cohort_filters.append(cf)
        # The new Cohort Filter's primary ID column is not generated until the DB session is flushed.
        db.session.flush()
        cohort = construct_cohort(cf)
        std_commit()
        return cohort

    @classmethod
    def update(cls, cohort_id, label):
        cf = CohortFilter.query.filter_by(id=cohort_id).first()
        cf.label = label
        cohort = construct_cohort(cf)
        std_commit()
        return cohort

    @classmethod
    def share(cls, cohort_id, user_id):
        cf = CohortFilter.query.filter_by(id=cohort_id).first()
        user = AuthorizedUser.find_by_uid(user_id)
        user.cohort_filters.append(cf)
        cohort = construct_cohort(cf)
        std_commit()
        return cohort

    @classmethod
    def all(cls):
        return [construct_cohort(cf, include_students=False) for cf in CohortFilter.query.all()]

    @classmethod
    def all_owned_by(cls, uid, include_alerts=False):
        filters = CohortFilter.query.filter(CohortFilter.owners.any(uid=uid)).order_by(CohortFilter.label).all()
        kwargs = {'include_students': False}
        if include_alerts:
            kwargs['include_alerts_for_uid'] = uid
        return [construct_cohort(cohort_filter, **kwargs) for cohort_filter in filters]

    @classmethod
    def find_by_id(cls, cohort_id, order_by=None, offset=0, limit=50):
        cf = CohortFilter.query.filter_by(id=cohort_id).first()
        return cf and construct_cohort(cf, order_by, offset, limit)

    @classmethod
    def delete(cls, cohort_id):
        cohort_filter = CohortFilter.query.filter_by(id=cohort_id).first()
        db.session.delete(cohort_filter)
        std_commit()

    @classmethod
    def compose_filter_criteria(
            cls,
            gpa_ranges=None,
            group_codes=None,
            levels=None,
            majors=None,
            unit_ranges_eligibility=None,
            unit_ranges_pacing=None,
    ):
        if not gpa_ranges and not group_codes and not levels and not majors and not unit_ranges_eligibility and not unit_ranges_pacing:
            raise InternalServerError('CohortFilter creation requires one or more non-empty criteria.')
        # Validate
        for arg in [gpa_ranges, group_codes, levels, majors, unit_ranges_eligibility, unit_ranges_pacing]:
            if arg and not isinstance(arg, list):
                raise InternalServerError('All \'filter_criteria\' objects must be instance of \'list\' type.')
        group_code_syntax = re.compile('^[A-Z\-]+$')
        if group_codes and any(not group_code_syntax.match(code) for code in group_codes):
            raise InternalServerError('\'group_codes\' arg has invalid data: ' + str(group_codes))
        level_syntax = re.compile('^[A-Z][a-z]+$')
        if levels and any(not level_syntax.match(level) for level in levels):
            raise InternalServerError('\'levels\' arg has invalid data: ' + str(levels))
        if majors and any(not isinstance(m, str) for m in majors):
            raise InternalServerError('\'majors\' arg has invalid data: ' + str(majors))
        # The 'numrange' syntax is based on https://www.postgresql.org/docs/9.3/static/rangetypes.html
        numrange_syntax = re.compile('^numrange\([0-9\.NUL]+, [0-9\.NUL]+, \'..\'\)$')
        for r in (gpa_ranges or []) + (unit_ranges_eligibility or []) + (unit_ranges_pacing or []):
            if not numrange_syntax.match(r):
                raise InternalServerError('Range argument \'{}\' does not match expected \'numrange\' syntax: {}'.format(r, numrange_syntax.pattern))
        return {
            'groupCodes': group_codes or [],
            'levels': levels or [],
            'majors': majors or [],
            'gpaRanges': gpa_ranges or [],
            'unitRangesEligibility': unit_ranges_eligibility or [],
            'unitRangesPacing': unit_ranges_pacing or [],
        }


def construct_cohort(cf, order_by=None, offset=0, limit=50, include_students=True, include_alerts_for_uid=None):
    cohort = {
        'id': cf.id,
        'code': cf.id,
        'label': cf.label,
        'name': cf.label,
        'owners': [user.uid for user in cf.owners],
    }
    c = cf if isinstance(cf.filter_criteria, dict) else json.loads(cf.filter_criteria)
    gpa_ranges = util.get(c, 'gpaRanges', [])
    # Property name 'team_group_codes' is deprecated; we prefer the camelCased 'groupCodes'.
    group_codes = util.get(c, 'groupCodes', []) or util.get(c, 'team_group_codes', [])
    levels = util.get(c, 'levels', [])
    majors = util.get(c, 'majors', [])
    unit_ranges_eligibility = util.get(c, 'unitRangesEligibility', [])
    unit_ranges_pacing = util.get(c, 'unitRangesPacing', [])
    results = Student.get_students(
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        levels=levels,
        majors=majors,
        unit_ranges_eligibility=unit_ranges_eligibility,
        unit_ranges_pacing=unit_ranges_pacing,
        order_by=order_by,
        offset=offset,
        limit=limit,
        sids_only=not include_students,
    )
    team_groups = Athletics.get_team_groups(group_codes) if group_codes else []
    cohort.update({
        'filterCriteria': {
            'gpaRanges': gpa_ranges,
            'groupCodes': group_codes,
            'levels': levels,
            'majors': majors,
            'unitRangesEligibility': unit_ranges_eligibility,
            'unitRangesPacing': unit_ranges_pacing,
        },
        'teamGroups': team_groups,
        'totalMemberCount': results['totalStudentCount'],
    })
    if include_students:
        cohort.update({
            'members': results['students'],
        })
    if include_alerts_for_uid:
        viewer = AuthorizedUser.find_by_uid(include_alerts_for_uid)
        if viewer:
            alert_counts = Alert.current_alert_counts_for_sids(viewer.id, results['sids'])
            cohort.update({
                'alerts': alert_counts,
            })
    return cohort
