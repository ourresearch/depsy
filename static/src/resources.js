angular.module('resourcesModule', [])
  .factory('Leaders', function($resource) {
    return $resource('api/leaders/:type')
  })

  .factory('UserResource', function($resource) {
    return $resource('/api/me')
  });