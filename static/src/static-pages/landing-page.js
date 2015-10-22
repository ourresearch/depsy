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

  .controller("StaticPageCtrl", function($scope, $sce, $http, ngProgress){

      console.log("getting readme...")
      $http.get("/api/readme").then(
          function(resp){
            console.log("readme:", resp.data.readme)
            $scope.readme = $sce.trustAsHtml(resp.data.readme)
            ngProgress.complete()
          },
          function(resp){
            alert("Sorry, there was an error getting this page!")
            ngProgress.complete()
          }

      )

  })










