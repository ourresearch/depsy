angular.module('app', [
  // external libs
  'ngRoute',
  'ngResource',
  'ui.bootstrap',

  'templates.app',  // this is how it accesses the cached templates in ti.js

  'landingPage',
  'profilePage',
  'articlePage',
  'header',

  'resourcesModule',
  'pageService',
  'globalModal'

]);




angular.module('app').config(function ($routeProvider,
                                       $locationProvider) {
  $locationProvider.html5Mode(true);


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
  PageService,
  GlobalModal){



  $scope.page = PageService



  /*
  $scope.$on('$routeChangeError', function(event, current, previous, rejection){
    RouteChangeErrorHandler.handle(event, current, previous, rejection)
  });
  */

  $scope.$on('$routeChangeSuccess', function(next, current){
    PageService.reset()
  })

  $scope.$on('$locationChangeStart', function(event, next, current){
  })


});

