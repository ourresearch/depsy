angular.module('resourcesModule', [])
  .factory('UserResource', function($resource) {
    return $resource('/api/me')
  });