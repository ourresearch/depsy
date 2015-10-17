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
      template: "<img class='wheel' src='static/img/wheel/{{ wheelVal }}.png' />",
      restrict: "EA",
      link: function(scope, elem, attrs) {


        scope.wheelVal = getWheelVal(attrs.credit)
        console.log("running the wheel directive. credit: ", attrs.credit, scope.wheelVal)
      }
    }


  })















