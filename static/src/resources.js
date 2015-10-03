angular.module('resourcesModule', [])
  .factory('Leaders', function($resource) {
    return $resource('api/leaderboard')
  })

  .factory('UserResource', function($resource) {
    return $resource('/api/me')
  })

  .factory('PackageResource', function($resource) {
    return $resource('/api/package/:namespace/:name')
  })