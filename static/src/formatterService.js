angular.module("formatterService", [])

.factory("FormatterService", function($location){

  var short = function(num){
    console.log("calling FormatterService.short()")
      // from http://stackoverflow.com/a/14994860/226013
      if (num === null){
        return 0
      }

      if (num >= 1000000) {
          return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
      }
      if (num >= 1000) {
          return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
      }

      if (num < .01) {
        return num.toExponential(1)
      }
      if (num < 1) {
        return Math.round(num * 100) / 100
      }

      return Math.floor(num);
  }

  return {
    short: short
  }
});