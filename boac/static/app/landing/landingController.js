(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authService, cohortFactory, watchlistFactory, $rootScope, $scope) {

    $scope.isLoading = true;
    $scope.isAuthenticated = authService.isAuthenticatedUser();

    var extendSortableNames = function(students) {
      return _.map(students, function(student) {
        return _.extend(student, {
          sortableName: student.lastName + ', ' + student.firstName
        });
      });
    };

    var init = function() {
      if ($scope.isAuthenticated) {
        cohortFactory.getTeams().then(function(teamsResponse) {
          $scope.teams = teamsResponse.data;

          cohortFactory.getMyCohorts().then(function(cohortsResponse) {
            $scope.myCohorts = [];
            _.each(cohortsResponse.data, function(cohort) {
              if (cohort.alerts.length) {
                var students = extendSortableNames(cohort.alerts);
                cohort.alerts = {
                  students: students,
                  sortBy: 'sortableName',
                  reverse: false
                };
              }
              $scope.myCohorts.push(cohort);
            });

            watchlistFactory.getMyWatchlist().then(function(response) {
              $scope.myWatchlist = {
                students: extendSortableNames(response.data),
                sortBy: 'sortableName',
                reverse: false
              };
              $scope.isLoading = false;
            });
          });
        });
      } else {
        $scope.isLoading = false;
      }
    };

    $rootScope.$on('devAuthFailure', function() {
      $scope.alertMessage = 'Log in failed. Please try again.';
    });

    $rootScope.$on('watchlistRemoval', function(event, sidRemoved) {
      $scope.myWatchlist.students = _.reject($scope.myWatchlist.students, ['sid', sidRemoved]);
    });

    init();
  });

}(window.angular));
