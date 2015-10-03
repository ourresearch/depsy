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
    "      <a href=\"leaderboard\" class=\"menu-link\" id=\"leaders-menu-link\">\n" +
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
    "   <div class=\"ti-page-sidebar\">\n" +
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
    "         <div class=\"person-package\" ng-repeat=\"package in person.person_packages | orderBy:'-person_project_impact'\">\n" +
    "            <div class=\"person-package-stats\">\n" +
    "               <span class=\"roles\">\n" +
    "                  <span class=\"role role-{{ role }}\" ng-repeat=\"role in package.roles | orderBy: '-toLowerCase()'\">\n" +
    "                     <i class=\"fa fa-user\" ng-if=\"role=='author'\"></i>\n" +
    "                     <i class=\"fa fa-save\"  ng-if=\"role=='github_contributor'\"></i>\n" +
    "                     <i class=\"fa fa-github\" ng-if=\"role=='github_owner'\"></i>\n" +
    "                  </span>\n" +
    "               </span>\n" +
    "               <div class=\"bar-outside\">\n" +
    "                  <span class=\"bar-inside\" style=\"width: {{ package.person_project_credit * 100 }}%\"></span>\n" +
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
    "\n" +
    "               <span class=\"text\" ng-show=\"filters.d.type=='packages'\">academic projects</span>\n" +
    "               <span class=\"text\" ng-show=\"filters.d.type=='people'\">academics</span>\n" +
    "               <span class=\"text\" ng-show=\"filters.d.type=='tags'\">academic</span>\n" +
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
