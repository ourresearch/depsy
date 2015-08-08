angular.module('currentUserService', [
    'resourcesModule'
  ])



  .factory("CurrentUser", function(UserResource){

    var data = {}


    return {
      d: data,
      get: function(){
        console.log("getting the current user...")
        return UserResource.get(
          function(data){
            console.log("got the current user data", data)
          },
          function(data){
            console.log("error getting current user data", data)
          }
        )
      }
    }


  })