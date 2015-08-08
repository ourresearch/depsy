angular.module('pageService', [
  ])



  .factory("PageService", function(){

    console.log("loaded the page service")
    var data = {}
    var defaultData = {
      hasDarkBg: false
    }

    function reset(){
      console.log("resetting the page service data")
      _.each(defaultData, function(v, k){
        data[k] = v
      })
      console.log("here's the new data", data)
    }

    return {
      d: data,
      reset: reset
    }


  })