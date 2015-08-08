angular.module('app', [
  // external libs
  'ngRoute',
  'ngResource',
  'ui.bootstrap',
  'satellizer',
  'snap', // hosted locally

  'templates.app',  // this is how it accesses the cached templates in ti.js

  'landingPage',
  'profilePage',
  'articlePage',

  'resourcesModule',
  'currentUserService',
  'pageService'

]);




angular.module('app').config(function ($routeProvider,
                                       $authProvider, // from satellizer
                                       snapRemoteProvider,
                                       $locationProvider) {
  $locationProvider.html5Mode(true);
  $authProvider.github({
    clientId: '46b1f697afdd04e119fb' // hard-coded for now
  });
  snapRemoteProvider.globalOptions.disable = 'left';


//  paginationTemplateProvider.setPath('directives/pagination.tpl.html')
});


angular.module('app').run(function($route,
                                   $rootScope,
                                   $timeout,
                                   $location ) {

  /*
  this lets you change the args of the URL without reloading the whole view. from
     - https://github.com/angular/angular.js/issues/1699#issuecomment-59283973
     - http://joelsaupe.com/programming/angularjs-change-path-without-reloading/
     - https://github.com/angular/angular.js/issues/1699#issuecomment-60532290
  */
  var original = $location.path;
  $location.path = function (path, reload) {
      if (reload === false) {
          var lastRoute = $route.current;
          var un = $rootScope.$on('$locationChangeSuccess', function () {
              $route.current = lastRoute;
              un();
          });
        $timeout(un, 500)
      }
      return original.apply($location, [path]);
  };

});


angular.module('app').controller('AppCtrl', function(
  $rootScope,
  $scope,
  $location,
  snapRemote,
  PageService,
  CurrentUser,
  $auth){

  $scope.isAuthenticated = function() {
    return $auth.isAuthenticated();
  };


  $scope.authenticate = function() {
    $auth.authenticate("github").then(function(resp){
      console.log("authenticated!", resp)
      $location.path("/u/" + resp["username"])
      CurrentUser.get()
    })
  };


  $scope.page = PageService
  CurrentUser.get()


  /*
  $scope.$on('$routeChangeError', function(event, current, previous, rejection){
    RouteChangeErrorHandler.handle(event, current, previous, rejection)
  });
  */

  $scope.$on('$routeChangeSuccess', function(next, current){
    snapRemote.close()
    PageService.reset()
  })

  $scope.$on('$locationChangeStart', function(event, next, current){
  })


});

