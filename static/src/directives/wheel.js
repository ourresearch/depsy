angular.module("directives.wheel", [])
.directive("wheel", function(){

    function getWheelVal(credit){
      if (credit < .08) {
        return "tiny"
      }
      else if (credit === 1) {
        return 8
      }
      else {
        return Math.floor(credit * 8)
      }


    }



    return {
      templateUrl: "directives/wheel.tpl.html",
      restrict: "EA",
      link: function(scope, elem, attrs) {

        scope.percentCredit = Math.ceil(attrs.credit * 100)
        scope.wheelData = scope.package.person_package

        scope.wheelVal = getWheelVal(attrs.credit)
        console.log("scope.package.person_package: ", scope.package)
      }
    }


  })















