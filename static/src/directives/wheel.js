angular.module("directives.wheel", [])
.directive("wheel", function(){

    function getWheelVal(credit){
      console.log("testing credit", credit)
      if (credit <= (1 / 16)) {
        return "tiny"
      }

      else {
        return Math.round(credit * 8)
      }


    }



    return {
      templateUrl: "directives/wheel.tpl.html",
      restrict: "EA",
      link: function(scope, elem, attrs) {

        if (scope.person_package){
          console.log("personPackage = scope.person_package")
          var personPackage = scope.person_package
        }
        else if (scope.package){
          var personPackage = scope.package

        }

        console.log("personPackage", personPackage)
        scope.percentCredit = Math.ceil(personPackage.person_package_credit * 100)
        scope.wheelVal = getWheelVal(personPackage.person_package_credit)

        scope.wheelData = personPackage

      }
    }


  })















