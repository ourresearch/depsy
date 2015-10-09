angular.module('staticPages', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/', {
      redirectTo: "/leaderboard"
    })
  })


  .config(function($routeProvider) {
    $routeProvider.when('/about', {
      templateUrl: "static-pages/about.tpl.html",
      controller: "StaticPageCtrl"
    })
  })

  .controller("StaticPageCtrl", function($scope, ngProgress){
      ngProgress.complete()
  })










