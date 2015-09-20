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
  'articlePage',
  'header',
  'packageSnippet',

  'resourcesModule',
  'pageService',

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
    ngProgress.complete()
  })
  $rootScope.$on('$routeChangeError', function(event, current, previous, rejection){
    console.log("$routeChangeError")
    ngProgress.complete()
  });

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
  PageService){



  $scope.page = PageService

  $scope.nFormatter = function(num){
      // from http://stackoverflow.com/a/14994860/226013
      if (num >= 1000000) {
          return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
      }
      if (num >= 1000) {
          return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
      }
      return Math.floor(num);
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


angular.module('articlePage', [
    'ngRoute',
    'articleService'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/article/:pmid', {
      templateUrl: 'article-page/article-page.tpl.html',
      controller: 'articlePageCtrl'
    })
  })



  .controller("articlePageCtrl", function($scope,
                                          $http,
                                          $routeParams,
                                          ArticleService){

    console.log("article page!", $routeParams)

    ArticleService.getArticle($routeParams.pmid)

    $scope.ArticleService = ArticleService

    $scope.barHorizPos = function(scopusScalingFactor){
      return (scopusScalingFactor * 100) + "%;"
    }

    $scope.barHeight = function(){

    }


    $scope.dotPosition = function(pmid, plotMax, scopus){
      if (scopus > plotMax) {
        return "display: none;"
      }

      var scalingFactorPercent = (scopus / plotMax) * 100

      var verticalJitter = randomPlusOrMinus(2, pmid)
      scalingFactorPercent += randomPlusOrMinus(0.5,pmid.substring(0, 7))

      var ret = "left: " + scalingFactorPercent + "%;"
      ret += "top:" + verticalJitter + "px;"
      return ret
    }

    $scope.medianPosition = function(plotMax, medianScopusCount){

      var medianPos = (medianScopusCount / plotMax * 100) + "%"
      return "left: " + medianPos + ";"
    }


    // not using this right now
    function rand(seed) {
        var x = Math.sin(seed) * 10000;
        return x - Math.floor(x);
    }

    function randomPlusOrMinus(range, seed){

      Math.seedrandom(seed)

      var pick = range * Math.random()
      pick *= (Math.random() > .5 ? -1 : 1)

      return pick
    }


  })  



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







angular.module('packageSnippet', [
  ])



  .controller("packageSnippetCtrl", function($scope){

    $scope.package = $scope.leader

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






    $scope.floor = function(num){
      return Math.floor(num)
    }

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
    return $resource('api/leaders/:type')
  })

  .factory('UserResource', function($resource) {
    return $resource('/api/me')
  });
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
    'ngRoute'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/top/:type', {
      templateUrl: 'top/top.tpl.html',
      controller: 'TopController',
      resolve: {
        leaders: function($http, $route, Leaders){
          console.log("getting rankees")
          return Leaders.get(
            {
              type: $route.current.params.type,
              filters: null,
              sort: null
            },
            function(resp){
              console.log("got a resp from leaders call", resp.list)
            }
          ).$promise
        }
      }
    })
  })


  .controller("TopController", function($scope,
                                          $http,
                                          $rootScope,
                                          $routeParams,
                                          leaders){

    console.log("i'm in hte top page ctrl", $routeParams)
    $scope.leaders = leaders














  })

angular.module('templates.app', ['article-page/article-page.tpl.html', 'directives/language-icon.tpl.html', 'header/header.tpl.html', 'header/search-result.tpl.html', 'package-snippet/package-snippet.tpl.html', 'package-snippet/sort-score-popover.tpl.html', 'person-page/person-page.tpl.html', 'static-pages/landing.tpl.html', 'top/top.tpl.html']);

angular.module("article-page/article-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("article-page/article-page.tpl.html",
    "<div class=\"article-page\">\n" +
    "   <div class=\"header\">\n" +
    "      <div class=\"articles-section\">\n" +
    "         <div class=\"article\" ng-show=\"ArticleService.data.article\">\n" +
    "            <div class=\"metrics\">\n" +
    "               <a href=\"/article/{{ ArticleService.data.article.pmid }}\"\n" +
    "                  tooltip-placement=\"left\"\n" +
    "                  tooltip=\"Citation percentile. Click to see comparison set.\"\n" +
    "                  class=\"percentile scale-{{ colorClass(ArticleService.data.article.percentile) }}\">\n" +
    "                  <span class=\"val\" ng-show=\"article.percentile !== null\">\n" +
    "                     {{ ArticleService.data.article.percentile }}\n" +
    "                  </span>\n" +
    "               </a>\n" +
    "               <span class=\"scopus scopus-small\"\n" +
    "                     tooltip-placement=\"left\"\n" +
    "                     tooltip=\"{{ article.citations }} citations via Scopus\">\n" +
    "                  {{ ArticleService.data.article.citations }}\n" +
    "               </span>\n" +
    "               <span class=\"loading\" ng-show=\"article.percentile === null\">\n" +
    "                  <i class=\"fa fa-refresh fa-spin\"></i>\n" +
    "               </span>\n" +
    "            </div>\n" +
    "\n" +
    "            <div class=\"article-biblio\">\n" +
    "               <span class=\"title\">{{ ArticleService.data.article.biblio.title }}</span>\n" +
    "               <span class=\"under-title\">\n" +
    "                  <span class=\"year\">({{ ArticleService.data.article.biblio.year }})</span>\n" +
    "                  <span class=\"authors\">{{ ArticleService.data.article.biblio.author_string }}</span>\n" +
    "                  <span class=\"journal\">{{ ArticleService.data.article.biblio.journal }}</span>\n" +
    "                  <a class=\"linkout\"\n" +
    "                     href=\"http://www.ncbi.nlm.nih.gov/pubmed/{{ ArticleService.data.article.biblio.pmid }}\">\n" +
    "                        <i class=\"fa fa-external-link\"></i>\n" +
    "                     </a>\n" +
    "               </span>\n" +
    "            </div>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "   </div>\n" +
    "\n" +
    "   <div class=\"articles-infovis journal-dots\">\n" +
    "\n" +
    "      <ul class=\"journal-lines\">\n" +
    "         <li class=\"single-journal-line\" ng-repeat=\"journal in ArticleService.data.article.refset.journals.list\">\n" +
    "            <span class=\"journal-name\">\n" +
    "               {{ journal.name }}\n" +
    "               <span class=\"article-count\">\n" +
    "                  ({{ journal.num_articles }})\n" +
    "               </span>\n" +
    "            </span>\n" +
    "\n" +
    "\n" +
    "\n" +
    "            <div class=\"journal-articles-with-dots\">\n" +
    "               <a class=\"journal-article-dot\"\n" +
    "                  ng-repeat=\"article in journal.articles\"\n" +
    "                  style=\"{{ dotPosition(article.biblio.pmid, ArticleService.data.article.refset.journals.scopus_max_for_plot, article.scopus) }}\"\n" +
    "                  target=\"_blank\"\n" +
    "                  tooltip=\"{{ article.scopus }}: {{ article.biblio.title }}\"\n" +
    "                  href=\"http://www.ncbi.nlm.nih.gov/pubmed/{{ article.biblio.pmid }}\">\n" +
    "                  </a>\n" +
    "               <div class=\"median\"\n" +
    "                    tooltip=\"Median {{ journal.scopus_median }} citations\"\n" +
    "                    style=\"{{ medianPosition(ArticleService.data.article.refset.journals.scopus_max_for_plot, journal.scopus_median) }}\"></div>\n" +
    "               <div style=\"{{ medianPosition(ArticleService.data.article.refset.journals.scopus_max_for_plot, ArticleService.data.article.citations) }}\"\n" +
    "                    class=\"owner-article-scopus scale-{{ colorClass(ArticleService.data.article.percentile) }}\">\n" +
    "\n" +
    "               </div>\n" +
    "\n" +
    "            </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "         </li>\n" +
    "         <div class=\"fake-journal\">\n" +
    "         </div>\n" +
    "      </ul>\n" +
    "   </div>\n" +
    "</div>");
}]);

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
    "         depsy\n" +
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
    "      {{ match.model.sort_score }} packages\n" +
    "   </span>\n" +
    "</a>\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("package-snippet/package-snippet.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("package-snippet/package-snippet.tpl.html",
    "<span class=\"package-snippet\"\n" +
    "     ng-controller=\"packageSnippetCtrl\">\n" +
    "   <span class=\"left-metrics\">\n" +
    "      <span class=\"vis\">\n" +
    "         <span class=\"vis-bar\" style=\"width: {{ package.sort_score * 100 }}%;\">\n" +
    "            <span ng-repeat=\"subScoreRatio in subScoreRatios\"\n" +
    "                  class=\"subscore subscore-{{ subScoreRatio.name }}\"\n" +
    "                  style=\"width: {{ subScoreRatio.val * 100 }}%;\"></span>\n" +
    "         </span>\n" +
    "\n" +
    "      </span>\n" +
    "      <span class=\"one-metric metric\"\n" +
    "            popover-placement=\"top\"\n" +
    "            popover-title=\"Sort score\"\n" +
    "            popover-trigger=\"mouseenter\"\n" +
    "            popover-template=\"'package-snippet/sort-score-popover.tpl.html'\">\n" +
    "         {{ floor(package.sort_score * 10000) }}\n" +
    "      </span>\n" +
    "   </span>\n" +
    "\n" +
    "   <span class=\"metadata\">\n" +
    "      <span class=\"name-container\">\n" +
    "         <i class=\"fa github fa-github-alt github-{{ package.num_stars !== null }}\"></i>\n" +
    "         <a class=\"name\" tooltip=\"click for more info\" href=\"package/{{ package.language }}/{{ package.name }}\">\n" +
    "            {{ package.name }}\n" +
    "         </a>\n" +
    "      </span>\n" +
    "      <span class=\"summary\">{{ package.summary }}</span>\n" +
    "   </span>\n" +
    "\n" +
    "</span>\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("package-snippet/sort-score-popover.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("package-snippet/sort-score-popover.tpl.html",
    "<div id=\"sort-score-popover\">\n" +
    "\n" +
    "\n" +
    "</div>");
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
    "            <span class=\"package-snippet-wrapper\" ng-include=\"'package-snippet/package-snippet.tpl.html'\"></span>\n" +
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
    "   <div class=\"sidebar\">\n" +
    "\n" +
    "      <div class=\"leader-type-select facet\">\n" +
    "         <h3></h3>\n" +
    "         <ul>\n" +
    "            <li class=\"leader-type\"><a href=\"top/packages\">Packages</a></li>\n" +
    "            <li class=\"leader-type\"><a href=\"top/people\">People</a></li>\n" +
    "            <li class=\"leader-type\"><a href=\"top/tags\">Tags</a></li>\n" +
    "         </ul>\n" +
    "\n" +
    "      </div>\n" +
    "\n" +
    "      <div class=\"sort-select facet\">\n" +
    "         <ul class=\"sort-select\">\n" +
    "            <li><a>Sort Score</a></li>\n" +
    "            <li><a>Citations</a></li>\n" +
    "            <li><a>Community</a></li>\n" +
    "         </ul>\n" +
    "\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "      <ul class=\"filters-select facet\">\n" +
    "\n" +
    "      </ul>\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "   <div class=\"main\">\n" +
    "\n" +
    "      <div class=\"ti-page-header\">\n" +
    "         <h2>\n" +
    "            <span class=\"text\">\n" +
    "               Top <span class=\"leaders-type\">{{ leaders.type }}</span>\n" +
    "               <span class=\"sort\">\n" +
    "                  , sorted by <span class=\"val\">{{ leaders.sort }}</span>\n" +
    "               </span>\n" +
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
    "            <div class=\"leader\" ng-repeat=\"leader in leaders.list\">\n" +
    "               <div class=\"package-snippet-wrapper\"  ng-include=\"'package-snippet/package-snippet.tpl.html'\"></div>\n" +
    "            </div>\n" +
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
