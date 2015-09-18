angular.module('top', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/packages/top', {
      templateUrl: 'top/top-packages.tpl.html',
      controller: 'topPageCtrl',
      resolve: {
        packages: function($http, $route){
          var url = "/api/packages?filter=language:python" + $route.current.params.person_id
          return $http.get(url)
        }
      }
    })
  })


  .controller("topPageCtrl", function($scope,
                                          $http,
                                          $rootScope,
                                          PageService){

    console.log("i'm in hte top page ctrl")












  })
