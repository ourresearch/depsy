angular.module('profilePage', [
    'ngRoute',
    'profileService',
    "directives.languageIcon"
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/u/:slug', {
      templateUrl: 'profile-page/profile.tpl.html',
      controller: 'profilePageCtrl',
      resolve: {
        profileResp: function($http, $route){
          var url = "/api/u/" + $route.current.params.slug
          return $http.get(url)
        }
      }
    })
  })



  .controller("profilePageCtrl", function($scope,
                                          $routeParams,
                                          CurrentUser,
                                          GlobalModal,
                                          profileResp){
    $scope.profile = profileResp.data
    console.log("retrieved the profile", $scope.profile)


  })


