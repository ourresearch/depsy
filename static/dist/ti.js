/* yay impactstory */
angular.module('app', [
  // external libs
  'ngRoute',
  'ngResource',
  'ui.bootstrap',
  'ngProgress',
  'ngSanitize',

  'templates.app',  // this is how it accesses the cached templates in ti.js

  'staticPages',
  'personPage',
  'tagPage',
  'packagePage',
  'header',
  'snippet',

  'resourcesModule',
  'pageService',
  'formatterService',

  'top'

]);




angular.module('app').config(function ($routeProvider,
                                       $locationProvider) {
  $locationProvider.html5Mode(true);


//  paginationTemplateProvider.setPath('directives/pagination.tpl.html')
});


angular.module('app').run(function($route,
                                   $rootScope,
                                   $timeout,
                                   ngProgress,
                                   $location) {



  $rootScope.$on('$routeChangeStart', function(next, current){
    console.log("route change start")
    ngProgress.start()
  })
  $rootScope.$on('$routeChangeSuccess', function(next, current){
    console.log("route change success")
    window.scrollTo(0, 0)
//    ngProgress.complete()
  })
  $rootScope.$on('$routeChangeError', function(event, current, previous, rejection){
    console.log("$routeChangeError")
    window.scrollTo(0, 0)
    ngProgress.complete()
  });


  // from http://cwestblog.com/2012/09/28/javascript-number-getordinalfor/
  (function(o) {
    Number.getOrdinalFor = function(intNum, includeNumber) {
      return (includeNumber ? intNum : "")
        + (o[((intNum = Math.abs(intNum % 100)) - 20) % 10] || o[intNum] || "th");
    };
  })([,"st","nd","rd"]);



  /*
  this lets you change the args of the URL without reloading the whole view. from
     - https://github.com/angular/angular.js/issues/1699#issuecomment-59283973
     - http://joelsaupe.com/programming/angularjs-change-path-without-reloading/
     - https://github.com/angular/angular.js/issues/1699#issuecomment-60532290
  */
  var original = $location.path;
  $location.path = function (path, reload) {
      if (reload === false) {
          var lastRoute = $route.current;
          var un = $rootScope.$on('$locationChangeSuccess', function () {
              $route.current = lastRoute;
              un();
          });
        $timeout(un, 500)
      }
      return original.apply($location, [path]);
  };




});


angular.module('app').controller('AppCtrl', function(
  $rootScope,
  $scope,
  $location,
  $sce,
  FormatterService,
  PageService){



  $scope.page = PageService




  function toRoundedSciNotation(n){

  }

  // from http://cwestblog.com/2012/09/28/javascript-number-getordinalfor/
  $scope.getOrdinal = function(n) {
    var s=["th","st","nd","rd"],
      v=n%100;
    return n+(s[(v-20)%10]||s[v]||s[0]);
  }

  $scope.toPercentile = function(proportion){
    return $scope.getOrdinal(Math.floor(proportion * 100))
  }

  $scope.floor = function(num){
    return Math.floor(num)
  }

  $scope.round = function(num, places){
    if (!places){
      places = 0
    }

    if (!num){
      num = 0
    }

    var ret = num.toFixed(places)

    // super hack
    if (ret == "100.0") {
      ret = "99.9"
    }
    else if (ret == "100") {
      ret = "99"
    }
    return ret


    var multiplier = Math.pow(10, places)
    var rounded = Math.round(num * multiplier)  / multiplier
    if (rounded == 100) {
      console.log("rounded", rounded)
      rounded = 99.9999999
    }
    return rounded.toFixed(places)
  }


  $scope.trustHtml = function(str){
    console.log("trusting html:", str)
    return $sce.trustAsHtml(str)
  }



  /*
  $scope.$on('$routeChangeError', function(event, current, previous, rejection){
    RouteChangeErrorHandler.handle(event, current, previous, rejection)
  });
  */


  $scope.$on('$locationChangeStart', function(event, next, current){
  })


});


angular.module("directives.languageIcon", [])
.directive("languageIcon", function(){


  var hueFromString = function(str) {
      var hash = 0;
      if (str.length == 0) return hash;
      for (var i = 0; i < str.length; i++) {
          hash = str.charCodeAt(i) + ((hash << 5) - hash);
          hash = hash & hash; // Convert to 32bit integer
      }
      return hash % 360;
  };

    return {
      templateUrl: "directives/language-icon.tpl.html",
      restrict: "EA",
      link: function(scope, elem, attrs) {

        scope.languageName = attrs.language
        scope.languageHue = hueFromString(attrs.language)
      }
    }


  })
















angular.module("filterService", [])

.factory("FilterService", function($location){

    var filters = {
      only_academic: "true",
      language: "python",
      tag: null,
      type: "pacakges"
    }

    var setFromUrl = function(){
      filters.only_academic = $location.search().only_academic
      filters.tag = $location.search().tag
      filters.language = $location.search().language
      filters.type = $location.search().type
      if (!filters.language){
        set("language", "python")
      }
      if (!filters.type){
        set("type", "people")
      }
      console.log("set filters from url", filters)
    }

    var set = function(k, v){
      filters[k] = v
      $location.search(k, v)
    }
    var toggle = function(k){
      // for booleans
      if (filters[k]) {
        filters[k] = null
      }
      else {
        filters[k] = "true"  // must be string or won't show up in url
      }
      $location.search(k, filters[k])
    }

    var unset = function(k){
      filters[k] = null
    }

    var asQueryStr = function(){
      var ret = []
      _.each(filters, function(v, k){
        if (v){
          ret.push(k + "=" + v)
        }
      })
      return ret.join("&")
    }


  return {
    d: filters,
    set: set,
    toggle: toggle,
    unset: unset,
    setFromUrl: setFromUrl,
    asQueryStr: asQueryStr
  }
});
angular.module("formatterService", [])

.factory("FormatterService", function($location){

  var commas = function(x) { // from stackoverflow
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

  var short = function(num){
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
    short: short,
    commas: commas
  }
});
angular.module('header', [
  ])



  .controller("headerCtrl", function($scope,
                                     $location,
                                     $rootScope,
                                     $http){



    $scope.searchResultSelected = ''

    $rootScope.$on('$routeChangeSuccess', function(next, current){
      $scope.searchResultSelected = ''
      document.getElementById("search-box").blur()
    })
    $rootScope.$on('$routeChangeError', function(event, current, previous, rejection){
      $scope.searchResultSelected = ''
      document.getElementById("search-box").blur()
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







angular.module('packagePage', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/package/:language/:package_name', {
      templateUrl: 'package-page/package-page.tpl.html',
      controller: 'PackagePageCtrl',
      resolve: {
        packageResp: function($http, $route, PackageResource){
          return PackageResource.get({
            namespace: $route.current.params.language,
            name: $route.current.params.package_name
          }).$promise
        }
      }
    })
  })



  .controller("PackagePageCtrl", function($scope,
                                          $routeParams,
                                          ngProgress,
                                          packageResp){
    ngProgress.complete()
    $scope.package = packageResp
    $scope.depNode = packageResp.rev_deps_tree







  })




angular.module('personPage', [
    'ngRoute',
    'profileService',
    "directives.languageIcon"
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/person/:person_id', {
      templateUrl: 'person-page/person-page.tpl.html',
      controller: 'personPageCtrl',
      resolve: {
        personResp: function($http, $route){
          var url = "/api/person/" + $route.current.params.person_id
          return $http.get(url)
        }
      }
    })
  })



  .controller("personPageCtrl", function($scope,
                                          $routeParams,
                                          ngProgress,
                                          FormatterService,
                                          personResp){
    ngProgress.complete()
    $scope.format = FormatterService
    $scope.person = personResp.data
    console.log("retrieved the person", $scope.person)






  })




angular.module('resourcesModule', [])
  .factory('Leaders', function($resource) {
    return $resource('api/leaderboard')
  })


  .factory('PackageResource', function($resource) {
    return $resource('/api/package/:namespace/:name')
  })
angular.module('articleService', [
  ])



  .factory("ArticleService", function($http,
                                      $timeout,
                                      $location){

    var data = {}

    function getArticle(pmid){
      var url = "api/article/" + pmid
      console.log("getting article", pmid)
      return $http.get(url).success(function(resp){
        console.log("got response for api/article/" + pmid, resp)
        data.article = resp
      })
    }

    return {
      data: data,
      getArticle: getArticle
    }


  })
angular.module('currentUserService', [
    'resourcesModule'
  ])



  .factory("CurrentUser", function(UserResource){

    var data = {}

    function overWriteData(newData){
      _.each(newData, function(v, k){
        data[k] = v
      })
    }

    return {
      d: data,
      get: function(){
        return UserResource.get(
          function(newData){
            overWriteData(newData)
            console.log("overwrote the CurrentUser data. now it's this:", data)
          },
          function(resp){
            console.log("error getting current user data", resp)
          }
        )
      }
    }


  })
angular.module('pageService', [
  ])



  .factory("PageService", function(){

    var data = {}
    var defaultData = {}

    function reset(){
      console.log("resetting the page service data")
      _.each(defaultData, function(v, k){
        data[k] = v
      })
    }

    return {
      d: data,
      reset: reset
    }


  })
angular.module('profileService', [
  ])



  .factory("ProfileService", function($http,
                                      $timeout,
                                      $location){

    var data = {
      profile: {
        articles:[]
      }
    }

    function profileStillLoading(){
      console.log("testing if profile still loading", data.profile.articles)
      return _.any(data.profile.articles, function(article){
        return _.isNull(article.percentile)
      })
    }

    function getProfile(slug){
      var url = "/profile/" + slug
      console.log("getting profile for", slug)
      return $http.get(url).success(function(resp){
        data.profile = resp

        if (profileStillLoading()){
          $timeout(function(){
            getProfile(slug)
          }, 1000)
        }

      })
    }

    return {
      data: data,
      foo: function(){
        return "i am in the profile service"
      },

      createProfile: function(name, pmids, coreJournals) {
        console.log("i am making a profile:", name, pmids)
        var postData = {
          name: name,
          pmids: pmids,
          core_journals: coreJournals
        }
        $http.post("/profile",postData)
          .success(function(resp, status, headers){
            console.log("yay got a resp from /profile!", resp)
            $location.path("/u/" + resp.slug)
          })
      },

      getProfile: getProfile
    }


  })
angular.module('snippet', [
  ])



  .controller("packageSnippetCtrl", function($scope){
//    var subscoreNames = [
//      "num_downloads",
//      "pagerank",
//      "num_citations"
//    ]
//    var subscores = _.map(subscoreNames, function(name){
//      return {
//        name: name,
//        percentile: $scope.package[name + "_percentile"],
//        val: $scope.package[name]
//      }
//    })

//    var subScoresSum =  _.reduce(
//      _.map(subScores, function(x){return x[1]}),
//      function(memo, num){ return memo + num; },
//      0
//    )
//    $scope.subScores = subscores
  })


  .controller("personSnippetCtrl", function($scope){

  })


angular.module('staticPages', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/', {
      redirectTo: "/leaderboard"
    })
  })








angular.module('tagPage', [
    'ngRoute',
    'profileService',
    "directives.languageIcon"
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/tag/:tagName', {
      templateUrl: 'tag-page/tag-page.tpl.html',
      controller: 'tagPageCtrl',
      resolve: {
        productsResp: function($http, $route){
          var url = "/api/leaderboard?type=packages&tag=" + $route.current.params.tagName
          return $http.get(url)
        }
      }
    })
  })



  .controller("tagPageCtrl", function($scope,
                                          $routeParams,
                                          ngProgress,
                                          FormatterService,
                                          productsResp){
    ngProgress.complete()
    $scope.format = FormatterService

    $scope.packages = productsResp.data
    console.log("retrieved the tag", productsResp)






  })




angular.module('top', [
    'ngRoute',
    'filterService'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/leaderboard', {
      templateUrl: 'top/top.tpl.html',
      controller: 'TopController',
      resolve: {

      }
    })
  })


  .controller("TopController", function($scope,
                                          $http,
                                          $rootScope,
                                          $routeParams,
                                          Leaders,
                                          ngProgress,
                                          FormatterService,
                                          FilterService){
    FilterService.setFromUrl()
    $scope.filters = FilterService
    $scope.format = FormatterService

    getLeaders()

    var makeUrl = function(){
      return "leaderboard?" + FilterService.asQueryStr()
    }

    function getLeaders(){
      console.log("getLeaders() go", FilterService.d)


      Leaders.get(
        FilterService.d,
        function(resp){
          console.log("got a resp from leaders call", resp.list)
          $scope.leaders = resp
          ngProgress.complete()
        },
        function(resp){
          console.log("got an error :(")
          ngProgress.complete()
        }
      )

    }



















  })

angular.module('templates.app', ['directives/language-icon.tpl.html', 'header/header.tpl.html', 'header/search-result.tpl.html', 'package-page/dep-node.tpl.html', 'package-page/package-page.tpl.html', 'person-page/person-page.tpl.html', 'snippet/impact-popover.tpl.html', 'snippet/package-snippet.tpl.html', 'snippet/person-mini.tpl.html', 'snippet/person-snippet.tpl.html', 'snippet/tag-snippet.tpl.html', 'static-pages/landing.tpl.html', 'tag-page/tag-page.tpl.html', 'top/top.tpl.html']);

angular.module("directives/language-icon.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("directives/language-icon.tpl.html",
    "<span class=\"language\"\n" +
    "      ng-class=\"{badge: languageName}\"\n" +
    "      style=\"background-color: hsl({{ languageHue }}, 80%, 30%)\">\n" +
    "   {{ languageName }}\n" +
    "</span>");
}]);

angular.module("header/header.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("header/header.tpl.html",
    "<div class=\"ti-header\" ng-controller=\"headerCtrl\">\n" +
    "   <h1>\n" +
    "      <a href=\"/\">\n" +
    "         <img src=\"static/img/logo-circle.png\" alt=\"\"/>\n" +
    "      </a>\n" +
    "   </h1>\n" +
    "\n" +
    "   <div class=\"ti-menu\">\n" +
    "      <a href=\"leaderboard?type=people\"\n" +
    "         popover=\"Top coders\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-placement=\"bottom\"\n" +
    "         class=\"menu-link\" id=\"leaders-menu-link\">\n" +
    "         <i class=\"fa fa-user\"></i>\n" +
    "      </a>\n" +
    "      <a href=\"leaderboard?type=packages\"\n" +
    "         popover=\"Top packages\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-placement=\"bottom\"\n" +
    "         class=\"menu-link\" id=\"leaders-menu-link\">\n" +
    "         <i class=\"fa fa-archive\"></i>\n" +
    "      </a>\n" +
    "      <a href=\"leaderboard?type=tags\"\n" +
    "         popover=\"Top tags\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-placement=\"bottom\"\n" +
    "         class=\"menu-link\" id=\"leaders-menu-link\">\n" +
    "         <i class=\"fa fa-tag\"></i>\n" +
    "      </a>\n" +
    "\n" +
    "      <!-- needs weird style hacks -->\n" +
    "      <a href=\"about\"\n" +
    "         class=\"menu-link about\" id=\"leaders-menu-link\">\n" +
    "         <i\n" +
    "         popover=\"Learn more about Depsy\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-placement=\"bottom\" class=\"fa fa-question-circle\"></i>\n" +
    "      </a>\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "   <div class=\"search-box\">\n" +
    "    <input type=\"text\"\n" +
    "           id=\"search-box\"\n" +
    "           ng-model=\"searchResultSelected\"\n" +
    "           placeholder=\"Search packages, authors, and topics\"\n" +
    "           typeahead=\"result as result.name for result in doSearch($viewValue)\"\n" +
    "           typeahead-loading=\"loadingLocations\"\n" +
    "           typeahead-no-results=\"noResults\"\n" +
    "           typeahead-template-url=\"header/search-result.tpl.html\"\n" +
    "           typeahead-focus-first=\"false\"\n" +
    "           typeahead-on-select=\"onSelect($item)\"\n" +
    "           class=\"form-control input-lg\">\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "</div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("header/search-result.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("header/search-result.tpl.html",
    "<div class=\"typeahead-group-header\" ng-if=\"match.model.is_first\">\n" +
    "   <span class=\"group-header-type pypy-package\" ng-if=\"match.model.type=='pypi_project'\">\n" +
    "      <img src=\"static/img/python.png\" alt=\"\"/>\n" +
    "      Python packages\n" +
    "   </span>\n" +
    "   <span class=\"group-header-type cran-package\" ng-if=\"match.model.type=='cran_project'\">\n" +
    "      <img src=\"static/img/r-logo.png\" alt=\"\"/>\n" +
    "      R packages\n" +
    "   </span>\n" +
    "   <span class=\"group-header-type people\" ng-if=\"match.model.type=='person'\">\n" +
    "      <i class=\"fa fa-user\"></i>\n" +
    "      People\n" +
    "   </span>\n" +
    "   <span class=\"group-header-type tags\" ng-if=\"match.model.type=='tag'\">\n" +
    "      <i class=\"fa fa-tag\"></i>\n" +
    "      Tags\n" +
    "   </span>\n" +
    "\n" +
    "</div>\n" +
    "<a ng-href=\"package/python/{{ match.model.name }}\" ng-if=\"match.model.type=='pypi_project'\">\n" +
    "   <span class=\"name\">\n" +
    "      {{ match.model.name }}\n" +
    "   </span>\n" +
    "   <span  class=\"summary\">\n" +
    "      {{ match.model.summary }}\n" +
    "   </span>\n" +
    "</a>\n" +
    "<a ng-href=\"package/r/{{ match.model.name }}\" ng-if=\"match.model.type=='cran_project'\">\n" +
    "   <span class=\"name\">\n" +
    "      {{ match.model.name }}\n" +
    "   </span>\n" +
    "   <span  class=\"summary\">\n" +
    "      {{ match.model.summary }}\n" +
    "   </span>\n" +
    "</a>\n" +
    "<a ng-href=\"person/{{ match.model.id }}\" ng-if=\"match.model.type=='person'\">\n" +
    "   <span class=\"name\">\n" +
    "      {{ match.model.name }}\n" +
    "   </span>\n" +
    "</a>\n" +
    "<a ng-href=\"tag/{{ match.model.name }}\" ng-if=\"match.model.type=='tag'\">\n" +
    "   <span class=\"name\">\n" +
    "      {{ match.model.name }}\n" +
    "   </span>\n" +
    "   <span class=\"tag summary\">\n" +
    "      {{ match.model.impact }} packages\n" +
    "   </span>\n" +
    "</a>\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("package-page/dep-node.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("package-page/dep-node.tpl.html",
    "<div class=\"dep-node is-rollup-{{ depNode.is_rollup }} is-root-{{ depNode.is_root }} is-package-{{ depNode.is_package }}\">\n" +
    "   <div class=\"about\">\n" +
    "      <a class=\"name\"\n" +
    "         ng-if=\"!depNode.is_rollup && depNode.is_package\"\n" +
    "         style=\"font-size: {{ 100 }}%;\"\n" +
    "         href=\"package/r/{{ depNode.name }}\">\n" +
    "         {{ depNode.name }}\n" +
    "      </a>\n" +
    "      <span ng-if=\"depNode.is_rollup || !depNode.is_package\"\n" +
    "            style=\"font-size: {{ 100 }}%;\"\n" +
    "            class=\"name\">\n" +
    "         {{ depNode.name }}\n" +
    "      </span>\n" +
    "      <span class=\"metrics\">\n" +
    "         <!--<span class=\"percent-root-goodness\">{{ nFormatter(depNode.percent_root_goodness * 100) }}%</span>-->\n" +
    "         <span class=\"pagerank\">{{ depNode.display_pagerank }}</span>\n" +
    "         <span class=\"stars\">({{ depNode.stars }})</span>\n" +
    "      </span>\n" +
    "   </div>\n" +
    "   <div class=\"children\">\n" +
    "      <div class=\"dep-node-container\"\n" +
    "           ng-repeat=\"depNode in depNode.children | orderBy: '-sort_score'\"\n" +
    "           ng-include=\"'package-page/dep-node.tpl.html'\"></div>\n" +
    "   </div>\n" +
    "</div>");
}]);

angular.module("package-page/package-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("package-page/package-page.tpl.html",
    "<div class=\"package-page sidebar-page\">\n" +
    "\n" +
    "\n" +
    "   <!--\n" +
    "   <div class=\"coming-soon\">\n" +
    "      <h1>Coming soon :)</h1>\n" +
    "      <h2>Check back here soon for summary, authors, impact details (downloads, dependency pagerank, citations) and dependency tree.</h2>\n" +
    "\n" +
    "   </div>\n" +
    "   -->\n" +
    "\n" +
    "   <!--\n" +
    "   <div class=\"ti-page-sidebar\">\n" +
    "      <div class=\"sidebar-header\">\n" +
    "\n" +
    "         <div class=\"person-about\">\n" +
    "            <img ng-src=\"{{ person.icon }}\" alt=\"\"/>\n" +
    "            <div class=\"score\">\n" +
    "               <span class=\"impact\">\n" +
    "                  {{ format.short(person.impact) }}\n" +
    "               </span>\n" +
    "               <span class=\"rank\">\n" +
    "                  #{{ person.impact_rank }}\n" +
    "               </span>\n" +
    "            </div>\n" +
    "\n" +
    "            <span class=\"name\">\n" +
    "               {{ person.name }}\n" +
    "            </span>\n" +
    "            <span class=\"accounts\">\n" +
    "               <i popover-title=\"Academic\"\n" +
    "                  popover-trigger=\"mouseenter\"\n" +
    "                  popover=\"We infer academic status based on factors like email address, tags, and institution.\"\n" +
    "                  ng-show=\"person.is_academic\"\n" +
    "                  class=\"is-academic account fa fa-graduation-cap\"></i>\n" +
    "\n" +
    "               <img class=\"orcid account\"\n" +
    "                  popover-title=\"ORCiD coming soon\"\n" +
    "                  popover-trigger=\"mouseenter\"\n" +
    "                  popover=\"ORCiD is a unique identifier for researchers. We'll be rolling out support soon.\"\n" +
    "                  ng-show=\"person.is_academic\"\n" +
    "                  src=\"static/img/orcid.gif\" alt=\"\"/>\n" +
    "\n" +
    "               <a ng-if=\"person.github_login\" class=\"account\" href=\"http://github/{{ person.github_login }}\">\n" +
    "                  <i class=\"fa fa-github\"></i>\n" +
    "                  <span class=\"github-url-part\" ng-if=\"!person.is_academic\">\n" +
    "                     github/{{ person.github_login }}\n" +
    "                  </span>\n" +
    "               </a>\n" +
    "            </span>\n" +
    "\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"top-tags\">\n" +
    "         <h3>Top tags</h3>\n" +
    "         <div class=\"tags\">\n" +
    "            <a class=\"tag\" ng-repeat=\"tag in person.top_person_tags | orderBy: '-count'\">\n" +
    "               {{ tag.name }}\n" +
    "            </a>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"top-collabs\">\n" +
    "         <h3>Top collaborators</h3>\n" +
    "         <div class=\"tags\">\n" +
    "            <a class=\"collab\"\n" +
    "               popover=\"We collaborated\"\n" +
    "               popover-trigger=\"mouseenter\"\n" +
    "               popover-title=\"Top collaborator\"\n" +
    "               href=\"person/{{ collab.id }}\"\n" +
    "               ng-repeat=\"collab in person.top_collabs | orderBy: '-collab_score'\">\n" +
    "               <img src=\"{{ collab.icon_small }}\" alt=\"\"/>\n" +
    "               <span class=\"impact\">{{ format.short(collab.impact) }}</span>\n" +
    "               <span class=\"name\">{{ collab.name }}</span>\n" +
    "               <span class=\"is-academic\" ng-show=\"collab.is_academic\"><i class=\"fa fa-graduation-cap\"></i></span>\n" +
    "\n" +
    "            </a>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "   <div class=\"ti-page-body\">\n" +
    "\n" +
    "      <div class=\"packages\">\n" +
    "         <div class=\"person-package\" ng-repeat=\"package in person.person_packages | orderBy:'-person_package_impact'\">\n" +
    "            <div class=\"person-package-stats\">\n" +
    "               <span class=\"roles\">\n" +
    "                  <span class=\"role role-{{ role }}\" ng-repeat=\"role in package.roles | orderBy: '-toLowerCase()'\">\n" +
    "                     <i class=\"fa fa-user\" ng-if=\"role=='author'\"></i>\n" +
    "                     <i class=\"fa fa-save\"  ng-if=\"role=='github_contributor'\"></i>\n" +
    "                     <i class=\"fa fa-github\" ng-if=\"role=='github_owner'\"></i>\n" +
    "                  </span>\n" +
    "               </span>\n" +
    "               <div class=\"bar-outside\">\n" +
    "                  <span class=\"bar-inside\" style=\"width: {{ package.person_package_credit * 100 }}%\"></span>\n" +
    "               </div>\n" +
    "            </div>\n" +
    "            <span class=\"package-snippet-wrapper\" ng-include=\"'snippet/package-snippet.tpl.html'\"></span>\n" +
    "         </div>\n" +
    "\n" +
    "\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "   -->\n" +
    "\n" +
    "</div>\n" +
    "");
}]);

angular.module("person-page/person-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("person-page/person-page.tpl.html",
    "<div class=\"person-page sidebar-page\">\n" +
    "   <div class=\"ti-page-sidebar\">\n" +
    "      <div class=\"sidebar-header\">\n" +
    "\n" +
    "         <div class=\"person-about\">\n" +
    "            <img ng-src=\"{{ person.icon }}\" alt=\"\"/>\n" +
    "            <div class=\"score\">\n" +
    "               <span class=\"impact\">\n" +
    "                  {{ format.short(person.impact) }}\n" +
    "               </span>\n" +
    "               <span class=\"rank\">\n" +
    "                  #{{ format.commas(person.impact_rank) }}\n" +
    "               </span>\n" +
    "            </div>\n" +
    "\n" +
    "            <span class=\"name\">\n" +
    "               {{ person.name }}\n" +
    "            </span>\n" +
    "            <span class=\"accounts\">\n" +
    "               <i popover-title=\"Academic\"\n" +
    "                  popover-trigger=\"mouseenter\"\n" +
    "                  popover=\"We infer academic status based on factors like email address, tags, and institution.\"\n" +
    "                  ng-show=\"person.is_academic\"\n" +
    "                  class=\"is-academic account fa fa-graduation-cap\"></i>\n" +
    "\n" +
    "               <img class=\"orcid account\"\n" +
    "                  popover-title=\"ORCiD coming soon\"\n" +
    "                  popover-trigger=\"mouseenter\"\n" +
    "                  popover=\"ORCiD is a unique identifier for researchers. We'll be rolling out support soon.\"\n" +
    "                  ng-show=\"person.is_academic\"\n" +
    "                  src=\"static/img/orcid.gif\" alt=\"\"/>\n" +
    "\n" +
    "               <a ng-if=\"person.github_login\" class=\"account\" href=\"http://github/{{ person.github_login }}\">\n" +
    "                  <i class=\"fa fa-github\"></i>\n" +
    "                  <span class=\"github-url-part\" ng-if=\"!person.is_academic\">\n" +
    "                     github/{{ person.github_login }}\n" +
    "                  </span>\n" +
    "               </a>\n" +
    "            </span>\n" +
    "\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"impact-descr\" ng-if=\"!person.is_organization\">\n" +
    "         <h3>Impact</h3>\n" +
    "         <div class=\"impact-copy\" ng-show=\"person.main_language=='python'\">\n" +
    "            Ranked #{{ format.commas(person.impact_rank) }} in impact out of {{ format.commas(person.impact_rank_max) }} Pythonistas on PyPi. That's based on summed package impacts, adjusted by percent contributions.\n" +
    "         </div>\n" +
    "         <div class=\"impact-copy\" ng-show=\"person.main_language=='r'\">\n" +
    "            Ranked #{{ person.impact_rank }} in impact out of {{ person.impact_rank_max }} R coders on CRAN. That's based on summed package impacts, adjusted by percent contributions.\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"top-tags\">\n" +
    "         <h3>Top tags</h3>\n" +
    "         <div class=\"tags\">\n" +
    "            <a class=\"tag\"\n" +
    "               href=\"tag/{{ tag.name }}\"\n" +
    "               ng-repeat=\"tag in person.top_person_tags | orderBy: '-count'\">\n" +
    "               {{ tag.name }}\n" +
    "            </a>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"top-collabs\">\n" +
    "         <h3>Top collaborators</h3>\n" +
    "         <div class=\"top-collabs-list\">\n" +
    "            <a class=\"collab person-mini\"\n" +
    "               href=\"person/{{ collab.id }}\"\n" +
    "               ng-repeat=\"collab in person.top_collabs | orderBy: '-collab_score'\">\n" +
    "               <img src=\"{{ collab.icon_small }}\" alt=\"\"/>\n" +
    "               <span class=\"impact\">{{ format.short(collab.impact) }}</span>\n" +
    "               <span class=\"name\">{{ collab.name }}</span>\n" +
    "               <span class=\"is-academic\" ng-show=\"collab.is_academic\"><i class=\"fa fa-graduation-cap\"></i></span>\n" +
    "\n" +
    "            </a>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <a class=\"json-link btn btn-default\"\n" +
    "         popover-title=\"View this page as JSON\"\n" +
    "         popover-placement=\"right\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         target=\"_self\"\n" +
    "         popover=\"Everything here is open data, free to use for your own projects. You can also check out our API for more systematic access.\"\n" +
    "         href=\"api/person/{{ person.id }}\">\n" +
    "         <i class=\"fa fa-download\"></i>\n" +
    "         JSON\n" +
    "      </a>\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "   <div class=\"ti-page-body\">\n" +
    "\n" +
    "      <div class=\"packages\">\n" +
    "         <div class=\"person-package\" ng-repeat=\"package in person.person_packages | orderBy:'-person_package_impact'\">\n" +
    "            <div class=\"person-package-stats\">\n" +
    "               <span class=\"roles\">\n" +
    "                  <span class=\"role role-{{ role }}\" ng-repeat=\"role in package.roles | orderBy: '-toLowerCase()'\">\n" +
    "                     <i class=\"fa fa-user\" ng-if=\"role=='author'\"></i>\n" +
    "                     <i class=\"fa fa-save\"  ng-if=\"role=='github_contributor'\"></i>\n" +
    "                     <i class=\"fa fa-github\" ng-if=\"role=='github_owner'\"></i>\n" +
    "                  </span>\n" +
    "               </span>\n" +
    "               <div class=\"bar-outside\">\n" +
    "                  <span class=\"bar-inside\" style=\"width: {{ package.person_package_credit * 100 }}%\"></span>\n" +
    "               </div>\n" +
    "            </div>\n" +
    "            <span class=\"package-snippet-wrapper\" ng-include=\"'snippet/package-snippet.tpl.html'\"></span>\n" +
    "         </div>\n" +
    "\n" +
    "\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "</div>\n" +
    "");
}]);

angular.module("snippet/impact-popover.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("snippet/impact-popover.tpl.html",
    "<div id=\"impact-popover\">\n" +
    "   <div class=\"impact\">\n" +
    "\n" +
    "      <div class=\"sub-score citations metric\" ng-show=\"package.num_citations\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-file-text-o\"></i>\n" +
    "            Citations\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ package.num_citations }}</span>\n" +
    "         </span>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"sub-score pagerank metric\" ng-show=\"package.pagerank\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-exchange\"></i>\n" +
    "            Dependency PageRank\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ format.short(package.pagerank_score) }} </span>\n" +
    "         </span>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"sub-score downloads metric\" ng-show=\"package.num_downloads\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-download\"></i>\n" +
    "            Downloads\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ format.short(package.num_downloads)}}</span>\n" +
    "         </span>\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "</div>");
}]);

angular.module("snippet/package-snippet.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("snippet/package-snippet.tpl.html",
    "<span class=\"snippet package-snippet\"\n" +
    "     ng-controller=\"packageSnippetCtrl\">\n" +
    "   <span class=\"left-metrics\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-title=\"Impact\"\n" +
    "         popover-template=\"'snippet/impact-popover.tpl.html'\">\n" +
    "\n" +
    "      <div class=\"one-metric metric\">\n" +
    "         {{ format.short(package.impact) }}\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "      <div class=\"vis\">\n" +
    "         <div class=\"subscore {{ subscore.name }}\"\n" +
    "              ng-repeat=\"subscore in package.subscores\">\n" +
    "            <div class=\"val {{ subscore.name }}\" ng-if=\"subscore.val > 0\">{{ format.short(subscore.val) }}</div>\n" +
    "            <div class=\"bar-outer\">\n" +
    "               <div class=\"bar-inner {{ subscore.name }}\" style=\"width: {{ subscore.score / 10 }}%;\"></div>\n" +
    "            </div>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"rank\">\n" +
    "         #{{ format.commas(package.impact_rank) }}\n" +
    "      </div>\n" +
    "\n" +
    "   </span>\n" +
    "\n" +
    "   <span class=\"metadata\">\n" +
    "      <span class=\"name-container\">\n" +
    "\n" +
    "         <span class=\"icon\">\n" +
    "            <span class=\"language-icon r\"\n" +
    "                  ng-if=\"package.language=='r'\">\n" +
    "               R\n" +
    "            </span>\n" +
    "            <span class=\"language-icon python\"\n" +
    "                  ng-if=\"package.language=='python'\">\n" +
    "               py\n" +
    "            </span>\n" +
    "         </span>\n" +
    "\n" +
    "\n" +
    "         <a class=\"name\" href=\"package/{{ package.language }}/{{ package.name }}\">\n" +
    "            {{ package.name }}\n" +
    "         </a>\n" +
    "         <i popover-title=\"Academic\"\n" +
    "            popover-trigger=\"mouseenter\"\n" +
    "            popover=\"We infer academic status based on factors like email address, tags, and institution.\"\n" +
    "            ng-show=\"package.is_academic\"\n" +
    "            class=\"is-academic fa fa-graduation-cap\"></i>\n" +
    "\n" +
    "         <span class=\"contribs\">\n" +
    "            <span class=\"by\">by</span>\n" +
    "            <a href=\"person/{{ contrib.id }}\"\n" +
    "               popover=\"name: {{ contrib.name }}\"\n" +
    "               popover-trigger=\"mouseenter\"\n" +
    "               class=\"contrib\"\n" +
    "               ng-repeat=\"contrib in package.contribs | orderBy: '-credit' | limitTo: 3\">{{ contrib.single_name }}<span\n" +
    "                       ng-hide=\"{{ $last }}\"\n" +
    "                       class=\"comma\">, </span></a><a class=\"contrib plus-more\"\n" +
    "               href=\"package/{{ package.language }}/{{ package.name }}\"\n" +
    "                  popover=\"click to see all {{ package.num_contributors }} contributors\"\n" +
    "                  popover-trigger=\"mouseenter\" ng-show=\"package.num_contributors > 3\">,\n" +
    "               and {{ package.num_contributors - 3 }} others\n" +
    "            </a>\n" +
    "         </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "      </span>\n" +
    "      <span class=\"summary\">{{ package.summary }}</span>\n" +
    "   </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "</span>\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("snippet/person-mini.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("snippet/person-mini.tpl.html",
    "<span class=\"person-mini-insides\"\n" +
    "   <img src=\"{{ contrib.icon_small }}\" alt=\"\"/>\n" +
    "   <span class=\"impact\">{{ format.short(contrib.impact) }}</span>\n" +
    "   <span class=\"name\">{{ contrib.name }}</span>\n" +
    "   <span class=\"is-academic\" ng-show=\"contrib.is_academic\"><i class=\"fa fa-graduation-cap\"></i></span>\n" +
    "</span>");
}]);

angular.module("snippet/person-snippet.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("snippet/person-snippet.tpl.html",
    "<span class=\"snippet person-snippet\"\n" +
    "     ng-controller=\"personSnippetCtrl\">\n" +
    "   <span class=\"left-metrics\"\n" +
    "         popover-placement=\"top\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-template=\"'snippet/impact-popover.tpl.html'\">\n" +
    "\n" +
    "      <span class=\"one-metric metric\">\n" +
    "         {{ format.short(person.impact) }}\n" +
    "      </span>\n" +
    "\n" +
    "\n" +
    "      <span class=\"rank\">\n" +
    "         #{{ format.commas(person.impact_rank) }}\n" +
    "      </span>\n" +
    "\n" +
    "   </span>\n" +
    "\n" +
    "\n" +
    "   <span class=\"metadata\">\n" +
    "      <span class=\"name-container\">\n" +
    "\n" +
    "\n" +
    "         <span class=\"icon\">\n" +
    "            <img class=\"person-icon\" src=\"{{ person.icon_small }}\" alt=\"\"/>\n" +
    "         </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "         <a class=\"name\" tooltip=\"click for more info\" href=\"person/{{ person.id }}\">\n" +
    "            {{ person.name }}\n" +
    "         </a>\n" +
    "\n" +
    "\n" +
    "         <i popover-title=\"Academic\"\n" +
    "            popover-trigger=\"mouseenter\"\n" +
    "            popover=\"We infer academic status based on factors like email address, tags, and institution.\"\n" +
    "            ng-show=\"person.is_academic\"\n" +
    "            class=\"is-academic fa fa-graduation-cap\"></i>\n" +
    "\n" +
    "\n" +
    "         <span class=\"person-packages\">\n" +
    "            <span class=\"works-on\">{{ person.num_packages }} packages including: </span>\n" +
    "            <span class=\"package\" ng-repeat=\"package in person.person_packages | orderBy: '-person_package_impact'\">\n" +
    "               <a href=\"package/{{ package.language }}/{{ package.name }}\">\n" +
    "                  {{ package.name }}</a><span class=\"sep\" ng-show=\"!$last\">,</span>\n" +
    "            </span>\n" +
    "         </span>\n" +
    "      </span>\n" +
    "\n" +
    "      <span class=\"summary tags\">\n" +
    "         <span class=\"tags\">\n" +
    "            <a href=\"tag/{{ tag.name }}\"\n" +
    "               class=\"tag\"\n" +
    "               ng-repeat=\"tag in person.top_person_tags | orderBy: '-count'\">\n" +
    "               {{ tag.name }}\n" +
    "            </a>\n" +
    "         </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "      </span>\n" +
    "   </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "</span>\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("snippet/tag-snippet.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("snippet/tag-snippet.tpl.html",
    "<span class=\"snippet tag-snippet\"\n" +
    "     ng-controller=\"personSnippetCtrl\">\n" +
    "<span class=\"left-metrics\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover=\"{{ tag.count }} packages are tagged with '{{ tag.name }}'\">\n" +
    "\n" +
    "      <span class=\"one-metric metric\">\n" +
    "         {{ format.short(tag.count) }}\n" +
    "      </span>\n" +
    "\n" +
    "   </span>\n" +
    "\n" +
    "   <span class=\"metadata\">\n" +
    "      <span class=\"name-container\">\n" +
    "\n" +
    "         <span class=\"icon tag-icon\">\n" +
    "            <i class=\"fa fa-tag\"></i>\n" +
    "         </span>\n" +
    "\n" +
    "         <a class=\"name\"\n" +
    "            href=\"tag/{{ tag.name }}\">\n" +
    "            {{ tag.name }}\n" +
    "         </a>\n" +
    "\n" +
    "\n" +
    "         <i popover-title=\"Academic\"\n" +
    "            popover-trigger=\"mouseenter\"\n" +
    "            popover=\"This tag is often applied to academic projects.\"\n" +
    "            ng-show=\"tag.is_academic\"\n" +
    "            class=\"is-academic fa fa-graduation-cap\"></i>\n" +
    "\n" +
    "      </span>\n" +
    "\n" +
    "      <span class=\"summary tags\">\n" +
    "         <span class=\"tags\">\n" +
    "            related tags:\n" +
    "            <a href=\"tag/{{ relatedTag.name }}\"\n" +
    "               class=\"tag\"\n" +
    "               ng-repeat=\"relatedTag in tag.related_tags | orderBy: '-count'\">\n" +
    "               {{ relatedTag.name }}\n" +
    "            </a>\n" +
    "         </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "      </span>\n" +
    "   </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "</span>\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("static-pages/landing.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("static-pages/landing.tpl.html",
    "<div class=\"landing\">\n" +
    "   <div class=\"tagline\">\n" +
    "      Find the impact of software packages for Python and R.\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "</div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("tag-page/tag-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("tag-page/tag-page.tpl.html",
    "<div class=\"tag-page sidebar-page\">\n" +
    "   <div class=\"ti-page-sidebar\">\n" +
    "      <div class=\"sidebar-header\">\n" +
    "\n" +
    "         <div class=\"tag-about\">\n" +
    "            <span class=\"name\">\n" +
    "               <i class=\"fa fa-tag\"></i>\n" +
    "               {{ packages.filters.tag }}\n" +
    "            </span>\n" +
    "            <span class=\"num-tags\">\n" +
    "               Showing {{ packages.num_returned }} of {{ packages.num_total }} uses\n" +
    "            </span>\n" +
    "         </div>\n" +
    "\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"top-tags\">\n" +
    "         <h3>Related tags</h3>\n" +
    "         <div class=\"tags\">\n" +
    "            <a class=\"tag\" ng-repeat=\"tag in tag.related_tags | orderBy: '-count'\">\n" +
    "               {{ packages.filters.tag }}\n" +
    "            </a>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "      <a class=\"json-link btn btn-default\"\n" +
    "         popover-title=\"View this page as JSON\"\n" +
    "         popover-placement=\"right\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         target=\"_self\"\n" +
    "         popover=\"Everything here is open data, free to use for your own projects. You can also check out our API for more systematic access.\"\n" +
    "         href=\"http://localhost:5008/api/leaderboard?type=packages&tag={{ packages.filters.tag }}\">\n" +
    "         <i class=\"fa fa-download\"></i>\n" +
    "         JSON\n" +
    "      </a>\n" +
    "\n" +
    "      <!-- we can use this from the people page to print out tag users...\n" +
    "      <div class=\"top-collabs\">\n" +
    "         <h3>Top collaborators</h3>\n" +
    "         <div class=\"tags\">\n" +
    "            <a class=\"collab\"\n" +
    "               popover=\"We collaborated\"\n" +
    "               popover-trigger=\"mouseenter\"\n" +
    "               popover-title=\"Top collaborator\"\n" +
    "               href=\"person/{{ collab.id }}\"\n" +
    "               ng-repeat=\"collab in person.top_collabs | orderBy: '-collab_score'\">\n" +
    "               <img src=\"{{ collab.icon_small }}\" alt=\"\"/>\n" +
    "               <span class=\"impact\">{{ format.short(collab.impact) }}</span>\n" +
    "               <span class=\"name\">{{ collab.name }}</span>\n" +
    "               <span class=\"is-academic\" ng-show=\"collab.is_academic\"><i class=\"fa fa-graduation-cap\"></i></span>\n" +
    "\n" +
    "            </a>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "      -->\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "   <div class=\"ti-page-body\">\n" +
    "      <div class=\"packages\">\n" +
    "         <div class=\"person-package\" ng-repeat=\"package in packages.list | orderBy:'-impact'\">\n" +
    "            <span class=\"package-snippet-wrapper\" ng-include=\"'snippet/package-snippet.tpl.html'\"></span>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "</div>\n" +
    "");
}]);

angular.module("top/top.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("top/top.tpl.html",
    "<div class=\"top-packages top-page page sidebar-page\">\n" +
    "\n" +
    "\n" +
    "\n" +
    "   <div class=\"sidebar\">\n" +
    "\n" +
    "      <div class=\"leader-type-select facet\">\n" +
    "         <h3>Show me</h3>\n" +
    "         <ul>\n" +
    "            <li class=\"filter-option\" ng-click=\"filters.set('type', 'people')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type == 'people'\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type != 'people'\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "\n" +
    "               <span class=\"text\">coders</span>\n" +
    "            </li>\n" +
    "\n" +
    "            <li class=\"filter-option\" ng-click=\"filters.set('type', 'packages')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type == 'packages'\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type != 'packages'\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "\n" +
    "               <span class=\"text\">packages</span>\n" +
    "            </li>\n" +
    "\n" +
    "            <li class=\"filter-option\" ng-click=\"filters.set('type', 'tags')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type == 'tags'\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type != 'tags'\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "\n" +
    "               <span class=\"text\">tags</span>\n" +
    "            </li>\n" +
    "         </ul>\n" +
    "\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"language-type-select facet\">\n" +
    "         <h3 ng-show=\"filters.d.type=='packages'\">written in</h3>\n" +
    "         <h3 ng-show=\"filters.d.type=='people'\">who work in</h3>\n" +
    "         <h3 ng-show=\"filters.d.type=='tags'\">applied to</h3>\n" +
    "         <ul>\n" +
    "            <li class=\"filter-option\" ng-click=\"filters.set('language', 'python')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.language == 'python'\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"filters.d.language != 'python'\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "\n" +
    "               <span class=\"text\">Python</span>\n" +
    "            </li>\n" +
    "\n" +
    "            <li class=\"filter-option\" ng-click=\"filters.set('language', 'r')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.language == 'r'\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"filters.d.language != 'r'\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "\n" +
    "               <span class=\"text\">R</span>\n" +
    "            </li>\n" +
    "         </ul>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"language-type-select facet\">\n" +
    "         <h3 ng-show=\"filters.d.type=='packages'\">that are</h3>\n" +
    "         <h3 ng-show=\"filters.d.type=='people'\">and who are</h3>\n" +
    "         <h3 ng-show=\"filters.d.type=='tags'\">that are</h3>\n" +
    "         <ul>\n" +
    "            <li class=\"filter-option\" ng-click=\"filters.toggle('only_academic')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.only_academic\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"!filters.d.only_academic\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "               <!--\n" +
    "               <i class=\"fa fa-graduation-cap\"></i>\n" +
    "               -->\n" +
    "\n" +
    "               <span class=\"text\" ng-show=\"filters.d.type=='packages'\">academic projects</span>\n" +
    "               <span class=\"text\" ng-show=\"filters.d.type=='people'\">academics</span>\n" +
    "               <span class=\"text\" ng-show=\"filters.d.type=='tags'\">academic</span>\n" +
    "            </li>\n" +
    "         </ul>\n" +
    "      </div>\n" +
    "\n" +
    "      <a class=\"json-link btn btn-default\"\n" +
    "         popover-title=\"View this page as JSON\"\n" +
    "         popover-placement=\"right\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         target=\"_self\"\n" +
    "         popover=\"Everything here is open data, free to use for your own projects. You can also check out our API for more systematic access.\"\n" +
    "         href=\"api/leaderboard?{{ filters.asQueryStr() }}\">\n" +
    "         <i class=\"fa fa-download\"></i>\n" +
    "         JSON\n" +
    "      </a>\n" +
    "\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "   <div class=\"main\">\n" +
    "\n" +
    "      <div class=\"ti-page-header leaderboard-header\">\n" +
    "         <h2>\n" +
    "            <span class=\"icons\">\n" +
    "               <!-- put icons here based on filters -->\n" +
    "            </span>\n" +
    "            <span class=\"text\">\n" +
    "               Highest-impact\n" +
    "               <span class=\"is-academic\" ng-if=\"filters.d.is_academic\">academic</span>\n" +
    "               <span class=\"language\">{{ filters.d.language }}</span>\n" +
    "               <span class=\"leaders-type\">{{ filters.d.type }}</span>\n" +
    "            </span>\n" +
    "         </h2>\n" +
    "         <div class=\"descr\">\n" +
    "            <span class=\"people\" ng-show=\"filters.d.type=='people'\">\n" +
    "               Based on the impact of packages they've worked on.\n" +
    "            </span>\n" +
    "            <span class=\"tags\" ng-show=\"filters.d.type=='tags'\">\n" +
    "               Based on the number of packages associated with the tag.\n" +
    "            </span>\n" +
    "            <span class=\"impact-criteria\" ng-show=\"filters.d.type=='packages' || filters.d.type=='people'\">\n" +
    "               That's from how often (and by whom) packages are\n" +
    "                  <a class=\"impact-dimension downloads\" popover=\"More about downloads coming soon\" popover-trigger=\"mouseenter\">\n" +
    "                     downloaded,\n" +
    "                     <i class=\"fa fa-question-circle\"></i>\n" +
    "                  </a>\n" +
    "                  <a class=\"impact-dimension pagerank\" popover=\"More about reverse dependencies coming soon\" popover-trigger=\"mouseenter\">\n" +
    "                     used in other software,\n" +
    "                     <i class=\"fa fa-question-circle\"></i>\n" +
    "                  </a>\n" +
    "                     and\n" +
    "                  <a class=\"impact-dimension downloads\" popover=\"More about citations coming soon\" popover-trigger=\"mouseenter\">\n" +
    "                     cited in the scholarly literature.\n" +
    "                     <i class=\"fa fa-question-circle\"></i>\n" +
    "                  </a>\n" +
    "            </span>\n" +
    "\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "      <div class=\"content\">\n" +
    "         <div class=\"list-items\">\n" +
    "            <!-- packages loop -->\n" +
    "            <div ng-if=\"filters.d.type=='packages'\" class=\"leader\" ng-repeat=\"package in leaders.list\">\n" +
    "               <div class=\"package-snippet-wrapper\"  ng-include=\"'snippet/package-snippet.tpl.html'\"></div>\n" +
    "            </div>\n" +
    "\n" +
    "            <!-- people loop -->\n" +
    "            <div ng-if=\"filters.d.type=='people'\" class=\"leader\" ng-repeat=\"person in leaders.list\">\n" +
    "               <div class=\"package-snippet-wrapper\"  ng-include=\"'snippet/person-snippet.tpl.html'\"></div>\n" +
    "            </div>\n" +
    "\n" +
    "            <!-- tag loop -->\n" +
    "            <div ng-if=\"filters.d.type=='tags'\" class=\"leader\" ng-repeat=\"tag in leaders.list\">\n" +
    "               <div class=\"package-snippet-wrapper\"  ng-include=\"'snippet/tag-snippet.tpl.html'\"></div>\n" +
    "            </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "</div>");
}]);
