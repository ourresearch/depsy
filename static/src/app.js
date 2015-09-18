angular.module('app', [
  // external libs
  'ngRoute',
  'ngResource',
  'ui.bootstrap',
  'ngProgress',
  'ngSanitize',

  'templates.app',  // this is how it accesses the cached templates in ti.js

  'staticPages',
  'personPage',
  'articlePage',
  'header',
  'packageSnippet',

  'resourcesModule',
  'pageService',

  'top'

]);




angular.module('app').config(function ($routeProvider,
                                       $locationProvider) {
  $locationProvider.html5Mode(true);


//  paginationTemplateProvider.setPath('directives/pagination.tpl.html')
});


angular.module('app').run(function($route,
                                   $rootScope,
                                   $timeout,
                                   ngProgress,
                                   $location) {



  $rootScope.$on('$routeChangeStart', function(next, current){
    console.log("route change start")
    ngProgress.start()
  })
  $rootScope.$on('$routeChangeSuccess', function(next, current){
    console.log("route change success")
    ngProgress.complete()
  })
  $rootScope.$on('$routeChangeError', function(event, current, previous, rejection){
    console.log("$routeChangeError")
    ngProgress.complete()
  });

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
  $sce,
  PageService){



  $scope.page = PageService

  $scope.nFormatter = function(num){
      // from http://stackoverflow.com/a/14994860/226013
      if (num >= 1000000) {
          return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
      }
      if (num >= 1000) {
          return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
      }
      return Math.floor(num);
  }



  $scope.trustHtml = function(str){
    console.log("trusting html:", str)
    return $sce.trustAsHtml(str)
  }



  /*
  $scope.$on('$routeChangeError', function(event, current, previous, rejection){
    RouteChangeErrorHandler.handle(event, current, previous, rejection)
  });
  */


  $scope.$on('$locationChangeStart', function(event, next, current){
  })


});

