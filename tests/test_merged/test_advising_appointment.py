"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from boac.externals import data_loch
from boac.merged.advising_appointment import get_advising_appointments, search_advising_appointments
from boac.models.university_dept import UniversityDept
from tests.util import (
    assert_every_search_filter_combination,
    assert_search_filters_not_vacuous,
    expected_fts_results,
    get_topic_matches,
    in_date_range,
    legacy_advisor_match,
    legacy_timestamp,
)

asc_advisor_uid = '1081940'
student_sid = '11667051'

# One value per filter, chosen so that filters overlap in fixture data and every combination is meaningful.
APPOINTMENT_SEARCH_FILTERS = {
    'search_phrase': 'life',
    'advisor_uid': asc_advisor_uid,
    'advisor_csid': '800700600',
    'student_csid': '11667051',
    'department_codes': ['COENG'],
    'topic': 'Show Off',
    'datetime_from': '2017-10-15',
    'datetime_to': '2021-09-01',
}
SEARCH_RESULTS_LIMIT = 50

class TestMergedAdvisingAppointment:
    """Advising appointment data, merged."""

    def test_get_advising_appointments(self):
        """Returns all legacy appointments for a given SID."""
        appointments = get_advising_appointments(student_sid)
        assert len(appointments) == 5

        # Verify Calendly appointment
        calendly_appointment = next((a for a in appointments if a['createdBy'] == 'Calendly'), None)
        assert calendly_appointment
        assert calendly_appointment['advisor']['name'] == 'Edwin Land'
        assert 'Can you picture this?' in calendly_appointment['details']
        assert calendly_appointment['appointmentTitle'] == 'Shake it like a Polaroid'

        # Verify YCBM appointment
        ycbm_appointment = next((a for a in appointments if a['createdBy'] == 'YCBM'), None)
        assert ycbm_appointment
        assert ycbm_appointment['id'] == '11667051-00010'
        assert ycbm_appointment['advisor']
        assert ycbm_appointment['advisor']['name'] == 'Milicent Balthazar'
        assert ycbm_appointment['advisor']['sid'] == '53791'
        assert ycbm_appointment['advisor']['title'] is None
        assert ycbm_appointment['advisor']['uid'] == '53791'
        assert ycbm_appointment['advisor']['departments'] == []
        assert ycbm_appointment['appointmentType'] is None
        assert len(ycbm_appointment['attachments']) == 1
        assert ycbm_appointment['createdAt'] == '2017-10-31T12:00:00+00:00'
        assert ycbm_appointment['createdBy'] == 'YCBM'
        assert ycbm_appointment['deptCode'] is None
        assert ycbm_appointment['details'] == 'To my people who keep an impressive wingspan even when the cubicle shrink: \
you got to pull up the intruder by the root of the weed; N.Y. Chew through the machine'
        assert ycbm_appointment['legacySource'] == 'SIS'
        assert ycbm_appointment['student']
        assert ycbm_appointment['student']['sid'] == student_sid
        assert ycbm_appointment['topics'] == ['Ofscéaw']
        assert ycbm_appointment['updatedAt'] is None
        assert ycbm_appointment['updatedBy'] is None
        assert ycbm_appointment['cancelReason'] is None
        assert ycbm_appointment['status'] in [None, 'cancelled']
        assert 'cancelReasonExplained' not in ycbm_appointment
        assert 'statusBy' not in ycbm_appointment
        assert 'statusDate' not in ycbm_appointment

    def test_search(self, mock_appointment_comment):  # noqa: PLR0915
        """Finds legacy appointments and appointment comments matching the criteria, ordered by newest to oldest then rank."""
        results = search_advising_appointments(search_phrase='life')
        appointments = results['appointments']
        assert results['totalAppointmentCount'] == 4
        assert len(appointments) == 4

        assert appointments[0]['id'] == '78342-847236-73423'
        assert appointments[0]['advisor']['name'] == 'John Deleted-in-BOA'
        assert appointments[0]['advisor']['role'] is None
        assert appointments[0]['advisor']['sid'] == '333333333'
        assert appointments[0]['advisor']['uid'] == '33333'
        assert appointments[0]['advisor']['deptCodes'] == ['QCADV']
        assert 'deptCode' not in appointments[0]
        assert appointments[0]['details'] == 'A life well lived'
        assert appointments[0]['detailsSnippet'] == 'A <strong>life</strong> well lived'
        assert 'cancelReason' not in appointments[0]
        assert 'cancelReasonExplained' not in appointments[0]
        assert appointments[0]['kind'] == 'appointment'
        assert 'status' not in appointments[0]
        assert appointments[0]['student']['sid'] == '9191919191'
        assert appointments[0]['student']['uid'] == '191919'
        assert appointments[0]['student']['firstName'] == 'Paul'
        assert appointments[0]['student']['lastName'] == 'Tarsus'
        assert appointments[0]['createdAt'] is None
        assert appointments[0]['updatedAt'] is None

        assert appointments[1]['id'] == mock_appointment_comment.id
        assert appointments[1]['parentType'] == 'appointment'
        assert appointments[1]['parentId'] == '11667051-00010'
        assert appointments[1]['advisor']['name'] == 'COE Advisor'
        assert appointments[1]['advisor']['role'] == 'advisor'
        assert appointments[1]['advisor']['sid'] == '53791'
        assert appointments[1]['advisor']['uid'] == '1133399'
        assert appointments[1]['advisor']['deptCodes'] == ['COENG']
        assert appointments[1]['snippet'] == '<strong>Life</strong> is like a comment on an appointment.'
        assert appointments[1]['kind'] == 'commentOnAppointment'
        assert appointments[1]['student']['sid'] == '11667051'
        assert appointments[1]['student']['uid'] == '61889'
        assert appointments[1]['student']['firstName'] == 'Deborah'
        assert appointments[1]['student']['lastName'] == 'Davies'
        assert appointments[1]['createdAt']
        assert appointments[1]['updatedAt']

        assert appointments[2]['id'] == '51d827-98ca28-43b98'
        assert appointments[2]['advisor']['name'] == 'Roberta Joan Anderson'
        assert appointments[2]['advisor']['role'] is None
        assert appointments[2]['advisor']['sid'] == '800700600'
        assert appointments[2]['advisor']['uid'] == '1133399'
        assert appointments[2]['advisor']['deptCodes'] == ['QCADV']
        assert appointments[2]['details'] == 'Need an A to pass, strategies for adapting to campus life.'
        assert appointments[2]['detailsSnippet'] == 'Need an A to pass, strategies for adapting to campus <strong>life</strong>.'
        assert appointments[2]['kind'] == 'appointment'
        assert appointments[2]['student']['sid'] == '9191919191'
        assert appointments[2]['student']['uid'] == '191919'
        assert appointments[2]['student']['firstName'] == 'Paul'
        assert appointments[2]['student']['lastName'] == 'Tarsus'
        assert appointments[2]['createdAt']
        assert appointments[2]['updatedAt'] is None

        assert appointments[3]['id'] == '9100000000-00010'
        assert appointments[3]['advisor']['name'] == 'Loramps Glub'
        assert appointments[3]['advisor']['role'] is None
        assert appointments[3]['advisor']['sid'] == '100200300'
        assert appointments[3]['advisor']['uid'] == '1081940'
        assert appointments[3]['advisor']['deptCodes'] == ['UWASC']
        assert appointments[3]['details'] == 'Art imitates life. Cancellation'
        assert appointments[3]['detailsSnippet'] == 'Art imitates <strong>life</strong>. Cancellation'
        assert appointments[3]['kind'] == 'appointment'
        assert appointments[3]['student']['sid'] == '9100000000'
        assert appointments[3]['student']['uid'] == '300848'
        assert appointments[3]['student']['firstName'] == 'Nora Stanton'
        assert appointments[3]['student']['lastName'] == 'Barney'
        assert appointments[3]['createdAt']
        assert appointments[3]['updatedAt'] is None


class TestAppointmentSearchFilterCombinations:
    """Loch appointment search, every combination of filters."""

    def test_every_filter_combination(self, mock_searchable_appointment_comments, mock_legacy_ucbconversion_records):  # noqa: ARG002
        """Returns exactly the BOA comments and legacy appointments matching all active filters, for all 256 combinations."""
        def _search_advising_appointments(criteria):
            results = search_advising_appointments(**criteria, offset=0, limit=SEARCH_RESULTS_LIMIT)
            return {
                'rows': results['appointments'],
                'total': results['totalAppointmentCount'],
            }
        assert_every_search_filter_combination(
            filters=APPOINTMENT_SEARCH_FILTERS,
            search=_search_advising_appointments,
            expected_keys=_expected_appointment_ids,
            limit=SEARCH_RESULTS_LIMIT,
        )

    def test_filters_are_not_vacuous(self, mock_searchable_appointment_comments, mock_legacy_ucbconversion_records):  # noqa: ARG002
        """Each filter, applied alone, narrows the results and leaves at least one match."""
        assert_search_filters_not_vacuous(APPOINTMENT_SEARCH_FILTERS, _expected_appointment_ids)

def _advisor_uids(department_codes, advisor_uid, advisor_sid):
    """Department codes, when present, take precedence over an individual advisor UID."""
    if not department_codes:
        if advisor_uid:
            return {advisor_uid}
        if advisor_sid:
            return {row['ldap_uid'] for row in data_loch.safe_execute_rds(
                'SELECT ldap_uid FROM sis_data.basic_attributes WHERE sid = %(sid)s',
                sid=advisor_sid,
            )}
        return set()
    uids = set()
    for dept_code in department_codes:
        dept = UniversityDept.find_by_dept_code(dept_code)
        uids.update(membership.authorized_user.uid for membership in dept.authorized_users)
    return uids


def _expected_appointment_ids(
        search_phrase=None,
        advisor_uid=None,
        advisor_csid=None,
        student_csid=None,
        department_codes=None,
        topic=None,
        datetime_from=None,
        datetime_to=None,
):
    boa_cdc = data_loch.boa_cdc_schema()
    legacy_appts = data_loch.advising_appointments_schema()
    advisor_uids = _advisor_uids(department_codes, advisor_uid, advisor_csid)
    all_student_sids = {row['sid'] for row in data_loch.safe_execute_rds(f'SELECT sid FROM {data_loch.student_schema()}.student_profile_index')}
    appointment_ids = []

    comment_text_matches = expected_fts_results(
        f'{boa_cdc}.advising_appointment_comments_search_index',
        'boa_id',
        search_phrase,
        data_loch.safe_execute_rds,
    )
    comments = data_loch.safe_execute_rds(f"""
        SELECT c.boa_id, c.parent_appointment_id, c.author_uid, c.updated_at, aa.student_sid
          FROM {boa_cdc}.advising_appointment_comments c
          JOIN {legacy_appts}.advising_appointments aa ON aa.id = c.parent_appointment_id""")
    for row in comments:
        if (
            not topic  # Comments on appointments have no topics.
            and (not comment_text_matches or row['boa_id'] in comment_text_matches)
            and (not advisor_uids or row['author_uid'] in advisor_uids)
            and (not student_csid or row['student_sid'] == student_csid)
            and (row['student_sid'] in all_student_sids)
            and in_date_range(row['updated_at'], datetime_from, datetime_to)
        ):
            appointment_ids.append(row['boa_id'])

    appointment_text_matches = expected_fts_results(
        f'{legacy_appts}.advising_appointments_search_index',
        'id',
        search_phrase,
        data_loch.safe_execute_rds,
    )
    topic_matches = get_topic_matches(f'{data_loch.advising_notes_schema()}.advising_note_topics_curated', topic, data_loch.safe_execute_rds)
    appointments = data_loch.safe_execute_rds(f"""
        SELECT id, student_sid, advisor_uid, advisor_sid, created_by, created_at, updated_at
          FROM {legacy_appts}.advising_appointments""")
    for row in appointments:
        if (
            (not appointment_text_matches or row['id'] in appointment_text_matches)
            and (not topic_matches or row['id'] in topic_matches)
            and legacy_advisor_match(row, advisor_uids, advisor_csid)
            and (not student_csid or row['student_sid'] == student_csid)
                        and (row['student_sid'] in all_student_sids)
            and in_date_range(legacy_timestamp(row), datetime_from, datetime_to)
        ):
            appointment_ids.append(row['id'])
    return appointment_ids
