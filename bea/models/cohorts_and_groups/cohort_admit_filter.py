"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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


class CohortAdmitFilter(object):

    def __init__(self, data):
        self.data = data

    @property
    def colleges(self):
        return list(map(lambda d: d['college'], self.data['colleges'])) if self.data.get('colleges') else []

    @colleges.setter
    def colleges(self, value):
        self.data['colleges'] = value

    @property
    def current_sir(self):
        return self.data.get('current_sir')

    @current_sir.setter
    def current_sir(self, value):
        self.data['current_sir'] = value

    @property
    def family_dependents(self):
        return [d for d in self.data['family_dependents']] if self.data.get('family_dependents') else []

    @family_dependents.setter
    def family_dependents(self, value):
        self.data['family_dependents'] = value

    @property
    def family_single_parent(self):
        return self.data.get('family_single_parent')

    @family_single_parent.setter
    def family_single_parent(self, value):
        self.data['family_single_parent'] = value

    @property
    def fee_waiver(self):
        return self.data.get('fee_waiver')

    @fee_waiver.setter
    def fee_waiver(self, value):
        self.data['fee_waiver'] = value

    @property
    def first_gen_college(self):
        return self.data.get('first_gen_college')

    @first_gen_college.setter
    def first_gen_college(self, value):
        self.data['first_gen_college'] = value

    @property
    def foster_care(self):
        return self.data.get('foster_care')

    @foster_care.setter
    def foster_care(self, value):
        self.data['foster_care'] = value

    @property
    def freshman_or_transfer(self):
        return list(map(lambda d: d['fresh_or_trans'], self.data['freshman_or_transfer'])) if self.data.get(
            'freshman_or_transfer') else []

    @freshman_or_transfer.setter
    def freshman_or_transfer(self, value):
        self.data['freshman_or_transfer'] = value

    @property
    def hispanic(self):
        return self.data.get('hispanic')

    @hispanic.setter
    def hispanic(self, value):
        self.data['hispanic'] = value

    @property
    def last_school_lcff_plus(self):
        return self.data.get('last_school_lcff_plus')

    @last_school_lcff_plus.setter
    def last_school_lcff_plus(self, value):
        self.data['last_school_lcff_plus'] = value

    @property
    def re_entry_status(self):
        return self.data.get('re_entry_status')

    @re_entry_status.setter
    def re_entry_status(self, value):
        self.data['re_entry_status'] = value

    @property
    def residency(self):
        return list(map(lambda d: d['category'], self.data['residency'])) if self.data.get('residency') else []

    @residency.setter
    def residency(self, value):
        self.data['residency'] = value

    @property
    def special_program_cep(self):
        return list(map(lambda d: d['program'], self.data['special_program_cep'])) if self.data.get('special_program_cep') else []

    @special_program_cep.setter
    def special_program_cep(self, value):
        self.data['special_program_cep'] = value

    @property
    def student_dependents(self):
        return [d for d in self.data['student_dependents']] if self.data.get('student_dependents') else []

    @student_dependents.setter
    def student_dependents(self, value):
        self.data['student_dependents'] = value

    @property
    def student_single_parent(self):
        return self.data.get('student_single_parent')

    @student_single_parent.setter
    def student_single_parent(self, value):
        self.data['student_single_parent'] = value

    @property
    def urem(self):
        return self.data.get('urem')

    @urem.setter
    def urem(self, value):
        self.data['urem'] = value

    @property
    def xethnic(self):
        return list(map(lambda d: d['ethnic'], self.data['xethnic'])) if self.data.get('xethnic') else []

    @xethnic.setter
    def xethnic(self, value):
        self.data['xethnic'] = value
