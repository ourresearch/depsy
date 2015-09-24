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
    console.log("retrieved the package revdepstree!", packageResp.rev_deps_tree)




      function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'From');
        data.addColumn('string', 'To');
        data.addColumn('number', 'Weight');
        data.addRows(packageResp.rev_deps_tree);

        // Sets chart options.
        var options = {
          width: 600,
          sankey: {
            iterations: 10000
          }
        };

        // Instantiates and draws our chart, passing in some options.
        var chart = new google.visualization.Sankey(document.getElementById('sankey_basic'));
        chart.draw(data, options);
      }

    drawChart()



  })



