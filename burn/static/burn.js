var module = angular.module('burn', []);

module.controller("CreateCtl", ['$scope', '$http', function($scope, $http) {
  $scope.generate_password = true;
  $scope.step = 1;

  var feedback = function(status, reason) {
    $scope.status = status;
    $scope.reason = reason;
  };

  var step2 = function(storage_key, encryption_key) {
    $scope.share_url = "http://localhost:5000/"+storage_key+"#"+encryption_key;
    $scope.step = 2;
  };

  $scope.send = function(message) {
    console.log(message);

    feedback("info", "encrypting...");

    feedback("info", "sending to server...");

    $http.post("/create", {message: message})
    .success(function(data) {
      step2(data, "");
    })
    .error(function(data) {
      feedback("error", data);
    });
  };
}]);

module.controller("OpenCtl", ['$scope', '$http', function($scope, $http) {

}]);
