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

  angular.module('boac').service('filterCriteriaService', function(
    $location,
    athleticsFactory,
    authService,
    filterCriteriaFactory,
    studentFactory,
    userFactory
  ) {

    var getCohortIdFromLocation = function() {
      return parseInt($location.search().c, 10);
    };

    var getFilterCriteriaFromLocation = function() {
      var queryArgs = _.clone($location.search());
      var filterCriteria = {};

      _.each(filterCriteriaFactory.getFilterDefinitions(), function(d) {
        filterCriteria[d.key] = d.handler(queryArgs[d.param]);
      });
      return filterCriteria;
    };

    var updateLocation = function(filterCriteria, currentPage) {
      $location.search('page', currentPage);

      var definitions = filterCriteriaFactory.getFilterDefinitions();

      _.each(filterCriteria, function(value, key) {
        var definition = _.find(definitions, ['key', key]);
        if (definition && _.size(value)) {
          $location.search(definition.param, value);
        }
      });
    };

    var getMajors = function(onClickDeclaredUndeclared, callback) {
      studentFactory.getRelevantMajors().then(function(response) {
        // Remove '*-undeclared' options in favor of generic 'Undeclared'
        var majors = _.filter(response.data, function(major) {
          return !major.match(/undeclared/i);
        });
        majors = _.map(majors, function(name) {
          return {
            name: name,
            value: name
          };
        });
        majors.unshift(
          {
            name: 'Declared',
            value: 'Declared',
            onClick: onClickDeclaredUndeclared
          },
          {
            name: 'Undeclared',
            value: 'Undeclared',
            onClick: onClickDeclaredUndeclared
          },
          null
        );
        return callback(majors);
      });
    };

    var setMenuOptions = function(definitions, key, options) {
      _.find(definitions, ['key', key]).options = options;
    };

    /**
     * @param   {Object}      definitions         Filter definitions will be populated according to user privileges.
     * @param   {Function}    callback            Standard callback
     * @returns {Array}                           Available filter-criteria with populated menu options.
     */
    var getAvailableFilters = function(definitions, callback) {
      async.series([
        function(done) {
          getMajors(_.noop, function(majors) {
            setMenuOptions(definitions, 'majors', majors);
            setMenuOptions(definitions, 'gpaRanges', studentFactory.getGpaRanges());
            setMenuOptions(definitions, 'levels', studentFactory.getStudentLevels());
            setMenuOptions(definitions, 'unitRanges', studentFactory.getUnitRanges());

            return done();
          });
        },
        function(done) {
          if (authService.canViewAsc()) {
            athleticsFactory.getAllTeamGroups().then(function(response) {
              setMenuOptions(definitions, 'groupCodes', _.map(response.data, function(group) {
                return {
                  name: group.name,
                  value: group.groupCode
                };
              }));
              return done();
            });
          } else {
            return done();
          }
        },
        function(done) {
          if (authService.canViewCoe()) {
            // The 'Advisor' dropdown has UIDs and names
            userFactory.getProfilesPerDeptCode('COENG').then(function(response) {
              setMenuOptions(definitions, 'advisorLdapUid', _.map(response.data, function(user) {
                return {
                  name: user.firstName + ' ' + user.lastName,
                  value: user.uid
                };
              }));
              return done();
            });
          } else {
            return done();
          }
        },
        function() {
          return callback(definitions);
        }
      ]);
    };

    return {
      getCohortIdFromLocation: getCohortIdFromLocation,
      getFilterCriteriaFromLocation: getFilterCriteriaFromLocation,
      getMajors: getMajors,
      getAvailableFilters: getAvailableFilters,
      updateLocation: updateLocation
    };

  });
}(window.angular));
