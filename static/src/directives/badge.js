angular.module("directives.badge", [])
    .directive("badge", function($modal, $http){

        return {
            templateUrl: "directives/badge.tpl.html",
            restrict: "EA",
            link: function(scope, elem, attrs) {

                var badgeUrl = "api/" + attrs.entity + "/badge"

                scope.openBadgeModal = function(){
                    var modalInstance = $modal.open({
                        controller: "badgeModalCtrl",
                        templateUrl: 'badge-modal.tpl.html',
                        resolve: {
                            badgeMarkup: function () {
                                console.log("making badgeMarkup call to ", badgeUrl)
                                return $http.get(badgeUrl)
                            },
                            badgeUrl: function(){
                                return badgeUrl
                            }
                        }
                    })
                }
            }
        }


    })

    .controller("badgeModalCtrl", function($scope, $sce, $location, badgeMarkup, badgeUrl){
        console.log("running the badgeModalCtrl", badgeMarkup)
        $scope.badgeMarkup = $sce.trustAsHtml(badgeMarkup.data)
        $scope.badgeUrl = badgeUrl
        $scope.currentUrl = $location.absUrl()


    })















