var module = angular.module('burn', []);

module.controller("CreateCtl", ['$scope', '$http', function($scope, $http) {
  $scope.generate_password = true;
  $scope.step = 1;

  var feedback = function(status, reason) {
    console.log(reason);
    $scope.status = status;
    $scope.reason = reason;
  };

  var step2 = function(storage_key, encryption_key) {
    feedback("info", "Done!");
    $scope.share_url = document.location+storage_key+"#"+encodeURIComponent(encryption_key);
    $scope.step = 2;
  };

  $scope.send = function(message) {
    if(!message || message.length == 0) {
      return feedback("info", "Type something!");      
    }

    console.log(message);
    var password = $scope.user_password;
    if(!password || password == "" || password.length == 0) {
      feedback("info", "generating a password...");
      password = sjcl.codec.hex.fromBits(sjcl.random.randomWords(8));
    }

    console.log(password);

    feedback("info", "encrypting...");
    message = sjcl.encrypt(password, message);
    message = btoa(JSON.stringify(message));

    feedback("info", "sending to server...");

    $http.post("/create", {message: message})
    .success(function(data) {
      step2(data, password);
    })
    .error(function(data) {
      feedback("error", data);
    });
  };
}]);

module.controller("OpenCtl", ['$scope', function($scope) {
  var password = decodeURIComponent(document.location.hash);
  password = password.substr(1, password.length-1);
  console.log(password);
  var message = document.getElementById("themessage").value;
  console.log(message);
  var debased = atob(message);
  message = JSON.parse(debased);
  $scope.decrypted = sjcl.decrypt(password, message);
}]);
