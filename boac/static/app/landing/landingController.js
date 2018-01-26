(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authService, cohortFactory, watchlistFactory, $rootScope, $scope) {

    $scope.isLoading = true;
    $scope.isAuthenticated = authService.isAuthenticatedUser();

    var init = function() {
      if ($scope.isAuthenticated) {
        cohortFactory.getTeams().then(function(teamsResponse) {
          $scope.teams = teamsResponse.data;

          cohortFactory.getMyCohorts().then(function(cohortsResponse) {
            $scope.myCohorts = [];
            _.each(cohortsResponse.data, function(cohort) {
              if (cohort.alerts.length) {
                var students = _.map(cohort.alerts, function(student) {
                  return _.extend(student, {
                    name: student.firstName + ' ' + student.lastName
                  });
                });
                cohort.alerts = {
                  students: students,
                  sortBy: 'name',
                  reverse: false
                };
              }
              $scope.myCohorts.push(cohort);
            });

            watchlistFactory.getMyWatchlist().then(function(response) {
              $scope.myWatchlist = {
                students: response.data,
                sortBy: 'name',
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
