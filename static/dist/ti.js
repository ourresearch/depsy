/* yay impactstory */
angular.module('app', [
  // external libs
  'ngRoute',
  'ngResource',
  'ui.bootstrap',
  'satellizer',
  'snap', // hosted locally

  'templates.app',  // this is how it accesses the cached templates in ti.js

  'landingPage',
  'profilePage',
  'articlePage',

  'resourcesModule',
  'currentUserService',
  'pageService'

]);




angular.module('app').config(function ($routeProvider,
                                       $authProvider, // from satellizer
                                       snapRemoteProvider,
                                       $locationProvider) {
  $locationProvider.html5Mode(true);
  $authProvider.github({
    clientId: '46b1f697afdd04e119fb' // hard-coded for now
  });
  snapRemoteProvider.globalOptions.disable = 'left';


//  paginationTemplateProvider.setPath('directives/pagination.tpl.html')
});


angular.module('app').run(function($route,
                                   $rootScope,
                                   $timeout,
                                   $location ) {

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
  snapRemote,
  PageService,
  CurrentUser,
  $auth){

  $scope.isAuthenticated = function() {
    return $auth.isAuthenticated();
  };
  $scope.logout = function(){
    $auth.logout("/")
  }


  $scope.authenticate = function() {
    $auth.authenticate("github").then(function(resp){
      console.log("authenticated. loading current user.")
      CurrentUser.get().$promise.then(
        function(resp){
          console.log("got current user", resp)
          $location.path("/u/" + resp["username"])
        },
        function(resp){
          console.log("there was an error getting the current user.", resp)
        }
      )
    })
  };


  $scope.page = PageService
  $scope.currentUser = CurrentUser
  CurrentUser.get()


  /*
  $scope.$on('$routeChangeError', function(event, current, previous, rejection){
    RouteChangeErrorHandler.handle(event, current, previous, rejection)
  });
  */

  $scope.$on('$routeChangeSuccess', function(next, current){
    snapRemote.close()
    PageService.reset()
  })

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
















angular.module('landingPage', [
    'ngRoute',
    'profileService'
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl: 'landing-page/landing.tpl.html',
      controller: 'landingPageCtrl'
    })
  })


  .controller("landingPageCtrl", function($scope,
                                          $http,
                                          $auth, // from satellizer
                                          $rootScope,
                                          PageService,
                                          ProfileService){


    PageService.d.hasDarkBg = true

    $scope.newProfile = {}
    $scope.newProfile.coreJournals = [{}]

    $scope.makeProfile = function(){
      ProfileService.createProfile(
        $scope.newProfile.name,
        $scope.newProfile.pmids.split("\n"),
        _.pluck($scope.newProfile.coreJournals, "name")
      )
    }

    $scope.addCoreJournal = function(){
      console.log("adding a core journal field")
      $scope.newProfile.coreJournals.push({})
    }


    $scope.getJournalNames = function(nameStartsWith){
      return $http.get("api/journals/" + nameStartsWith)
      .then(function(resp){
          return resp.data
      })
    }

  })



angular.module('profilePage', [
    'ngRoute',
    'profileService',
    "directives.languageIcon"
  ])



  .config(function($routeProvider) {
    $routeProvider.when('/u/:slug', {
      templateUrl: 'profile-page/profile.tpl.html',
      controller: 'profilePageCtrl',
      resolve: {
        profileResp: function($http, $route){
          var url = "/api/u/" + $route.current.params.slug
          return $http.get(url)
        }
      }
    })
  })



  .controller("profilePageCtrl", function($scope,
                                          $routeParams,
                                          profileResp){
    $scope.profile = profileResp.data
    console.log("here's the profile", $scope.profile)






  })



angular.module('resourcesModule', [])
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
    var defaultData = {
      hasDarkBg: false
    }

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
angular.module('templates.app', ['article-page/article-page.tpl.html', 'directives/language-icon.tpl.html', 'header.tpl.html', 'landing-page/landing.tpl.html', 'profile-page/profile.tpl.html', 'side-menu.tpl.html']);

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

angular.module("header.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("header.tpl.html",
    "<div class=\"header\">\n" +
    "   <h1>\n" +
    "      <a href=\"/\">\n" +
    "         <img src=\"static/img/impactstory-software.png\" alt=\"Impactstory software\"/>\n" +
    "      </a>\n" +
    "   </h1>\n" +
    "   <div class=\"controls\">\n" +
    "      <span class=\"menu-button\"\n" +
    "            ng-class=\"{'on-dark-bg': page.d.hasDarkBg}\"\n" +
    "            snap-toggle=\"right\">\n" +
    "         <i class=\"fa fa-bars\"></i>\n" +
    "      </span>\n" +
    "   </div>\n" +
    "</div>");
}]);

angular.module("landing-page/landing.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("landing-page/landing.tpl.html",
    "<div class=\"landing\">\n" +
    "   <div class=\"tagline\">\n" +
    "      Discover the full impact of your research software:\n" +
    "      citations, forks, reverse dependencies and more.\n" +
    "   </div>\n" +
    "   <div class=\"big-action-button\">\n" +
    "      <span class=\"btn btn-lg btn-primary\" ng-click=\"authenticate()\">\n" +
    "         <i class=\"fa fa-github\"></i>\n" +
    "         Sign in with GitHub\n" +
    "      </span>\n" +
    "   </div>\n" +
    "\n" +
    "</div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("profile-page/profile.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("profile-page/profile.tpl.html",
    "<div class=\"profile-page\">\n" +
    "   <div class=\"owner-info\">\n" +
    "      <img ng-src=\"{{ profile.avatar_url }}\" alt=\"\"/>\n" +
    "      <h2>{{ profile.name }}</h2>\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "   <div class=\"repos\">\n" +
    "      <div class=\"repo\" ng-repeat=\"repo in profile.repos | orderBy: 'language'\">\n" +
    "         <div class=\"meta\">\n" +
    "            <h3>\n" +
    "               <span class=\"repo-name\">\n" +
    "                  {{ repo.name }}\n" +
    "               </span>\n" +
    "               <language-icon language=\"{{ repo.language }}\"></language-icon>\n" +
    "               </h3>\n" +
    "            <span class=\"description\">{{ repo.description }}</span>\n" +
    "            <a class=\"repo_url\" href=\"{{ profile.html_url }}/{{ repo.name }}\"><i class=\"fa fa-share\"></i></a>\n" +
    "         </div>\n" +
    "         <div class=\"impact\">\n" +
    "            <div class=\"stars metric\" ng-show=\"repo.github_stargazers_count\">\n" +
    "               <i class=\"fa fa-star-o\"></i>\n" +
    "               <span class=\"val\">{{ repo.github_stargazers_count }}</span>\n" +
    "               <span class=\"descr\">stars</span>\n" +
    "            </div>\n" +
    "            <div class=\"forks metric\" ng-show=\"repo.github_forks_count\">\n" +
    "               <i class=\"fa fa-code-fork\"></i>\n" +
    "               <span class=\"val\">{{ repo.github_forks_count }}</span>\n" +
    "               <span class=\"descr\">forks</span>\n" +
    "            </div>\n" +
    "\n" +
    "\n" +
    "            <div class=\"subscribers\" ng-show=\"repo.subscribers_count\">\n" +
    "               <i class=\"fa fa-eye\"></i>\n" +
    "               <span class=\"val\">{{ repo.subscribers_count }}</span>\n" +
    "               <span class=\"descr\">subscribers</span>\n" +
    "               <span class=\"subscriber-list\" ng-repeat=\"subscriber in repo.subscribers\">\n" +
    "                  <a class=\"subscriber-name\" href=\"{{ subscriber.html_url }}\">\n" +
    "                     {{ subscriber.login }}\n" +
    "                  </a>\n" +
    "               </span>\n" +
    "            </div>      \n" +
    "            <div class=\"downloads\" ng-show=\"repo.total_downloads\">\n" +
    "               <i class=\"fa fa-cloud-download\"></i>\n" +
    "               <span class=\"val\">{{ repo.total_downloads }}</span>\n" +
    "               <span class=\"descr\">downloads from CRAN</span>\n" +
    "            </div>\n" +
    "            <div class=\"used_by\" ng-show=\"repo.used_by\">\n" +
    "               <i class=\"fa fa-cubes\"></i>\n" +
    "               <span class=\"val\">{{ repo.used_by_count }}</span>\n" +
    "               <span class=\"descr\">R packages use this package: </span>\n" +
    "               <span class=\"used-by-list\">{{ repo.used_by }}</span>\n" +
    "            </div>\n" +
    "\n" +
    "            </div>                         \n" +
    "         </div>\n" +
    "\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "\n" +
    "</div>\n" +
    "");
}]);

angular.module("side-menu.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("side-menu.tpl.html",
    "<ul class=\"our-nav not-signed-in\" ng-show=\"!isAuthenticated()\">\n" +
    "   <li>\n" +
    "      <a ng-click=\"authenticate()\">\n" +
    "         <i class=\"fa fa-sign-in\"></i>\n" +
    "         Sign in\n" +
    "      </a>\n" +
    "   </li>\n" +
    "</ul>\n" +
    "\n" +
    "<ul class=\"our-nav signed-in\" ng-show=\"isAuthenticated()\">\n" +
    "   <li>\n" +
    "      <a href=\"/u/{{ currentUser.d.username }}\" class=\"user-name-and-pic\">\n" +
    "         <img src=\"{{ currentUser.d.avatar_url }}\"/>\n" +
    "         <span class=\"name\">\n" +
    "            {{ currentUser.d.name }}\n" +
    "         </span>\n" +
    "      </a>\n" +
    "   </li>\n" +
    "   <li>\n" +
    "      <a href=\"/settings\">\n" +
    "         <i class=\"fa fa-cog\"></i>\n" +
    "         Settings\n" +
    "      </a>\n" +
    "   </li>\n" +
    "\n" +
    "\n" +
    "   <li>\n" +
    "      <a href=\"/\" ng-click=\"logout()\">\n" +
    "         <i class=\"fa fa-sign-out\"></i>\n" +
    "         Log out\n" +
    "      </a>\n" +
    "   </li>\n" +
    "</ul>\n" +
    "\n" +
    "<div class=\"bottom-menu\">\n" +
    "   <ul class=\"our-nav\">\n" +
    "      <!--\n" +
    "      <li>\n" +
    "         <a href=\"/about\">\n" +
    "            About\n" +
    "         </a>\n" +
    "      </li>\n" +
    "      -->\n" +
    "   </ul>\n" +
    "   <a class=\"home-link\" href=\"/\">\n" +
    "      <img src=\"static/img/impactstory-logo.png\" alt=\"\"/>\n" +
    "   </a>\n" +
    "</div>");
}]);
