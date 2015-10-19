angular.module("directives.wheel", [])
.directive("wheel", function(){

    function getWheelVal(credit){
      console.log("testing credit", credit)
      if (credit <= .081) {
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

        if (scope.contrib){
          var personPackage = scope.contrib
        }
        else if (scope.package){
          var personPackage = scope.package

        }

        console.log("personPackage", personPackage)
        scope.percentCredit = Math.floor(personPackage.person_package_credit * 100)
        scope.wheelVal = getWheelVal(personPackage.person_package_credit)

        scope.wheelData = personPackage

      }
    }


  })















