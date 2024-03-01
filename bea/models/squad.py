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


class Squad(Enum):
    MBB = {'code': 'MBB', 'name': 'Men\'s Baseball'}
    MBB_AA = {'code': 'MBB-AA', 'name': 'Men\'s Baseball (AA)'}
    MBK = {'code': 'MBK', 'name': 'Men\'s Basketball'}
    MBK_AA = {'code': 'MBK-AA', 'name': 'Men\'s Basketball (AA)'}
    MCR = {'code': 'MCR', 'name': 'Men\'s Crew'}
    MCR_AA = {'code': 'MCR-AA', 'name': 'Men\'s Crew (AA)'}
    MFB = {'code': 'MFB', 'name': 'Football - Other'}
    MFB_AA = {'code': 'MFB-AA', 'name': 'Football (AA)'}
    MFB_DB = {'code': 'MFB-DB', 'name': 'Football, Defensive Backs'}
    MFB_DL = {'code': 'MFB-DL', 'name': 'Football, Defensive Line'}
    MFB_MLB = {'code': 'MFB-MLB', 'name': 'Football, Inside Linebackers'}
    MFB_OL = {'code': 'MFB-OL', 'name': 'Football, Offensive Line'}
    MFB_OLB = {'code': 'MFB-OLB', 'name': 'Football, Outside Linebackers'}
    MFB_QB = {'code': 'MFB-QB', 'name': 'Football, Quarterbacks'}
    MFB_RB = {'code': 'MFB-RB', 'name': 'Football, Running Backs'}
    MFB_ST = {'code': 'MFB-ST', 'name': 'Football, Special Teams'}
    MFB_TE = {'code': 'MFB-TE', 'name': 'Football, Tight Ends'}
    MFB_WR = {'code': 'MFB-WR', 'name': 'Football, Wide Receivers'}
    MGO = {'code': 'MGO', 'name': 'Men\'s Golf'}
    MGO_AA = {'code': 'MGO-AA', 'name': 'Men\'s Golf (AA)'}
    MGY = {'code': 'MGY', 'name': 'Men\'s Gymnastics'}
    MGY_AA = {'code': 'MGY-AA', 'name': 'Men\'s Gymnastics (AA)'}
    MRU = {'code': 'MRU', 'name': 'Men\'s Rugby'}
    MRU_AA = {'code': 'MRU-AA', 'name': 'Men\'s Rugby (AA)'}
    MSC = {'code': 'MSC', 'name': 'Men\'s Soccer'}
    MSC_AA = {'code': 'MSC-AA', 'name': 'Men\'s Soccer (AA)'}
    MSW = {'code': 'MSW', 'name': 'Men\'s SwimDive - Other'}
    MSW_AA = {'code': 'MSW-AA', 'name': 'Men\'s SwimDive (AA)'}
    MSW_DV = {'code': 'MSW-DV', 'name': 'Men\'s SwimDive, Divers'}
    MSW_SW = {'code': 'MSW-SW', 'name': 'Men\'s SwimDive, Swimmers'}
    MTE = {'code': 'MTE', 'name': 'Men\'s Tennis'}
    MTE_AA = {'code': 'MTE-AA', 'name': 'Men\'s Tennis (AA)'}
    MTR = {'code': 'MTR', 'name': 'Men\'s TrackCC - Other'}
    MTR_AA = {'code': 'MTR-AA', 'name': 'Men\'s TrackCC - Other'}
    MTR_DC = {'code': 'MTR-DC', 'name': 'Men\'s TrackCC, Distance CC'}
    MTR_JP = {'code': 'MTR-JP', 'name': 'Men\'s TrackCC, Jumps'}
    MTR_MD = {'code': 'MTR-MD', 'name': 'Men\'s TrackCC, Middle Dist'}
    MTR_MT = {'code': 'MTR-MT', 'name': 'Men\'s TrackCC, Multis'}
    MTR_PV = {'code': 'MTR-PV', 'name': 'Men\'s TrackCC, Pole Vault'}
    MTR_SH = {'code': 'MTR-SH', 'name': 'Men\'s TrackCC, Sprints Hurdles'}
    MTR_TH = {'code': 'MTR-TH', 'name': 'Men\'s TrackCC, Throws'}
    MWP = {'code': 'MWP', 'name': 'Men\'s Water Polo'}
    MWP_AA = {'code': 'MWP-AA', 'name': 'Men\'s Water Polo (AA)'}
    WBK = {'code': 'WBK', 'name': 'Women\'s Basketball'}
    WBK_AA = {'code': 'WBK-AA', 'name': 'Women\'s Basketball (AA)'}
    WBV = {'code': 'WBV', 'name': 'Women\'s Beach Volleyball'}
    WBV_AA = {'code': 'WBV-AA', 'name': 'Women\'s Beach Volleyball (AA)'}
    WCR = {'code': 'WCR', 'name': 'Women\'s Crew'}
    WCR_AA = {'code': 'WCR-AA', 'name': 'Women\'s Crew (AA)'}
    WFH = {'code': 'WFH', 'name': 'Women\'s Field Hockey'}
    WFH_AA = {'code': 'WFH-AA', 'name': 'Women\'s Field Hockey (AA)'}
    WGO = {'code': 'WGO', 'name': 'Women\'s Golf'}
    WGO_AA = {'code': 'WGO-AA', 'name': 'Women\'s Golf (AA)'}
    WGY = {'code': 'WGY', 'name': 'Women\'s Gymnastics'}
    WGY_AA = {'code': 'WGY-AA', 'name': 'Women\'s Gymnastics (AA)'}
    WLC = {'code': 'WLC', 'name': 'Women\'s Lacrosse'}
    WLC_AA = {'code': 'WLC-AA', 'name': 'Women\'s Lacrosse (AA)'}
    WSC = {'code': 'WSC', 'name': 'Women\'s Soccer'}
    WSC_AA = {'code': 'WSC-AA', 'name': 'Women\'s Soccer (AA)'}
    WSF = {'code': 'WSF', 'name': 'Women\'s Softball'}
    WSF_AA = {'code': 'WSF-AA', 'name': 'Women\'s Softball (AA)'}
    WSW_DV = {'code': 'WSW-DV', 'name': 'Women\'s SwimDive, Divers'}
    WSW_SW = {'code': 'WSW-SW', 'name': 'Women\'s SwimDive, Swimmers'}
    WTE = {'code': 'WTE', 'name': 'Women\'s Tennis'}
    WTR = {'code': 'WTR', 'name': 'Women\'s TrackCC - Other'}
    WTE_AA = {'code': 'WTE-AA', 'name': 'Women\'s Tennis (AA)'}
    WTR_AA = {'code': 'WTR-AA', 'name': 'Women\'s TrackCC (AA)'}
    WTR_DC = {'code': 'WTR-DC', 'name': 'Women\'s TrackCC, Distance CC'}
    WTR_JP = {'code': 'WTR-JP', 'name': 'Women\'s TrackCC, Jumps'}
    WTR_MD = {'code': 'WTR-MD', 'name': 'Women\'s TrackCC, Middle Dist'}
    WTR_MT = {'code': 'WTR-MT', 'name': 'Women\'s TrackCC, Multis'}
    WTR_PV = {'code': 'WTR-PV', 'name': 'Women\'s TrackCC, Pole Vault'}
    WTR_SH = {'code': 'WTR-SH', 'name': 'Women\'s TrackCC, Sprints Hurdles'}
    WTR_TH = {'code': 'WTR-TH', 'name': 'Women\'s TrackCC, Throws'}
    WVB = {'code': 'WVB', 'name': 'Women\'s Volleyball'}
    WVB_AA = {'code': 'WVB-AA', 'name': 'Women\'s Volleyball'}
    WWP = {'code': 'WWP', 'name': 'Women\'s Water Polo'}
    WWP_AA = {'code': 'WWP-AA', 'name': 'Women\'s Water Polo (AA)'}
