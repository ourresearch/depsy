angular.module('top', [
    'ngRoute',
    'filterService'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/leaderboard', {
      templateUrl: 'top/top.tpl.html',
      controller: 'TopController',
      resolve: {

      }
    })
  })


  .controller("TopController", function($scope,
                                          $http,
                                          $rootScope,
                                          $routeParams,
                                          Leaders,
                                          FilterService){
    FilterService.setFromUrl()
    $scope.filters = FilterService

    getLeaders()

    function getLeaders(){
      console.log("getLeaders() go")

      Leaders.get(
        FilterService.filters,
        function(resp){
          console.log("got a resp from leaders call", resp.list)
          $scope.leaders = resp.list
        }
      )

    }



















  })
