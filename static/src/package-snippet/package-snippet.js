angular.module('packageSnippet', [
  ])



  .controller("packageSnippetCtrl", function($scope){
    $scope.package = $scope.contrib.package
    $scope.floor = function(num){
      return Math.floor(num)
    }

  })

