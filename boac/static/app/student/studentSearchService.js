/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

(function(angular) {

  'use strict';

  angular.module('boac').service('studentSearchService', function(utilService, studentFactory, $location) {

    var getSortByOptionsForSearch = function() {
      return {
        options: [
          {name: 'First Name', value: 'first_name'},
          {name: 'Last Name', value: 'last_name'},
          {name: 'Team', value: 'group_name'},
          {name: 'GPA', value: 'gpa'},
          {name: 'Level', value: 'level'},
          {name: 'Major', value: 'major'},
          {name: 'Units', value: 'units'}
        ],
        selected: 'last_name'
      };
    };

    /**
     * Use selected filter options to query students API.
     *
     * @param  {Object}      opts                        Search criteria: gpaRanges, levels, etc.
     * @param  {String}      orderBy                     Requested sort order
     * @param  {Number}      offset                      As used in SQL query
     * @param  {Number}      limit                       As used in SQL query
     * @param  {Number}      updateBrowserLocation       If true, we will update search criteria in browser location URL
     * @return {List}                                    Backend API results
     */
    var getStudents = function(opts, orderBy, offset, limit, updateBrowserLocation) {
      var getValues = utilService.getValuesSelected;
      // Get values where selected=true
      var gpaRanges = getValues(opts.gpaRanges);
      var groupCodes = getValues(opts.groupCodes, 'groupCode');
      var levels = getValues(opts.levels);
      var majors = getValues(opts.majors);
      var unitRanges = getValues(opts.unitRanges);

      if (updateBrowserLocation) {
        $location.search('c', 'search');
        $location.search('g', gpaRanges);
        // Use string 'true' rather than boolean so that the value persists in browser location.
        $location.search('i', opts.intensive ? 'true' : null);
        $location.search('inactive', opts.inactive ? 'true' : null);
        $location.search('l', levels);
        $location.search('m', majors);
        $location.search('t', groupCodes);
        $location.search('u', unitRanges);
      }
      return studentFactory.getStudents(
        gpaRanges,
        groupCodes,
        levels,
        majors,
        unitRanges,
        opts.intensive,
        opts.inactive,
        orderBy,
        offset,
        limit
      );
    };

    return {
      getSortByOptionsForSearch: getSortByOptionsForSearch,
      getStudents: getStudents
    };
  });

}(window.angular));
