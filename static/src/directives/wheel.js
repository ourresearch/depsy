angular.module("directives.wheel", [])
.directive("wheel", function(){

    function getWheelVal(credit){
      if (credit <= (1/16)) {
        return "tiny"
      }

      else if (credit >= (15/16) && credit < 1) {
        return "nearly-all"
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
          var personPackage = scope.person_package
        }
        else if (scope.package){
          var personPackage = scope.package

        }

        if (attrs.popoverRight){
          scope.popoverRight = true
        }
        else {
          scope.popoverRight = false
        }

        scope.percentCredit = Math.min(
            100,
            Math.ceil(personPackage.person_package_credit * 100)
        )

        scope.wheelVal = getWheelVal(personPackage.person_package_credit)
        scope.wheelData = personPackage

      }
    }


  })















