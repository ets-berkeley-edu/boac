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

from boac.models.authorized_user import AuthorizedUser
from boac.models.degree_progress_template import DegreeProgressTemplate
import pytest


coe_advisor_uid = '1133399'


@pytest.mark.usefixtures('db_session')
class TestCreateDegreeProgressTemplate:
    """Degree Progress Template Creation."""

    def test_create_template(self):
        """Initializes a master template."""
        advisor_dept_codes = ['COENG']
        coe_advisor_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        degree_name = 'Celtic Studies BA 2021'
        degree = DegreeProgressTemplate.create(
            advisor_dept_codes=advisor_dept_codes,
            created_by=coe_advisor_id,
            degree_name=degree_name,
        )
        assert degree
        assert degree.__repr__() == f"""<DegreeProgressTemplate id={degree.id},
                    degree_name={degree_name},
                    student_sid=None,
                    advisor_dept_codes={advisor_dept_codes},
                    deleted_at=None,
                    created_at={degree.created_at},
                    created_by={coe_advisor_id},
                    updated_at={degree.updated_at}
                    updated_by={coe_advisor_id}>"""
