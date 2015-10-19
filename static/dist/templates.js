angular.module('templates.app', ['directives/language-icon.tpl.html', 'directives/wheel-popover.tpl.html', 'directives/wheel.tpl.html', 'header/header.tpl.html', 'header/search-result.tpl.html', 'package-page/dep-node.tpl.html', 'package-page/package-page.tpl.html', 'person-page/person-page.tpl.html', 'snippet/package-impact-popover.tpl.html', 'snippet/package-snippet.tpl.html', 'snippet/person-impact-popover.tpl.html', 'snippet/person-mini.tpl.html', 'snippet/person-snippet.tpl.html', 'snippet/tag-snippet.tpl.html', 'static-pages/about.tpl.html', 'static-pages/landing.tpl.html', 'tag-page/tag-page.tpl.html', 'top/top.tpl.html']);

angular.module("directives/language-icon.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("directives/language-icon.tpl.html",
    "<span class=\"language\"\n" +
    "      ng-class=\"{badge: languageName}\"\n" +
    "      style=\"background-color: hsl({{ languageHue }}, 80%, 30%)\">\n" +
    "   {{ languageName }}\n" +
    "</span>");
}]);

angular.module("directives/wheel-popover.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("directives/wheel-popover.tpl.html",
    "<div class=\"wheel-popover\">\n" +
    "   <div class=\"committer\" ng-show=\"wheelData.person_package_commits\">\n" +
    "      <i class=\"fa fa-save\"></i>\n" +
    "\n" +
    "\n" +
    "      commits: {{ myPersonPackage.person_package_commits }}\n" +
    "\n" +
    "   </div>\n" +
    "\n" +
    "</div>");
}]);

angular.module("directives/wheel.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("directives/wheel.tpl.html",
    "<img class='wheel'\n" +
    "     popover-template=\"'directives/wheel-popover.tpl.html'\"\n" +
    "     popover-title=\"{{ percentCredit }}% credit\"\n" +
    "     popover-trigger=\"mouseenter\"\n" +
    "     src='static/img/wheel/{{ wheelVal }}.png' />\n" +
    "");
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
    "<div class=\"page entity-page package-page\">\n" +
    "\n" +
    "\n" +
    "    <div class=\"ti-page-sidebar\">\n" +
    "        <div class=\"sidebar-header\">\n" +
    "\n" +
    "            <div class=\"about\">\n" +
    "                <div class=\"meta\">\n" +
    "               <span class=\"name\">\n" +
    "                  {{ package.name }}\n" +
    "               </span>\n" +
    "\n" +
    "                    <div class=\"summary\">\n" +
    "                        {{ package.summary }}\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "                <div class=\"links\">\n" +
    "                    <a class=\"language-icon r\"\n" +
    "                       href=\"https://cran.r-project.org/web/packages/{{ package.name }}/index.html\"\n" +
    "                       ng-if=\"package.language=='r'\">\n" +
    "                        R\n" +
    "                    </a>\n" +
    "                    <a class=\"language-icon python\"\n" +
    "                       href=\"https://pypi.python.org/pypi/{{ package.name }}\"\n" +
    "                       ng-if=\"package.language=='python'\">\n" +
    "                        py\n" +
    "                    </a>\n" +
    "                    <a class=\"github\"\n" +
    "                       href=\"http://github.com/{{ package.github_owner }}/{{ package.github_repo_name }}\">\n" +
    "                        <i class=\"fa fa-github\"></i>\n" +
    "                    </a>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "        <div class=\"sidebar-section tags\" ng-if=\"package.tags.length\">\n" +
    "            <h3>Tags</h3>\n" +
    "            <div class=\"tags\">\n" +
    "                <a class=\"tag\" ng-repeat=\"tag in package.tags\">\n" +
    "                    {{ tag }}\n" +
    "                </a>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "        <div class=\"sidebar-section contribs\">\n" +
    "            <h3>Key contributors</h3>\n" +
    "            <div class=\"contrib\"\n" +
    "                 ng-repeat=\"person_package in package.top_contribs | orderBy: '-credit'\">\n" +
    "                <wheel></wheel>\n" +
    "                <img class=\"person-icon\" src=\"{{ person_package.icon_small }}\" alt=\"\"/>\n" +
    "                <a class=\"name\" href=\"person/{{ person_package.id }}\">{{ person_package.name }}</a>\n" +
    "                <i popover-title=\"Academic\"\n" +
    "                   popover-trigger=\"mouseenter\"\n" +
    "                   popover=\"We infer academic status based on factors like email address, tags, and institution.\"\n" +
    "                   ng-show=\"person_package.is_academic\"\n" +
    "                   class=\"is-academic fa fa-graduation-cap\"></i>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "        <div class=\"sidebar-section actions\">\n" +
    "            <a class=\"json-link btn btn-default\"\n" +
    "               popover-title=\"View this page as JSON\"\n" +
    "               popover-placement=\"right\"\n" +
    "               popover-trigger=\"mouseenter\"\n" +
    "               target=\"_self\"\n" +
    "               popover=\"Everything here is open data, free to use for your own projects. You can also check out our API for more systematic access.\"\n" +
    "               href=\"api/package/{{ package.host }}/{{ package.name }}\">\n" +
    "                <i class=\"fa fa-download\"></i>\n" +
    "                JSON\n" +
    "            </a>\n" +
    "\n" +
    "            <!--\n" +
    "         <a href=\"https://twitter.com/share?url={{ encodeURIComponent('http://google.com') }}\" >Tweet</a>\n" +
    "         -->\n" +
    "\n" +
    "\n" +
    "        </div>\n" +
    "\n" +
    "\n" +
    "    </div>\n" +
    "\n" +
    "\n" +
    "    <div class=\"ti-page-body\">\n" +
    "\n" +
    "        <div class=\"subscore package-page-subscore {{ subscore.name }}\"\n" +
    "             ng-repeat=\"subscore in package.subscores\">\n" +
    "            <h3>\n" +
    "                <i class=\"fa {{ subscore.icon }}\"></i>\n" +
    "                {{ subscore.display_name }}\n" +
    "            </h3>\n" +
    "            <div class=\"metrics\">\n" +
    "                <div class=\"summary-metrics\">\n" +
    "                    <div class=\"vis\">\n" +
    "                        <div class=\"bar-outer\">\n" +
    "                            <div class=\"bar-inner {{ subscore.name }}\" style=\"height: {{ subscore.score /10 }}%\"></div>\n" +
    "                        </div>\n" +
    "                    </div>\n" +
    "               <span class=\"main-metric\">\n" +
    "                  {{ format.short(subscore.val) }}\n" +
    "               </span>\n" +
    "               <span class=\"percentile\">\n" +
    "                  <span class=\"val\">\n" +
    "                     {{ format.round(subscore.percentile * 100) }}\n" +
    "                  </span>\n" +
    "                  <span class=\"descr\">\n" +
    "                     percentile\n" +
    "                  </span>\n" +
    "               </span>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "            <div class=\"explanation\">\n" +
    "\n" +
    "            </div>\n" +
    "\n" +
    "            <div class=\"top-importers\" ng-show=\"subscore.name=='pagerank' && package.indegree\">\n" +
    "                <h4>\n" +
    "                    <div class=\"main\">Reused by </div>\n" +
    "                    <div class=\"subheading\">\n" +
    "                        <span class=\"val\">{{ package.indegree }}</span> other projects on {{ package.host }} and GitHub.\n" +
    "                      <span class=\"more\" ng-show=\"package.top_neighbors.length < package.indegree\">\n" +
    "                          (showing the top {{ package.top_neighbors.length }})\n" +
    "                      </span>\n" +
    "                    </div>\n" +
    "                </h4>\n" +
    "\n" +
    "                <div class=\"dep-container\" ng-repeat=\"dep in package.top_neighbors\">\n" +
    "\n" +
    "\n" +
    "                    <!-- CRAN or PyPi package -->\n" +
    "                    <div class=\"package dep\" ng-if=\"dep.host\">\n" +
    "                        <div class=\"top-line\">\n" +
    "                            <div class=\"vis impact-stick\">\n" +
    "                                <div ng-repeat=\"subscore in dep.subscores\"\n" +
    "                                     class=\"bar-inner {{ subscore.name }}\"\n" +
    "                                     style=\"width: {{ subscore.score / 33.3333 }}%;\">\n" +
    "                                </div>\n" +
    "                            </div>\n" +
    "\n" +
    "                            <a class=\"name\" href=\"package/{{ dep.language }}/{{ dep.name }}\">\n" +
    "                                {{ dep.name }}\n" +
    "                            </a>\n" +
    "\n" +
    "                            <i popover-title=\"Academic\"\n" +
    "                               popover-trigger=\"mouseenter\"\n" +
    "                               popover=\"We infer academic status based on factors like email address, tags, and institution.\"\n" +
    "                               ng-show=\"dep.is_academic\"\n" +
    "                               class=\"is-academic fa fa-graduation-cap\"></i>\n" +
    "                        </div>\n" +
    "                        <div class=\"underline\">\n" +
    "                            {{ dep.summary }}\n" +
    "                        </div>\n" +
    "                    </div>\n" +
    "\n" +
    "                    <!-- GitHub repo -->\n" +
    "                    <div class=\"github dep\" ng-if=\"!dep.host\">\n" +
    "                        <div class=\"top-line\">\n" +
    "                            <div class=\"vis\"\n" +
    "                                 popover-trigger=\"mouseenter\"\n" +
    "                                 popover=\"{{ dep.stars }} GitHub stars\">\n" +
    "                                {{ dep.stars }}\n" +
    "                                <i class=\"fa fa-star\"></i>\n" +
    "                            </div>\n" +
    "\n" +
    "                            <span class=\"name\">\n" +
    "                                <a href=\"http://github.com/{{ dep.login }}/{{ dep.repo_name }}\"\n" +
    "                                   popover-trigger=\"mouseenter\"\n" +
    "                                   popover=\"This {{ dep.language }} project is not in CRAN or PyPi, but it is viewable on GitHub\"\n" +
    "                                   class=\"github-link\">\n" +
    "                                    <i class=\"fa fa-github\"></i>\n" +
    "                                </a>\n" +
    "                                {{ dep.repo_name }}\n" +
    "                            </span>\n" +
    "                        </div>\n" +
    "                        <div class=\"underline\">\n" +
    "                            {{ dep.summary }}\n" +
    "                        </div>\n" +
    "                    </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "                </div>\n" +
    "\n" +
    "\n" +
    "            </div>\n" +
    "\n" +
    "        </div>\n" +
    "\n" +
    "    </div>\n" +
    "\n" +
    "\n" +
    "</div>\n" +
    "");
}]);

angular.module("person-page/person-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("person-page/person-page.tpl.html",
    "<div class=\"page entity-page person-page\">\n" +
    "   <div class=\"ti-page-sidebar\">\n" +
    "      <div class=\"sidebar-header\">\n" +
    "\n" +
    "         <div class=\"person-about\">\n" +
    "            <img ng-src=\"{{ person.icon }}\" alt=\"\"/>\n" +
    "            <div class=\"score\">\n" +
    "               <span class=\"impact\">\n" +
    "                  {{ format.short(person.impact) }}\n" +
    "               </span>\n" +
    "               <span class=\"rank\" ng-show=\"!person.is_organization\">\n" +
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
    "               <a ng-if=\"person.github_login\" class=\"account\" href=\"http://github.com/{{ person.github_login }}\">\n" +
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
    "\n" +
    "      <div class=\"sidebar-section impact\">\n" +
    "         <h3>Impact</h3>\n" +
    "         <div class=\"vis\">\n" +
    "            <div class=\"subscore {{ subscore.name }}\"\n" +
    "                 ng-if=\"subscore.val > 0\"\n" +
    "                 ng-repeat=\"subscore in person.subscores\">\n" +
    "               <div class=\"bar-outer\">\n" +
    "                  <div class=\"bar-inner {{ subscore.name }}\" style=\"width: {{ subscore.score / 10 }}%;\"></div>\n" +
    "               </div>\n" +
    "               <div class=\"subscore-label\">\n" +
    "                  <span class=\"val\">{{ format.short(subscore.val) }}</span>\n" +
    "                  <span class=\"text\">{{ subscore.display_name }}</span>\n" +
    "               </div>\n" +
    "\n" +
    "            </div>\n" +
    "         </div>\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "      <!--\n" +
    "      <div class=\"impact-descr\" ng-if=\"!person.is_organization\">\n" +
    "         <h3>Impact</h3>\n" +
    "         <div class=\"impact-copy\" ng-show=\"person.main_language=='python'\">\n" +
    "            Ranked #{{ format.commas(person.impact_rank) }} in impact out of {{ format.commas(person.impact_rank_max) }} Pythonistas on PyPi. That's based on summed package impacts, adjusted by percent contributions.\n" +
    "         </div>\n" +
    "         <div class=\"impact-copy\" ng-show=\"person.main_language=='r'\">\n" +
    "            Ranked #{{ person.impact_rank }} in impact out of {{ person.impact_rank_max }} R coders on CRAN. That's based on summed package impacts, adjusted by percent contributions.\n" +
    "         </div>\n" +
    "      </div>\n" +
    "      -->\n" +
    "\n" +
    "      <div class=\"top-tags\" ng-if=\"package.tags.length\">\n" +
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
    "      <div class=\"top-collabs\" ng-show=\"person.top_collabs.length\">\n" +
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
    "               <wheel roles=\"\" credit=\"{{ package.person_package_credit }}\"></wheel>\n" +
    "\n" +
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

angular.module("snippet/package-impact-popover.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("snippet/package-impact-popover.tpl.html",
    "<div class=\"package impact-popover\">\n" +
    "   <div class=\"impact\">\n" +
    "\n" +
    "      <!-- repeat for each subscore -->\n" +
    "      <div class=\"subscore {{ subscore.name }} metric\"\n" +
    "           ng-if=\"subscore.val > 0\"\n" +
    "           ng-repeat=\"subscore in package.subscores\">\n" +
    "         <span class=\"name\">\n" +
    "            <i class=\"fa fa-file-text-o\" ng-if=\"subscore.name=='num_mentions'\"></i>\n" +
    "            <i class=\"fa fa-exchange\" ng-if=\"subscore.name=='pagerank'\"></i>\n" +
    "            <i class=\"fa fa-download\" ng-if=\"subscore.name=='num_downloads'\"></i>\n" +
    "            {{ subscore.display_name }}\n" +
    "         </span>\n" +
    "         <span class=\"descr\">\n" +
    "            <span class=\"val\">{{ format.short(subscore.val) }}</span>\n" +
    "         </span>\n" +
    "      </div>\n" +
    "\n" +
    "\n" +
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
    "         popover-template=\"'snippet/package-impact-popover.tpl.html'\">\n" +
    "\n" +
    "      <div class=\"vis impact-stick\">\n" +
    "            <div ng-repeat=\"subscore in package.subscores\"\n" +
    "                 class=\"bar-inner {{ subscore.name }}\"\n" +
    "                 style=\"width: {{ subscore.score / 33.3333 }}%;\">\n" +
    "            </div>\n" +
    "        </div>\n" +
    "\n" +
    "      <div class=\"rank\">\n" +
    "         <span class=\"octothorpe\">#</span>\n" +
    "         <span class=\"val\">\n" +
    "            {{ format.commas(package.impact_rank) }}\n" +
    "         </span>\n" +
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
    "               popover=\"{{ contrib.name }}\"\n" +
    "               popover-trigger=\"mouseenter\"\n" +
    "               class=\"contrib\"\n" +
    "               ng-repeat=\"contrib in package.top_contribs | orderBy: '-credit' | limitTo: 3\">{{ contrib.single_name }}<span\n" +
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

angular.module("snippet/person-impact-popover.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("snippet/person-impact-popover.tpl.html",
    "<div class=\"person impact-popover\">\n" +
    "   coming soon...\n" +
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
    "            Monthly Downloads\n" +
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
    "         popover-title=\"Impact\"\n" +
    "         popover-trigger=\"mouseenter\"\n" +
    "         popover-template=\"'snippet/person-impact-popover.tpl.html'\">\n" +
    "\n" +
    "\n" +
    "      <div class=\"vis impact-stick\">\n" +
    "         <div class=\"subscore {{ subscore.name }}\"\n" +
    "              ng-repeat=\"subscore in person.subscores\">\n" +
    "            <div class=\"bar-outer\">\n" +
    "               <div class=\"bar-inner {{ subscore.name }}\" style=\"height: {{ subscore.score / 10 }}%;\"></div>\n" +
    "            </div>\n" +
    "         </div>\n" +
    "      </div>\n" +
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

angular.module("static-pages/about.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("static-pages/about.tpl.html",
    "<div class=\"about-page static-page\">\n" +
    "   <div class=\"coming-soon\">\n" +
    "      <h1>Coming soon</h1>\n" +
    "      <h2>Many explanations of many things.</h2>\n" +
    "   </div>\n" +
    "\n" +
    "</div>\n" +
    "\n" +
    "\n" +
    "\n" +
    "\n" +
    "");
}]);

angular.module("static-pages/landing.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("static-pages/landing.tpl.html",
    "<div class=\"landing static-page\">\n" +
    "   <div class=\"tagline\">\n" +
    "      foo Find the impact of software packages for Python and R.\n" +
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
    "<div class=\"page entity-page person-page\">\n" +
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
    "            <a class=\"tag\" href=\"tag/{{ tag.name }}\" ng-repeat=\"tag in packages.related_tags | orderBy: '-count'\">\n" +
    "               {{ tag.name }}\n" +
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
    "<div class=\"page leaderboard\">\n" +
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
