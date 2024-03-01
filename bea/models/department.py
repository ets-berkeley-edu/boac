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

from enum import Enum


class Department(Enum):

    ADMIN = {
        'code': 'ADMIN',
        'name': 'Admins',
        'export_name': None,
        'notes_only': False,
    }
    ASC = {
        'code': 'UWASC',
        'name': 'Athletic Study Center',
        'export_name': None,
        'notes_only': False,
    }
    CHEM = {
        'code': 'CDCDN',
        'name': 'College of Chemistry',
        'export_name': None,
        'notes_only': False,
    }
    COE = {
        'code': 'COENG',
        'name': 'College of Engineering',
        'export_name': None,
        'notes_only': False,
    }
    ENV_DESIGN = {
        'code': 'DACED',
        'name': 'College of Environmental Design',
        'export_name': None,
        'notes_only': False,
    }
    GUEST = {
        'code': 'GUEST',
        'name': 'Guest Access',
        'export_name': 'Guest',
        'notes_only': False,
    }
    HAAS = {
        'code': 'BAHSB',
        'name': 'Haas School of Business',
        'export_name': None,
        'notes_only': False,
    }
    L_AND_S = {
        'code': 'QCADV',
        'name': 'College of Letters & Science',
        'export_name': 'L&S College Advising',
        'notes_only': False,
    }
    L_AND_S_MAJ = {
        'code': 'QCADVMAJ',
        'name': 'Letters & Science Major Advisors',
        'export_name': 'L&S Major Advising',
        'notes_only': False,
    }
    NAT_RES = {
        'code': 'MANRD',
        'name': 'College of Natural Resources',
        'export_name': None,
        'notes_only': False,
    }
    NOTES_ONLY = {
        'code': 'NOTESONLY',
        'name': 'Notes Only',
        'export_name': None,
        'notes_only': True,
    }
    OTHER = {
        'code': 'ZZZZZ',
        'name': 'Other',
        'export_name': None,
        'notes_only': False,
    }
    ZCEEE = {
        'code': 'ZCEEE',
        'name': 'Centers for Educational Equity and Excellence',
        'export_name': None,
        'notes_only': False,
    }
