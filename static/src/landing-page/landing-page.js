angular.module('landingPage', [
    'ngRoute',
    'profileService'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl: 'landing-page/landing.tpl.html',
      controller: 'landingPageCtrl'
    })
  })


  .controller("landingPageCtrl", function($scope,
                                          $http,
                                          $auth, // from satellizer
                                          $rootScope,
                                          PageService){


    PageService.d.hasDarkBg = true




  })


