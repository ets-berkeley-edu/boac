"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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


"""A utility module collecting logic specific to the Berkeley campus."""

ACADEMIC_STANDING_DESCRIPTIONS = {
    'DIS': 'Dismissed',
    'GST': 'Good Standing',
    'PRO': 'Probation',
    'SUB': 'Subject to Dismissal',
}

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

COE_ETHNICITIES_PER_CODE = {
    'A': 'African-American / Black',
    'B': 'Japanese / Japanese American',
    'C': 'American Indian / Alaska Native',
    'D': 'Other',
    'E': 'Mexican / Mexican-American / Chicano',
    'F': 'White / Caucasian',
    'G': 'Declined to state',
    'H': 'Chinese / Chinese-American',
    'I': 'Other Spanish-American / Latino',
    'L': 'Filipino / Filipino-American',
    'M': 'Pacific Islander',
    'P': 'Puerto Rican',
    'R': 'East Indian / Pakistani',
    'T': 'Thai / Other Asian',
    'V': 'Vietnamese',
    'X': 'Korean / Korean-American',
    'Y': 'Other Asian',
    'Z': 'Foreign',
}

BERKELEY_DEPT_CODE_TO_NAME = {
    'AIDDC': 'Univ Development and Alumni Relations',
    'AIDVO': 'VC University Relations',
    'AJPIO': 'Public Affairs',
    'AQCPE': 'CAP Physical & Environ Planning',
    'AZADM': 'Shared Services, Administration',
    'BAHSB': 'Haas School of Business',
    'BCHCI': 'Haas Centers and Institutes',
    'BMCCB': 'Center for Computational Biology',
    'BOOPT': 'School of Optometry',
    'BPOPC': 'Optometry Clinic',
    'BTCNM': 'Center for New Media',
    'BUGMS': 'Center for Global Metropolitan Studies',
    'CALTEACH': 'CalTeach Program',
    'CCHEM': 'Department of Chemistry',
    'CDCDN': 'College of Chemistry',
    'CEEEG': 'Department of Chemical and Biomolecular Engineering',
    'CELTIC': 'Celtic Studies',
    'CFPPR': 'Goldman School of Public Policy',
    'CITRIS': 'Center for Information Technology Research in the Interest of Society',
    'CITRS': 'Center for Information Technology Research in Interest of Society',
    'CLLAW': 'School of Law',
    'COENG': 'College of Engineering',
    'CPACA': 'School of Public Health',
    'CQADM': 'School of Public Health, Administration',
    'CRTHE': 'Program in Critical Theory',
    'CSDEP': 'Department of Social Welfare',
    'DACED': 'College of Environmental Design',
    'DBARC': 'Department of Architecture',
    'DCCRP': 'Department of City and Regional Planning',
    'DFLAE': 'Department of Landscape Architecture and Environmental Planning',
    'DJOUR': 'Department of Journalism',
    'DSDDO': 'Data Science, Admin and Ops',
    'EAEDU': 'School of Education',
    'ED1DO': 'College of Engineering, Dean\'s Office',
    'EDCFI': 'Coleman Fung Institute for Engineering Leadership',
    'EDDNO': 'Engineering Dean\'s Office',
    'EDESS': 'COENG Engineering Student Services',
    'EECS': 'Department of Electrical Engineering and Computer Sciences',
    'EERCT': 'Engineering Research Centers',
    'EERSO': 'Shared Services, Research Support',
    'EFBIO': 'Department of Bioengineering',
    'EGCEE': 'Department of Civil and Environmental Engineering',
    'EH1CS': 'Comp Sci Div Operations',
    'EH1EO': 'EECS Dept Operations',
    'EHEEC': 'Electrical Engineering and Computer Sciences',
    'EIIEO': 'Department of Industrial Engineering and Operations Research',
    'EJMSM': 'Department of Materials Science and Engineering',
    'EKMEG': 'Department of Mechanical Engineering',
    'ELNUC': 'Department of Nuclear Engineering',
    'EMECI': 'Energy and Climate Institute',
    'ENAPF': 'Undergrad Education Administration',
    'ERFEO': 'Faculty Equity & Welfare Office',
    'ERRET': 'UC Berkeley Retirement Center',
    'ESPM': 'Department of Environmental Science, Policy, and Management',
    'EUNEU': 'Helen Wills Neuroscience Institute',
    'EWSUM': 'Summer Sessions',
    'FJPPS': 'Physical Plant Campus Services',
    'FMHUM': 'Human Resources',
    'FOREC': 'Recreational Sports',
    'FSSEM': 'Freshman and Sophomore Seminars',
    'FTRAN': 'Parking & Transportation',
    'FUPOL': 'University Police',
    'FVAUX': 'ASUC Business Auxiliary',
    'FWHHS': 'Incentive Award Programs',
    'FYUHS': 'University Health Services',
    'HARTH': 'History of Art Department',
    'HCPHI': 'Department of Philosophy',
    'HDRAM': 'Department of Theater Dance and Performance Studies',
    'HENGL': 'Department of English',
    'HFREN': 'Department of French',
    'HGEAL': 'Department of East Asian Languages and Cultures',
    'HHDNO': 'Arts & Humanities, Dean\'s Office',
    'HITAL': 'Department of Italian Studies',
    'HKCLF': 'Comparative Literature and French',
    'HLCOM': 'Department of Comparative Literature',
    'HMUSC': 'Department of Music',
    'HNNES': 'Department of Near Eastern Studies',
    'HOGSP': 'German Spanish & Portuguese',
    'HPMED': 'Program in Medieval Studies',
    'HQISS': 'Italian Scandinavian & Slavic',
    'HRHET': 'Department of Rhetoric',
    'HSCAN': 'Department of Scandinavian',
    'HTAHN': 'Group in Ancient History and Mediterranean Archaeology',
    'HUFLM': 'Department of Film and Media',
    'HVSSA': 'Department of South and Southeast Asian Studies',
    'HYACD': 'UNEX Academic Departments',
    'HZGER': 'Department of German',
    'IABSS': 'Biosciences Divisional Services',
    'IBIBI': 'Department of Integrative Biology',
    'IEIRP': 'Berkeley Center for Cosmo Physics',
    'IMMCB': 'Department of Molecular and Cell Biology',
    'IMRES': 'MCB Research',
    'INCAS': 'CASMA Administration',
    'IPPEP': 'Department of Physical Education',
    'IQBBB': 'QB3 Institute',
    'ISF': 'Interdisciplinary Studies Field',
    'JAISI': 'Institute for Study of Societal Issues',
    'JICCS': 'Architecture, Platforms and Integration',
    'JYHST': 'Center for Science Technology Medicine and Society',
    'KCBCP': 'Berkeley Connect Program',
    'KDCJS': 'Center for Jewish Studies',
    'KKCAP': 'Cal Performances',
    'KNBAM': 'Art, Music & Pacific Film Archive',
    'KPADM': 'Library Administration',
    'LBEAS': 'Institute of East Asian Studies',
    'LLSIS': 'Berkeley International Office',
    'LMOIH': 'International House',
    'LORFS': 'Rhetoric & Film Studies',
    'LPSPP': 'Department of Spanish and Portuguese',
    'LQAPR': 'Department of Art Practice',
    'LSCLA': 'Department of Classics',
    'LTSLL': 'Department of Slavic Languages and Literatures',
    'MANRD': 'College of Natural Resources',
    'MBARC': 'Department of Agricultural and Resource Economics',
    'MCESP': 'Environmental Science, Policy and Management',
    'MDNST': 'Department of Nutritional Sciences and Toxicology',
    'MEDIAST': 'Media Studies',
    'MEPMB': 'Department of Plant and Microbial Biology',
    'MGERG': 'Energy and Resources Group',
    'MMIMS': 'School of Information',
    'NGITS': 'Institute of Transportation Studies',
    'NQBSL': 'Berkeley Seismological Lab',
    'NRTAC': 'Theoretical Astrophysics Center',
    'NSARF': 'Archaeological Research Facility',
    'NUIGS': 'Institute of Governmental Studies',
    'NYIHD': 'Institute of Human Development',
    'OEMPA': 'Museum of Paleontology',
    'OGHMA': 'PA Hearst Museum of Anthropology',
    'OIBOT': 'UC Botanical Garden',
    'OKLHS': 'Lawrence Hall of Science',
    'OLGDD': 'Graduate Division',
    'OUNNI': 'Nanosciences and Nanoengineering Institute',
    'PAAST': 'Department of Astronomy',
    'PCENT': 'Mathematical & Physical Sciences',
    'PDPSD': 'Physical Science, Dean\'s off',
    'PGEGE': 'Department of Earth and Planetary Science',
    'PHYSI': 'Department of Physics',
    'PMATH': 'Department of Mathematics',
    'PQPAS': 'Center for Particle Astrophysics',
    'PSTAT': 'Department of Statistics',
    'QALSD': 'Letters and Science Deans',
    'QCADV': 'L&S College Advising',
    'QCADVMAJ': 'L&S Major Advising',
    'QHUIS': 'Office of Undergraduate and Interdisciplinary Studies',
    'QHUTL': 'UGIS Teaching Programs',
    'QIIAS': 'International and Area Studies Academic Program',
    'QKCWP': 'College Writing Programs',
    'QLROT': 'Military Affairs Program',
    'SAAMS': 'Department of African American Studies',
    'SBETH': 'Department of Ethnic Studies',
    'SDDEM': 'Department of Demography',
    'SECON': 'Department of Economics',
    'SGEOG': 'Department of Geography',
    'SHIST': 'Department of History',
    'SISOC': 'Department of Sociology',
    'SLING': 'Department of Linguistics',
    'SPOLS': 'Charles and Louise Travers Department of Political Science',
    'SRIIS': 'The Social Science Matrix',
    'SWOME': 'Department of Gender and Women\'s Studies',
    'SYPSY': 'Department of Psychology',
    'SZANT': 'Department of Anthropology',
    'UACSC': 'Cal Student Central',
    'UBOSS': 'Office of Student Systems',
    'UCCEU': 'Central Evaluation Unit',
    'UCIMM': 'VCUA Immediate Office',
    'UCIMO': 'Student Affairs Office',
    'UCOP': 'University of California, Office of The President',
    'UGIS': 'Undergraduate Interdisciplinary Studies',
    'UHREG': 'Office of the Registrar',
    'UIDES': 'CEP Destination College',
    'UIUPB': 'CEP Upward Bound Program',
    'UKHDS': 'Housing & Dining Services',
    'UOSLC': 'Student Learning Center',
    'UPCAR': 'Career Center',
    'UQNAD': 'UQMSC Campus Climate, Administration',
    'URSET': 'Educational Technology Services',
    'USSAS': 'Dean of Student Centers',
    'UWASC': 'Athletic Study Center',
    'UXDSP': 'Disabled Students Program',
    'VREAS': 'Student Information Systems',
    'ZCEEE': 'Centers for Educational Equity and Excellence',
    'GUEST': 'Guest',
    'ZZZZZ': 'Other',
}

BERKELEY_DEPT_NAME_TO_CODE = {value: key for key, value in BERKELEY_DEPT_CODE_TO_NAME.items()}


BERKELEY_DEPT_CODE_TO_PROGRAM_AFFILIATIONS = {
    'BAHSB': {
        'program': 'UBUS',
    },
    'CDCDN': {
        'program': 'UCCH',
    },
    'COENG': {
        'program': 'UCOE',
    },
    'DACED': {
        'program': 'UCED',
    },
    'MANRD': {
        'program': 'UCNR',
    },
    'QCADV': {
        'program': 'UCLS',
        # DNDS ('Dean Designate') advisors get filed with college advisors.
        'affiliations': ['COLL', 'DNDS'],
    },
    'QCADVMAJ': {
        'program': 'UCLS',
        # ADVD ('Advisor Delegate') and minor advisors get filed with major advisors.
        'affiliations': ['ADVD', 'MAJ', 'MIN'],
    },
    # Our catchall 'Other' department gets stuck with empty program codes.
    'ZZZZZ': {
        'program': '',
    },
}


def previous_term_id(term_id):
    term_id = int(term_id)
    previous = term_id - (4 if (term_id % 10 == 2) else 3)
    return str(previous)


def term_ids_range(earliest_term_id, latest_term_id):
    """Return SIS ID of each term in the range, from oldest to newest."""
    term_id = int(earliest_term_id)
    ids = []
    while term_id <= int(latest_term_id):
        ids.append(str(term_id))
        term_id += 4 if (term_id % 10 == 8) else 3
    return ids


def sis_term_id_for_name(term_name=None):
    if term_name:
        match = re.match(r'\A(Spring|Summer|Fall) (\d)[09](\d{2})\Z', term_name)
        if match:
            season_codes = {
                'Spring': '2',
                'Summer': '5',
                'Fall': '8',
            }
            return match.group(2) + match.group(3) + season_codes[match.group(1)]


def term_name_for_sis_id(sis_id=None):
    if sis_id:
        sis_id = str(sis_id)
        season_codes = {
            '0': 'Winter',
            '2': 'Spring',
            '5': 'Summer',
            '8': 'Fall',
        }
        year = f'19{sis_id[1:3]}' if sis_id.startswith('1') else f'20{sis_id[1:3]}'
        return f'{season_codes[sis_id[3:4]]} {year}'


def degree_program_url_for_major(plan_description):
    matched = next(
        (k for k in ACADEMIC_PLAN_TO_DEGREE_PROGRAM_PAGE.keys() if re.match(r'^' + re.escape(k) + r' (BA|BS)', plan_description)),
        None,
    )
    if matched:
        return f'http://guide.berkeley.edu/undergraduate/degree-programs/{ACADEMIC_PLAN_TO_DEGREE_PROGRAM_PAGE[matched]}/'
    else:
        return None


def get_dept_codes(user):
    return [m.university_dept.dept_code for m in user.department_memberships] if user else None


def dept_codes_where_advising(user):
    if user:
        dept_where_advising = list(filter(lambda d: d.get('role') in ('advisor', 'director'), user.departments))
        return list(map(lambda d: d['code'], dept_where_advising))
    else:
        return None


def section_is_eligible_for_alerts(enrollment, section):
    if section.get('component') == 'LEC':
        return True
    else:
        display_name = enrollment.get('displayName')
        decal_catalog_id_pattern = re.compile(' 1?9[89][A-Z]?[A-Z]?$')
        return not decal_catalog_id_pattern.search(display_name)
