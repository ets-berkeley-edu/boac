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

  angular.module('boac').service('authService', function(
    $http,
    $location,
    $rootScope,
    authFactory,
    googleAnalyticsService
  ) {

    var getMe = function() {
      return _.cloneDeep($rootScope.me);
    };

    var isDepartmentMember = function(user, deptCode) {
      return _.get(user.departments, deptCode + '.isAdvisor') || _.get(user.departments, deptCode + '.isDirector');
    };

    var isAscUser = function() {
      // Athletic Study Center
      return isDepartmentMember(getMe(), 'UWASC');
    };

    var isCoeUser = function() {
      // College of Engineering
      return isDepartmentMember(getMe(), 'COENG');
    };

    var canViewAsc = function() {
      return getMe().isAdmin || isAscUser();
    };

    var canViewCoe = function() {
      return getMe().isAdmin || isCoeUser();
    };

    var reloadMe = function() {
      return $http.get('/api/status').then(authFactory.loadUserProfile).then(function() {
        var me = $rootScope.me;
        if ($rootScope.me.isAuthenticated) {
          if ($location.search().casLogin) {
            // Track CAS login event
            var uid = $rootScope.me.uid;
            googleAnalyticsService.track('user', 'login', uid, parseInt(uid, 10));
          }
        }
        return me;
      });
    };

    $rootScope.$on('filteredCohortCreated', function(event, data) {
      if (_.get($rootScope, 'me.myFilteredCohorts')) {
        $rootScope.me.myFilteredCohorts.push(data.cohort);
      }
    });

    $rootScope.$on('filteredCohortDeleted', function(event, data) {
      if (_.get($rootScope, 'me.myFilteredCohorts')) {
        $rootScope.me.myFilteredCohorts = _.remove($rootScope.me.myFilteredCohorts, function(cohort) {
          return data.cohort.id !== cohort.id;
        });
      }
    });

    $rootScope.$on('filteredCohortNameChanged', function(event, data) {
      if (_.get($rootScope, 'me.myFilteredCohorts')) {
        _.each($rootScope.me.myFilteredCohorts, function(cohort) {
          if (data.cohort.id === cohort.id) {
            cohort.name = data.cohort.name;
          }
        });
      }
    });

    $rootScope.$on('curatedCohortCreated', function(event, data) {
      if (_.get($rootScope, 'me.myCuratedCohorts')) {
        $rootScope.me.myCuratedCohorts.push(data.cohort);
      }
    });

    $rootScope.$on('curatedCohortDeleted', function(event, data) {
      if (_.get($rootScope, 'me.myCuratedCohorts')) {
        $rootScope.me.myCuratedCohorts = _.remove($rootScope.me.myCuratedCohorts, function(cohort) {
          return data.cohortId !== cohort.id;
        });
      }
    });

    $rootScope.$on('curatedCohortRenamed', function(event, data) {
      if (_.get($rootScope, 'me.myCuratedCohorts')) {
        _.each($rootScope.me.myCuratedCohorts, function(cohort) {
          if (data.cohort.id === cohort.id) {
            cohort.name = data.cohort.name;
          }
        });
      }
    });

    return {
      canViewAsc: canViewAsc,
      canViewCoe: canViewCoe,
      getMe: getMe,
      isAscUser: isAscUser,
      isCoeUser: isCoeUser,
      isDepartmentMember: isDepartmentMember,
      reloadMe: reloadMe
    };
  });

}(window.angular));
