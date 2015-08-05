angular.module("directives.languageIcon", [])
.directive("languageIcon", function(){


    var languagesWithIconNames = [
      "c",
      "coffeescript",
      "c++",
      "c#",
      "css",
      "docker",
      "erlang",
      "go",
      "html",
      "java",
      "javascript",
      "nodejs",
      "php",
      "python",
      "rails",
      "ruby"
    ]

    var languagesWithDifferentIconNames = {
      "C++": "cplusplus",
      "C#":"csharp"
    }

    var languagesWithImages = {
      "r": "img/r-logo-flat.png"
    }

    var getIconName = function(languageName){
      if (languagesWithDifferentIconNames[languageName]) {
        return languagesWithDifferentIconNames[languageName]
      }
      else if (languagesWithIconNames.indexOf(languageName.toLowerCase()) > -1){
        return languageName.toLowerCase()
      }
      else {
        return null
      }
    }

    var getIconImg = function(languageName){
      return languagesWithImages[languageName]
    }



    return {
      templateUrl: "directives/language-icon.tpl.html",
      restrict: "EA",
      link: function(scope, elem, attrs) {
        console.log("LanguageIcon.link() ran!", scope, elem, attrs)
        scope.languageIconName = getIconName(attrs.language)
        scope.languageIconImg = getIconImg(attrs.language)

        scope.languageName = attrs.language
      }
    }


  })















