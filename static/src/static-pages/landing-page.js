angular.module('staticPages', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/', {
      redirectTo: "/leaderboard"
    })
  })







