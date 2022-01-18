"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement
import pytest
from sqlalchemy.exc import IntegrityError

coe_advisor_uid = '1133399'


@pytest.mark.usefixtures('db_session')
class TestDegreeProgressUnitRequirement:
    """Degree Progress Unit Requirement Creation."""

    def test_create_unit_requirement(self):
        coe_advisor_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        template = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=coe_advisor_id,
            degree_name='Celtic Studies BA 2021',
        )
        min_units = 45
        name = 'Celtic Requirements'
        unit_requirement = DegreeProgressUnitRequirement.create(
            created_by=coe_advisor_id,
            min_units=min_units,
            name=name,
            template_id=template.id,
        )
        assert unit_requirement
        assert unit_requirement.__repr__() == f"""<DegreeProgressUnitRequirement id={unit_requirement.id},
                    name={name},
                    min_units={min_units},
                    template_id={template.id},
                    created_at={unit_requirement.created_at},
                    created_by={coe_advisor_id},
                    updated_at={unit_requirement.updated_at},
                    updated_by={coe_advisor_id}>"""

        assert template.unit_requirements
        assert len(template.unit_requirements) == 1
        assert unit_requirement.template

    @pytest.mark.skip(reason='TODO: unit_requirement db.relationship needs fix')
    def test_create_nonunique_unit_requirements(self, db):
        """Requires unit requirements in a single template to have unique names."""
        coe_advisor_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        template = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=coe_advisor_id,
            degree_name='Celtic Studies BA 2021',
        )
        name = 'Celtic Requirements'
        unit_requirement = DegreeProgressUnitRequirement.create(
            created_by=coe_advisor_id,
            min_units=70,
            name=name,
            template_id=template.id,
        )
        assert unit_requirement

        with pytest.raises(IntegrityError):
            DegreeProgressUnitRequirement.create(
                created_by=coe_advisor_id,
                min_units=53,
                name=name,
                template_id=template.id,
            )
        db.session.rollback()
