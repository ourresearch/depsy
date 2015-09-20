angular.module('packageSnippet', [
  ])



  .controller("packageSnippetCtrl", function($scope){

    $scope.package = $scope.leader

    var packagePairs = _.pairs($scope.package)
    var subScores = _.filter(packagePairs, function(packagePair){
      return packagePair[0].indexOf("_percentile") > 0
    })

    var subScoresSum =  _.reduce(
      _.map(subScores, function(x){return x[1]}),
      function(memo, num){ return memo + num; },
      0
    )

    var subScoreRatios = _.map(subScores, function(subScore){

      var rawVal = subScore[1]
      var val
      if (!rawVal){
        val = 0
      }
      else {
        val = rawVal / subScoresSum
      }

      return {
        name: subScore[0],
        val: val
      }
    })

    $scope.subScoreRatios = subScoreRatios






    $scope.floor = function(num){
      return Math.floor(num)
    }

  })

