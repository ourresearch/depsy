angular.module('templates.app', ['article-page/article-page.tpl.html', 'directives/language-icon.tpl.html', 'header.tpl.html', 'landing-page/landing.tpl.html', 'profile-page/profile.tpl.html', 'services/global-modal.tpl.html']);

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
    "      Find the impact of software libraries for Python and R.\n" +
    "   </div>\n" +
    "   <div class=\"search-box\">\n" +
    "    <input type=\"text\"\n" +
    "           ng-model=\"asyncSelected\"\n" +
    "           placeholder=\"Search libraries and authors\"\n" +
    "           typeahead=\"address for address in doSearch($viewValue)\"\n" +
    "           typeahead-loading=\"loadingLocations\"\n" +
    "           typeahead-no-results=\"noResults\"\n" +
    "           class=\"form-control input-lg\">\n" +
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
    "   <h1>boom, profile page!</h1>\n" +
    "\n" +
    "</div>\n" +
    "");
}]);

angular.module("services/global-modal.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("services/global-modal.tpl.html",
    "<div class=\"global-modal\">\n" +
    "   <div class=\"modal-body\">\n" +
    "      <h2 class=\"msg\">\n" +
    "         <i class=\"fa fa-circle-o-notch fa-spin\"></i>\n" +
    "         <span>\n" +
    "            {{ GlobalModal.getMsg() }}\n" +
    "         </span>\n" +
    "      </h2>\n" +
    "      <div class=\"sub-msg\">\n" +
    "         {{ GlobalModal.getSubMsg() }}\n" +
    "      </div>\n" +
    "   </div>\n" +
    "</div>\n" +
    "");
}]);
