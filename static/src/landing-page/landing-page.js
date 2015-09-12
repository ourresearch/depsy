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
                                          $rootScope,
                                          PageService){


    $scope.doSearch = function(val){
      console.log("val", val)
      return $http.get("/api/search/" + val)
        .then(
          function(resp){
            console.log("this is the response", resp)
            var names = _.pluck(resp.data.list, "name")
            console.log(names)
            return names
          }
        )
    }





  })


