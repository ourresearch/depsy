angular.module("directives.languageIcon", [])
.directive("languageIcon", function(){


    var languagesWithIconNames = [

      /*
      "c",
      "coffeescript",
      "c++",
      "c#",
      "erlang",
      "go",
      "rails",
      "ruby",
      */

      "css",
      "html",
      "java",
      "javascript",
      "php",
      "python",
      "perl",
      "r",
      "shell"
    ]


    // not using right now
    var languagesWithDifferentIconNames = {
      "C++": "cplusplus",
      "C#":"csharp"
    }

    var getIconImg = function(languageName){
     if (languagesWithIconNames.indexOf(languageName.toLowerCase()) > -1){
        return languageName.toLowerCase()
      }
      else {
        return null
      }
    }



    return {
      templateUrl: "directives/language-icon.tpl.html",
      restrict: "EA",
      link: function(scope, elem, attrs) {
        console.log("LanguageIcon.link() ran!", scope, elem, attrs)
        scope.languageIconImg = getIconImg(attrs.language)

        scope.languageName = attrs.language
      }
    }


  })















