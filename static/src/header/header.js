angular.module('header', [
  ])



  .controller("headerCtrl", function($scope,
                                     $http){



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






