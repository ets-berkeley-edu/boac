"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from itertools import islice

from boac.externals import data_loch
from boac.lib.util import camelize, get_benchmarker
from dateutil.tz import tzutc


"""Provide merged admit data from external sources."""


def get_admitted_student_by_sid(sid):
    admit = data_loch.get_admitted_student_by_sid(sid)
    return _to_api_json(admit) if admit else None


def search_for_admitted_students(
    search_phrase=None,
    order_by=None,
):
    benchmark = get_benchmarker('search_for_admitted_students')
    query_tables, query_filter, query_bindings, temp_table = data_loch.get_admitted_students_query(
        search_phrase=search_phrase,
    )
    order_by = order_by or 'last_name'
    sql = f"""
    {temp_table}
    SELECT DISTINCT(sa.cs_empl_id),
        sa.first_name,
        sa.middle_name,
        sa.last_name,
        sa.current_sir,
        sa.special_program_cep,
        sa.reentry_status,
        sa.first_generation_college,
        sa.urem,
        sa.application_fee_waiver_flag,
        sa.residency_category,
        sa.freshman_or_transfer,
        sa.updated_at
        {query_tables}
        {query_filter}
        ORDER BY sa.{order_by}, sa.last_name, sa.first_name, sa.middle_name, sa.cs_empl_id"""

    benchmark('begin admit search query')
    admits = data_loch.safe_execute_rds(sql, **query_bindings)
    benchmark('end')
    return {
        'admits': [_to_api_json(row) for row in islice(admits, 50)] if admits else None,
        'totalAdmitCount': len(admits),
    }


def query_admitted_students(
    colleges=None,
    family_dependent_ranges=None,
    freshman_or_transfer=None,
    has_fee_waiver=None,
    in_foster_care=None,
    is_family_single_parent=None,
    is_first_generation_college=None,
    is_hispanic=None,
    is_last_school_lcff=None,
    is_reentry=None,
    is_student_single_parent=None,
    is_urem=None,
    limit=50,
    offset=0,
    order_by=None,
    residency_categories=None,
    sids_only=False,
    sir=None,
    special_program_cep=None,
    student_dependent_ranges=None,
    x_ethnicities=None,
):
    query_tables, query_filter, query_bindings = data_loch.get_admitted_students_query(
        colleges=colleges,
        family_dependent_ranges=family_dependent_ranges,
        freshman_or_transfer=freshman_or_transfer,
        has_fee_waiver=has_fee_waiver,
        in_foster_care=in_foster_care,
        is_family_single_parent=is_family_single_parent,
        is_first_generation_college=is_first_generation_college,
        is_hispanic=is_hispanic,
        is_last_school_lcff=is_last_school_lcff,
        is_reentry=is_reentry,
        is_student_single_parent=is_student_single_parent,
        is_urem=is_urem,
        residency_categories=residency_categories,
        sir=sir,
        special_program_cep=special_program_cep,
        student_dependent_ranges=student_dependent_ranges,
        x_ethnicities=x_ethnicities,
    )
    sids_result = data_loch.safe_execute_rds(f'SELECT DISTINCT(cs_empl_id) as sid {query_tables} {query_filter}', **query_bindings)
    if sids_result is None:
        return None
    summary = {
        'sids': [row['sid'] for row in sids_result],
        'totalStudentCount': len(sids_result),
    }
    order_by = order_by or 'last_name'
    if not sids_only:
        sql = f"""SELECT DISTINCT(sa.cs_empl_id),
        sa.first_name,
        sa.middle_name,
        sa.last_name,
        sa.current_sir,
        sa.special_program_cep,
        sa.reentry_status,
        sa.first_generation_college,
        sa.urem,
        sa.application_fee_waiver_flag,
        sa.residency_category,
        sa.freshman_or_transfer,
        sa.updated_at
        {query_tables}
        {query_filter}
        ORDER BY sa.{order_by}, sa.last_name, sa.first_name, sa.cs_empl_id OFFSET :offset"""
        query_bindings['offset'] = offset
        if limit and limit < 100:  # Sanity check large limits
            query_bindings['limit'] = limit
            sql += ' LIMIT :limit'
        admits = data_loch.safe_execute_rds(sql, **query_bindings)
        summary['students'] = [_to_api_json(row) for row in admits] if admits else None
    return summary


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()


def _to_api_json(admit):
    updated_at = admit.pop('updated_at', None)
    admit_json = {camelize(key): admit[key] for key in admit.keys()}
    admit_json['updatedAt'] = _isoformat(updated_at) if updated_at else None
    return admit_json
