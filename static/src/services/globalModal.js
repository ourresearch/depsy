angular.module('globalModal', [
  ])

  .factory("GlobalModal", function($modal){

    var instance // this is the global modal instance everyone will use
    var msg

    var modalOpts = {
      animation: true,
      backdrop: "static",
      keyboard: false,
      templateUrl: 'services/global-modal.tpl.html',
      controller: 'GlobalModalCtrl'
    }

    function getInstance(){
      if (!instance){
        instance = $modal.open(modalOpts)
      }
      return instance
    }

    function open(newMsg){
      if (newMsg){
        msg = newMsg
      }
      return getInstance()
    }

    function close(){
      msg = null
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
      close: close,
      getMsg: function(){
        return msg
      },
      setMsg: function(newMsg){
        msg = newMsg
      }
    }


  })

  .controller("GlobalModalCtrl", function($scope, GlobalModal){
    console.log("GlobalModalCtrl loaded")
    $scope.GlobalModal = GlobalModal
  })