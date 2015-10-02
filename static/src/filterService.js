angular.module("filterService", [])

.factory("FilterService", function($location){

    var filters = {
      is_academic: true,
      language: "python",
      tag: null,
      type: "pacakges"
    }

    var setFromUrl = function(){
      filters.is_academic = $location.search().is_academic
      filters.tag = $location.search().tag
      filters.language = $location.search().language
      filters.type = $location.search().type
      if (!filters.language){
        set("language", "python")
      }
      if (!filters.type){
        set("type", "packages")
      }
      console.log("set filters from url", filters)
    }

    var set = function(k, v){
      filters[k] = v
      $location.search(k, v)
    }

    var unset = function(k){
      filters[k] = null
    }


  return {
    d: filters,
    set: set,
    unset: unset,
    setFromUrl: setFromUrl
  }
});