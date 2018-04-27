"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


import re
from flask import current_app as app


"""A utility module collecting logic specific to the Berkeley campus."""

# This is not a complete mapping:
#  - Not all SIS-defined academic plans map to a single Degree Programs page.
#  - Not all Degree Programs pages map to a single SIS-defined academic plan.
#  - An unknown number of obsolete academic plan descriptions are still active
#    from before the CS era.
ACADEMIC_PLAN_TO_DEGREE_PROGRAM_PAGE = {
    'African American Studies': 'african-american-studies',
    'American Studies': 'american-studies',
    'Anthropology': 'anthropology',
    'Applied Mathematics': 'applied-mathematics',
    'Architecture': 'architecture',
    'Art': 'art-practice',
    'Asian Am & Asian Diasp': 'asian-american-diaspora-studies',
    'Asian Studies': 'asian-studies-multi-area',
    'Astrophysics': 'astrophysics',
    'BioE\/MSE Joint Major': 'bioengineering-materials-science-engineering-joint-major',
    'Bioengineering': 'bioengineering',
    'Buddhist Studies': 'buddhism',
    'Business Administration': 'business-administration',
    'Celtic Studies': 'celtic-studies',
    'Chem Eng\/MSE Joint Major': 'chemical-engineering-materials-science-joint-major',
    'Chem Eng\/NE Joint Major': 'chemical-engineering-nuclear-joint-major',
    'Chemical Biology': 'chemical-biology',
    'Chemical Engineering': 'chemical-engineering',
    'Chemistry': 'chemistry',
    'Chicano Studies': 'chicano-latino-studies',
    'Chinese Language': 'chinese-language',
    'City & Regional Planning': 'city-planning',
    'Civil & Environmental Eng': 'environmental-engineering',
    'Civil Engineering': 'civil-engineering',
    'Classical Civilizations': 'classical-civilizations',
    'Classical Languages': 'classical-languages',
    'Cognitive Science': 'cognitive-science',
    'Comparative Literature': 'comparative-literature',
    'Computer Science': 'computer-science',
    'Conserv & Resource Stds': 'conservation-resource-studies',
    'Dance & Perf Studies': 'dance-performance-studies',
    'Demography': 'demography',
    'Development Studies': 'development-studies',
    'Dutch Studies': 'dutch-studies',
    'Earth & Planetary Science': 'earth-planetary-science',
    'Economics': 'economics',
    'Education': 'education',
    'Electrical Eng & Comp Sci': 'electrical-engineering-computer-sciences',
    'Energy & Resources': 'energy-resources',
    'Energy Engineering': 'energy-engineering',
    'Eng Math & Statistics': 'engineering-math-statistics',
    'Engineering Physics': 'engineering-physics',
    'English': 'english',
    'Environ Econ & Policy': 'environmental-economics-policy',
    'Environmental Eng Science': 'environmental-engineering-science',
    'Environmental Sciences': 'environmental-sciences',
    'Ethnic Studies': 'ethnic-studies',
    'Film': 'film',
    'Forestry & Natural Res': 'forestry-natural-resources',
    'French': 'french',
    'Gender & Womens Studies': 'gender-womens-studies',
    'Genetics & Plant Biology': 'genetics-plant-biology',
    'Geography': 'geography',
    'Geology': 'geology',
    'Geophysics': 'geophysics',
    'German': 'german',
    'Global Studies': 'global-studies',
    'Greek': 'greek',
    'Hispanic Lang': 'hispanic-languages-linguistics-bilingualism',
    'History of Art': 'art-history',
    'History': 'history',
    'Industrial Eng & Ops Rsch': 'industrial-engineering-operations-research',
    'Integrative Biology': 'integrative-biology',
    'Interdisciplinary Studies': 'interdisciplinary-studies',
    'Italian': 'italian-studies',
    'Japanese Language': 'japanese-language',
    'Jewish Studies': 'jewish-studies',
    'Journalism': 'journalism',
    'Landscape Architecture': 'landscape-architecture',
    'Latin American Studies': 'latin-american-studies',
    'Latin': 'latin',
    'Legal Studies': 'legal-studies',
    'Linguistics': 'linguistics',
    'Materials Science & Eng': 'materials-science-engineering',
    'Mathematics': 'mathematics',
    'MCB-Biochem & Mol Biol': 'molecular-cell-biology-biochemistry',
    'MCB-Cell & Dev Biology': 'molecular-cell-biology-developmental',
    'MCB-Neurobiology': 'molecular-cell-biology-neurobiology',
    'ME\/NE Joint Major': 'mechanical-engineering-nuclear',
    'Mechanical Engineering': 'mechanical-engineering',
    'Media Studies': 'media-studies',
    'Medieval Studies': 'medieval-studies',
    'Microbial Biology': 'microbial-biology',
    'Middle Eastern Studies': 'middle-eastern-studies',
    'Molecular Environ Biology': 'molecular-environmental-biology',
    'MSE\/ME Joint Major': 'materials-science-engineering-mechanical-joint-major',
    'MSE\/NE Joint Major': 'materials-science-engineering-nuclear-joint-major',
    'Music': 'music',
    'Native American Studies': 'native-american-studies',
    'Near Eastern Studies': 'near-eastern-civilizations',
    'Nuclear Engineering': 'nuclear-engineering',
    'Nut Sci-Physio & Metabol': 'nutritional-science',
    'Nutritional Sci-Toxicology': 'nutritional-science',
    'Nutritional Science': 'nutritional-science',
    'Peace & Conflict Studies': 'peace-conflict-studies',
    'Philosophy': 'philosophy',
    'Physics': 'physics',
    'Political Economy': 'political-economy',
    'Political Science': 'political-science',
    'Psychology': 'psychology',
    'Public Health': 'public-health',
    'Public Policy': 'public-policy',
    'Religious Studies': 'religious-studies',
    'Rhetoric': 'rhetoric',
    'Scandinavian': 'scandinavian',
    'Science & Math Education': 'science-math-education',
    'Slavic Lang & Lit': 'czech-polish-bosnian-croatian-serbian-language-literature',
    'Social Welfare': 'socialwelfare',
    'Society and Environment': 'society-environment',
    'Sociology': 'sociology',
    'South & SE Asian Studies': 'south-southeast-asian-studies',
    'Span-Spanish Lang & Lit': 'languages-literatures-cultures-spanish-speaking-world',
    'Spanish': 'languages-literatures-cultures-spanish-speaking-world',
    'Statistics': 'statistics',
    'Sustainable Environ Dsgn': 'sustainable-environmental-design',
    'Theater & Perf Studies': 'theater-performance-studies',
    'Urban Studies': 'urban-studies',
}

BERKELEY_DEPT_NAME_TO_CODE = {
    'Athletic Study Center': 'UWASC',
    'Electrical Engineering and Computer Science': 'EHEEC',
}


def current_term_id():
    term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    return sis_term_id_for_name(term_name)


def all_term_ids():
    """Return SIS IDs of each term covered by BOAC, from current to oldest."""
    earliest_term_id = int(sis_term_id_for_name(app.config['CANVAS_EARLIEST_TERM']))
    term_id = int(current_term_id())
    ids = []
    while term_id >= earliest_term_id:
        ids.append(str(term_id))
        term_id -= 4 if (term_id % 10 == 2) else 3
    return ids


def sis_term_id_for_name(term_name=None):
    if term_name:
        match = re.match(r'\A(Spring|Summer|Fall) 20(\d{2})\Z', term_name)
        if match:
            season_codes = {
                'Spring': '2',
                'Summer': '5',
                'Fall': '8',
            }
            return '2' + match.group(2) + season_codes[match.group(1)]


def term_name_for_sis_id(sis_id=None):
    if sis_id:
        sis_id = str(sis_id)
        season_codes = {
            '2': 'Spring',
            '5': 'Summer',
            '8': 'Fall',
        }
        return season_codes[sis_id[3:4]] + ' 20' + sis_id[1:3]


def degree_program_url_for_major(plan_description):
    matched = next(
        (k for k in ACADEMIC_PLAN_TO_DEGREE_PROGRAM_PAGE.keys() if re.match(r'^' + re.escape(k) + r' (BA|BS)', plan_description)),
        None,
    )
    if matched:
        return f'http://guide.berkeley.edu/undergraduate/degree-programs/{ACADEMIC_PLAN_TO_DEGREE_PROGRAM_PAGE[matched]}/'
    else:
        return None


def extract_canvas_ccn(canvas_course_section):
    # Manually created site sections will have no integration ID.
    canvas_sis_section_id = canvas_course_section.get('sis_section_id') or ''
    ccn_match = re.match(r'\ASEC:20\d{2}-[BCD]-(\d{5})', canvas_sis_section_id)
    return ccn_match.group(1) if ccn_match else None


def is_authorized_to_use_boac(user):
    authorized = False
    if user.is_admin:
        authorized = True
    elif len(user.department_memberships):
        for m in user.department_memberships:
            authorized = m.is_advisor or m.is_director
            if authorized:
                break
    return authorized
