angular.module('header', [
  ])



  .controller("headerCtrl", function($scope,
                                     $location,
                                     $rootScope,
                                     $http){



    $scope.searchResultSelected = ''

    $rootScope.$on('$routeChangeSuccess', function(next, current){
      $scope.searchResultSelected = ''
    })
    $rootScope.$on('$routeChangeError', function(event, current, previous, rejection){
      $scope.searchResultSelected = ''
    });


    $scope.onSelect = function(item ){
      console.log("select!", item)
      if (item.type=='pypi_project') {
        $location.path("package/python/" + item.name)
      }
      else if (item.type=='cran_project') {
        $location.path("package/r/" + item.name)
      }
      else if (item.type=='person') {
        $location.path("person/" + item.id)
      }
      else if (item.type=='tag') {
        $location.path("tag/" + item.name)
      }
    }

    $scope.doSearch = function(val){
      console.log("doing search")
      return $http.get("/api/search/" + val)
        .then(
          function(resp){
            console.log("this is the response", resp)
            return resp.data.list

            var names = _.pluck(resp.data.list, "name")
            console.log(names)
            return names
          }
        )
    }

  })

.controller("searchResultCtrl", function($scope, $sce){

    $scope.trustHtml = function(str){
      console.log("trustHtml got a thing", str)

      return $sce.trustAsHtml(str)
    }




  })






