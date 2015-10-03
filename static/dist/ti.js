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
//    ngProgress.complete()
  })
  $rootScope.$on('$routeChangeError', function(event, current, previous, rejection){
    console.log("$routeChangeError")
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
        set("type", "packages")
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


  return {
    d: filters,
    set: set,
    toggle: toggle,
    unset: unset,
    setFromUrl: setFromUrl
  }
});
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
                                          packageResp){
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
                                          personResp){
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

    var packagePairs = _.pairs($scope.package)
    var subScores = _.filter(packagePairs, function(packagePair){
      return packagePair[0].indexOf("_percentile") > 0
    })

    var subScoresSum =  _.reduce(
      _.map(subScores, function(x){return x[1]}),
      function(memo, num){ return memo + num; },
      0
    )

    var subScoreRatios = _.map(subScores, function(subScore){

      var rawVal = subScore[1]
      var val
      if (!rawVal){
        val = 0
      }
      else {
        val = rawVal / subScoresSum
      }

      return {
        name: subScore[0],
        val: val
      }
    })

    $scope.subScoreRatios = subScoreRatios
  })


  .controller("personSnippetCtrl", function($scope){

  })


angular.module('staticPages', [
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl: 'static-pages/landing.tpl.html',
      controller: 'landingPageCtrl'
    })
  })


  .controller("landingPageCtrl", function($scope,
                                          $http,
                                          $rootScope,
                                          PageService){








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

angular.module('templates.app', ['directives/language-icon.tpl.html', 'header/header.tpl.html', 'header/search-result.tpl.html', 'package-page/dep-node.tpl.html', 'package-page/package-page.tpl.html', 'person-page/person-page.tpl.html', 'snippet/impact-popover.tpl.html', 'snippet/package-snippet.tpl.html', 'snippet/person-snippet.tpl.html', 'static-pages/landing.tpl.html', 'top/top.tpl.html']);

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
    "   <div class=\"ti-menu\">\n" +
    "\n" +
    "      <a href=\"top/packages\" class=\"menu-link\" id=\"leaders-menu-link\">\n" +
    "         leaderboard\n" +
    "      </a>\n" +
    "      <a href=\"about\" class=\"menu-link\">\n" +
    "         about\n" +
    "      </a>\n" +
    "   </div>\n" +
    "</div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("header/search-result.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("header/search-result.tpl.html",
    "\n" +
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
    "<div class=\"package-page\">\n" +
    "   <div class=\"ti-page-header\">\n" +
    "      <h1>\n" +
    "         <span class=\"text\">\n" +
    "            {{ package.name }}\n" +
    "         </span>\n" +
    "         <span class=\"indegree\">{{ package.indegree }} direct reverse dependencies</span>\n" +
    "      </h1>\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "   <div class=\"ti-page-body\">\n" +
    "\n" +
    "      <div class=\"dep-nodes-tree\" ng-include=\"'package-page/dep-node.tpl.html'\">\n" +
    "      </div>\n" +
    "   </div>\n" +
    "\n" +
    "</div>\n" +
    "");
}]);

angular.module("person-page/person-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("person-page/person-page.tpl.html",
    "<div class=\"person-page\">\n" +
    "   <div class=\"ti-page-header\">\n" +
    "      <h1>\n" +
    "         <img ng-src=\"{{ person.icon }}\" alt=\"\"/>\n" +
    "         <span class=\"text\">\n" +
    "            {{ person.name }}\n" +
    "         </span>\n" +
    "      </h1>\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "   <div class=\"ti-page-body\">\n" +
    "\n" +
    "      <div class=\"packages\">\n" +
    "         <div class=\"person-package\" ng-repeat=\"package in person.person_packages | orderBy:'!credit_points'\">\n" +
    "            <span class=\"roles\" ng-repeat=\"role in package.roles\">\n" +
    "               <span class=\"role author\" ng-if=\"role.name=='author'\">auth</span>\n" +
    "               <span class=\"role github-contrib\" ng-if=\"role.name=='github_contributor'\">contrib</span>\n" +
    "               <span class=\"role owner\" ng-if=\"role.name=='github_owner'\">owner</span>\n" +
    "\n" +
    "\n" +
    "            </span>\n" +
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
    "   <div class=\"head metric\">\n" +
    "      <span class=\"name\">Impact:</span>\n" +
    "      <span class=\"descr\">\n" +
    "         <span class=\"val\">{{ floor(package.impact) }}<span class=\"small\">/10k</span></span>\n" +
    "      </span>\n" +
    "   </div>\n" +
    "\n" +
    "   <div class=\"impact\">\n" +
    "\n" +
    "      <div class=\"sub-score citations metric\" ng-show=\"package.num_citations\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-file-text-o\"></i>\n" +
    "            Citations\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ package.num_citations }}</span>\n" +
    "            <span class=\"paren\">({{ round(package.num_citations_percentile * 100) }}%)</span>\n" +
    "         </span>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"sub-score pagerank metric\" ng-show=\"package.pagerank\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-exchange\"></i>\n" +
    "            Dependency PageRank\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ nFormatter(package.pagerank) }} </span>\n" +
    "            <span class=\"paren\">({{ round(package.pagerank_percentile * 100 )}}%)</span>\n" +
    "         </span>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"sub-score downloads metric\" ng-show=\"package.num_downloads\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-download\"></i>\n" +
    "            Downloads\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ nFormatter(package.num_downloads)}}</span>\n" +
    "            <span class=\"paren\">({{ round(package.num_downloads_percentile * 100) }}%)</span>\n" +
    "         </span>\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"sub-score stars metric\" ng-show=\"package.num_stars\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-star-o\"></i>\n" +
    "            Github stars\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ nFormatter( package.num_stars ) }} </span>\n" +
    "            <span class=\"paren\">({{ round(package.num_stars_percentile * 100) }}%)</span>\n" +
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
    "         popover-placement=\"top\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-template=\"'snippet/impact-popover.tpl.html'\">\n" +
    "\n" +
    "      <span class=\"one-metric metric\">\n" +
    "         {{ format.short(package.impact) }}\n" +
    "      </span>\n" +
    "\n" +
    "\n" +
    "      <span class=\"vis\">\n" +
    "         <!--\n" +
    "         <span class=\"vis-bar\" style=\"width: {{ package.impact }}%;\">\n" +
    "            <span ng-repeat=\"subScoreRatio in subScoreRatios\"\n" +
    "                  class=\"subscore subscore-{{ subScoreRatio.name }}\"\n" +
    "                  style=\"width: {{ subScoreRatio.val * 100 }}%;\"></span>\n" +
    "         </span>\n" +
    "         -->\n" +
    "\n" +
    "      </span>\n" +
    "\n" +
    "   </span>\n" +
    "\n" +
    "   <span class=\"metadata\">\n" +
    "      <span class=\"name-container\">\n" +
    "\n" +
    "         <span class=\"icon\">\n" +
    "            <span class=\"language-icon r\"\n" +
    "                  ng-if=\"package.language=='r'\"\n" +
    "                 tooltip=\"R package\">\n" +
    "               R\n" +
    "            </span>\n" +
    "            <span class=\"language-icon python\"\n" +
    "                  ng-if=\"package.language=='python'\"\n" +
    "                 tooltip=\"Python package\">\n" +
    "               py\n" +
    "            </span>\n" +
    "         </span>\n" +
    "\n" +
    "\n" +
    "         <a class=\"name\" tooltip=\"click for more info\" href=\"package/{{ package.language }}/{{ package.name }}\">\n" +
    "            {{ package.name }}\n" +
    "         </a>\n" +
    "         <i popover-title=\"aca-what?\"\n" +
    "            popover-trigger=\"mouseenter\"\n" +
    "            popover=\"content!\"\n" +
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
    "      <span class=\"vis\">\n" +
    "         <!--\n" +
    "         <span class=\"vis-bar\" style=\"width: {{ package.impact }}%;\">\n" +
    "            <span ng-repeat=\"subScoreRatio in subScoreRatios\"\n" +
    "                  class=\"subscore subscore-{{ subScoreRatio.name }}\"\n" +
    "                  style=\"width: {{ subScoreRatio.val * 100 }}%;\"></span>\n" +
    "         </span>\n" +
    "         -->\n" +
    "\n" +
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
    "            popover=\"We infer academic status based on factors like email address, citedness, institution.\"\n" +
    "            ng-show=\"person.is_academic\"\n" +
    "            class=\"is-academic fa fa-graduation-cap\"></i>\n" +
    "\n" +
    "\n" +
    "         <span class=\"person-packages\">\n" +
    "            <span class=\"works-on\">{{ person.num_packages }} packages including: </span>\n" +
    "            <span class=\"package\" ng-repeat=\"package in person.person_packages | orderBy: '-person_project_impact'\">\n" +
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
    "            <li class=\"filter-option\" ng-click=\"filters.set('type', 'people')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type == 'people'\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"filters.d.type != 'people'\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "\n" +
    "               <span class=\"text\">people</span>\n" +
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
    "         <h3>written in</h3>\n" +
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
    "         <h3>and only</h3>\n" +
    "         <ul>\n" +
    "            <li class=\"filter-option\" ng-click=\"filters.toggle('only_academic')\">\n" +
    "               <span class=\"status\" ng-if=\"filters.d.only_academic\">\n" +
    "                  <i class=\"fa fa-check-square-o\"></i>\n" +
    "               </span>\n" +
    "               <span class=\"status\" ng-if=\"!filters.d.only_academic\">\n" +
    "                  <i class=\"fa fa-square-o\"></i>\n" +
    "               </span>\n" +
    "\n" +
    "               <span class=\"text\">academic projects</span>\n" +
    "            </li>\n" +
    "         </ul>\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "   <div class=\"main\">\n" +
    "\n" +
    "      <div class=\"ti-page-header leaderboard-header\">\n" +
    "         <h2>\n" +
    "            <span class=\"text\">\n" +
    "               Top\n" +
    "               <span class=\"language\">{{ filters.d.language }}</span>\n" +
    "               <span class=\"leaders-type\">{{ filters.d.type }}</span>\n" +
    "               <span class=\"filters\" ng-show=\"leaders.filters.length\">\n" +
    "\n" +
    "               </span>\n" +
    "            </span>\n" +
    "         </h2>\n" +
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
