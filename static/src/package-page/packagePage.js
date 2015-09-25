angular.module('packagePage', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/package/:language/:package_name', {
      templateUrl: 'package-page/package-page.tpl.html',
      controller: 'PackagePageCtrl',
      resolve: {
        packageResp: function($http, $route, PackageResource){
          return PackageResource.get({
            namespace: $route.current.params.language,
            name: $route.current.params.package_name
          }).$promise
        }
      }
    })
  })



  .controller("PackagePageCtrl", function($scope,
                                          $routeParams,
                                          packageResp){
    $scope.package = packageResp
    $scope.depNode = packageResp.rev_dep_nodes
    console.log("retrieved the package revdepstree!", packageResp.rev_deps_tree)







  })



