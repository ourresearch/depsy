angular.module('top', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/top/:type', {
      templateUrl: 'top/top.tpl.html',
      controller: 'TopController',
      resolve: {
        leaders: function($http, $route, Leaders){
          console.log("getting rankees")
          return Leaders.get(
            {
              type: $route.current.params.type,
              filters: null,
              sort: null
            },
            function(resp){
              console.log("got a resp from leaders call", resp.list)
            }
          ).$promise
        }
      }
    })
  })


  .controller("TopController", function($scope,
                                          $http,
                                          $rootScope,
                                          $routeParams,
                                          leaders){

    console.log("i'm in hte top page ctrl", $routeParams)
    $scope.leaders = leaders














  })
