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
    authService,
    studentFactory,
    utilService
  ) {

    /**
     * @return {Array}    List of cohort filter-criteria, available to current user, with defining attributes.
     */
    var filterDefinitions = function() {
      var me = authService.getMe();
      var ref = [
        {
          available: me.isAdmin || authService.isCoeUser(),
          defaultValue: [],
          depth: 2,
          key: 'advisorLdapUid',
          name: 'Advisor',
          handler: utilService.asArray,
          param: 'a'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          key: 'gpaRanges',
          handler: utilService.asArray,
          name: 'GPA',
          param: 'g'
        },
        {
          available: me.isAdmin || authService.isAscUser(),
          defaultValue: false,
          depth: 1,
          handler: utilService.lenientBoolean,
          key: 'isInactiveAsc',
          name: 'Inactive',
          param: 'v'
        },
        {
          available: me.isAdmin || authService.isAscUser(),
          defaultValue: false,
          depth: 1,
          handler: utilService.lenientBoolean,
          key: 'inIntensiveCohort',
          name: 'Intensive',
          param: 'i'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          handler: utilService.asArray,
          key: 'levels',
          name: 'Levels',
          param: 'l'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          handler: utilService.asArray,
          key: 'majors',
          name: 'Majors',
          param: 'm'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          handler: utilService.asArray,
          key: 'unitRanges',
          name: 'Units',
          param: 'u'
        }
      ];

      return _.filter(ref, 'available');
    };

    var getCohortIdFromLocation = function() {
      return parseInt($location.search().c, 10);
    };

    var getCriteriaFromLocation = function() {
      var queryArgs = _.clone($location.search());
      var criteria = {};

      _.each(filterDefinitions, function(c) {
        criteria[c.filter] = c.handler(queryArgs[c.param]);
      });
      return criteria;
    };

    var updateLocation = function(filterCriteria) {
      // Clear browser location then update
      $location.url($location.path());

      _.each(filterCriteria, function(value, filterName) {
        var definition = _.find(filterDefinitions, ['filter', filterName]);
        if (definition && !_.isNil(value)) {
          $location.search(definition.param, value);
        }
      });
    };

    /**
     * @param  {Array}     allOptions     All options of dropdown
     * @param  {Function}  isSelected     Determines value of 'selected' property
     * @return {void}
     */
    var setSelected = function(allOptions, isSelected) {
      _.each(allOptions, function(option) {
        if (option) {
          option.selected = isSelected(option);
        }
      });
    };

    /**
     * @param  {String}    menuName      For example, 'majors'
     * @param  {Object}    optionGroup   Menu represents a group of options (see option-group definition)
     * @return {void}
     */
    var onClickMajorOptionGroup = function(menuName, optionGroup) {
      if (menuName === 'majors') {
        if (optionGroup.selected) {
          if (optionGroup.name === 'Declared') {
            // If user selects "Declared" then all other checkboxes are deselected
            $scope.search.count.majors = 1;
            setSelected($scope.search.options.majors, function(major) {
              return major.name === optionGroup.name;
            });
          } else if (optionGroup.name === 'Undeclared') {
            // If user selects "Undeclared" then "Declared" is deselected
            manualSetSelected(menuName, 'Declared', false);
            onClickOption(menuName, optionGroup);
          }
        } else {
          onClickOption(menuName, optionGroup);
        }
      }
    };

    var getMajors = function(callback) {
      studentFactory.getRelevantMajors().then(function(majorsResponse) {
        // Remove '*-undeclared' options in favor of generic 'Undeclared'
        var majors = _.filter(majorsResponse.data, function(major) {
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
            onClick: onClickMajorOptionGroup
          },
          {
            name: 'Undeclared',
            onClick: onClickMajorOptionGroup
          },
          null
        );
        return callback(majors);
      });
    };

    /**
     * @param   {Function}    callback    Standard callback
     * @returns {Array}                   Available filter-criteria with populated menu options.
     */
    var getFilterDefinitions = function(callback) {
      getMajors(function(majors) {
        var definitions = filterDefinitions();

        _.find(definitions, ['key', 'majors']).options = majors;
        _.find(definitions, ['key', 'gpaRanges']).options = studentFactory.getGpaRanges();
        _.find(definitions, ['key', 'levels']).options = studentFactory.getStudentLevels();
        _.find(definitions, ['key', 'unitRanges']).options = studentFactory.getUnitRanges();

        return callback(definitions);
      });
    };

    return {
      filterDefinitions: filterDefinitions,
      getCohortIdFromLocation: getCohortIdFromLocation,
      getCriteriaFromLocation: getCriteriaFromLocation,
      getFilterDefinitions: getFilterDefinitions,
      getMajors: getMajors,
      updateLocation: updateLocation
    };

  });
}(window.angular));
