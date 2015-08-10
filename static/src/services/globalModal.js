angular.module('globalModal', [
  ])

  .factory("GlobalModal", function($modal){

    var instance // this is the global modal instance everyone will use
    var msg
    var subMsg

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

    function open(newMsg, newSubMsg){
      if (newMsg){
        msg = newMsg
      }
      if (newSubMsg){
        subMsg = newSubMsg
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
      getSubMsg: function(){
        return subMsg
      },
      setMsg: function(newMsg, newSubMsg){
        msg = newMsg
        subMsg = newSubMsg
      }
    }


  })

  .controller("GlobalModalCtrl", function($scope, GlobalModal){
    console.log("GlobalModalCtrl loaded")
    $scope.GlobalModal = GlobalModal
  })