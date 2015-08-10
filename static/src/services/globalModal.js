angular.module('globalModal', [
  ])

  .factory("GlobalModal", function($modal){

    var instance // this is the global modal instance everyone will use
    var modalOpts = {
      animation: true,
      backdrop: "static",
      templateUrl: 'services/global-modal.tpl.html',
      controller: 'GlobalModalCtrl'
    }

    function getInstance(){
      console.log("checking to see if there's a modal instance", instance)
      if (instance){
        return instance
      }
      else {
        instance = $modal.open(modalOpts)

      }
    }

    function open(){
      return getInstance()
    }

    function close(){
      if (!instance){
        return null
      }
      else {
        return instance.close()
      }
    }

    return {
      foo: function(){return 42},
      getInstance: getInstance,
      open: open,
      close: close
    }


  })

  .controller("GlobalModalCtrl", function(){
    console.log("GlobalModalCtrl loaded")
  })