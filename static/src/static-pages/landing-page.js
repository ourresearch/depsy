angular.module('staticPages', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl: 'static-pages/landing.tpl.html',
      controller: 'landingPageCtrl'
    })
  })


  .controller("landingPageCtrl", function($scope,
                                          $http,
                                          $rootScope,
                                          PageService){








  })






