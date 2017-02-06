var module = angular.module('burn', []);

module.factory('_feedback', [function() {
  return function(scope, status, reason) {
    if(status.indexOf("error") > -1) {
      var el = document.getElementById("statusbox");
      el.classList.remove("flash");
      el.offsetWidth = el.offsetWidth;
      el.classList.add("flash");
    }

    console.log(reason);
    scope.status = status;
    scope.reason = reason;
  }
}]);

module.controller("CreateCtl", ['$scope', '$http', '_feedback', function($scope, $http, _feedback) {
  $scope.generate_password = true;
  $scope.anonymize_ip = true;
  $scope.step = 1;
  $scope.expiry = "hour";

  var feedback = function(status, reason) {
    _feedback($scope, status, reason);
  }

  var step2 = function(storage_key, encryption_key) {
    feedback("info", "Done!");
    b64 = sjcl.codec.base64url.fromBits(encryption_key);
    console.log(b64);
    $scope.share_url = document.location+storage_key+"#"+b64;
    $scope.step = 2;
  };

  $scope.copy = function() {
    document.getElementById("theurlbox").select();
    if(document.execCommand('copy')) {
      feedback("info", "The message has been copied to your clipboard.")
    } else {
      feedback("error", "Could not copy the message to your keyboard, your browser may not support this feature.")
    }    
  };

  $scope.send = function(message) {
    if(!message || message.length == 0) {
      return feedback("info", "Type something!");
    }

    console.log(message);
    if($scope.generate_password) {
      feedback("info", "generating a password...");
      password = sjcl.random.randomWords(8); // 32 bits per word. 8*32 = 256 bits. 2^256 combinations.
    } else {
      if(!$scope.user_password || $scope.user_password.length == 0)
        return feedback("info", "Password can't be empty!");
      password = $scope.user_password;
    }

    console.log(password);

    var expiry_time = Date.now();
    if($scope.expiry == "hour") {
      expiry_time += 1000*60*60;
    } else if($scope.expiry == "day") {
      expiry_time += 1000*60*60*24;
    } else if($scope.expiry == "week") {
      expiry_time += 1000*60*60*24*7;
    }

    feedback("info", "encrypting...");
    var rp = {};
    message = sjcl.encrypt(password, message, {}, rp);
    message = btoa(JSON.stringify(message));
    password = rp.key;

    feedback("info", "sending to server...");

    $http.post("/create", {
      message: message,
      expiry: expiry_time,
      anonymize_ip: $scope.anonymize_ip
    })
    .success(function(data) {
      step2(data, password);
    })
    .error(function(data) {
      feedback("error flash", data);
    });
  };
}]);

module.controller("OpenCtl", ['$scope', '$http', '_feedback', function($scope, $http, _feedback) {

  var feedback = function(status, reason) {
    _feedback($scope, status, reason);
  }

  var convertDate = function(datestring) {
    var date = new Date(datestring);
    var newDate = new Date(date.getTime()+date.getTimezoneOffset()*60*1000);
    var offset = date.getTimezoneOffset() / 60;
    var hours = date.getHours();
    newDate.setHours(hours - offset);
    return newDate;
  }

  var decrypt = function(password) {

    feedback("info", "decrypting...");

    try {
      // console.log(id);
      // console.log(password);

      var fixed = document.getElementById("expiry").value.replace(" ","T");
      var date = convertDate(fixed);

      $scope.expiry = date.toLocaleString();

      var message = document.getElementById("themessage").value;
      // console.log(message);
      var debased = atob(message);
      message = JSON.parse(debased);
      $scope.decrypted = sjcl.decrypt(password, message);
    } catch(err) {
      feedback("error", "Failed to decrypt. Please provide the correct password.");
      console.log(err);
      return false;
    }

    feedback("info", "Successfully decrypted the message.");
    console.log($scope.decrypted);

    return true;
  };

  $scope.copy = function() {
    document.getElementById("thebox").select();
    if(document.execCommand('copy')) {
      feedback("info", "The message has been copied to your clipboard.")
    } else {
      feedback("error", "Could not copy the message to your keyboard, your browser may not support this feature.")
    }    
  };

  $scope.burn = function() {
    feedback("info", "Telling server to delete the message...");
    $http.delete("/"+id)
    .success(function() {
      feedback("info", "The message was deleted.")
      $scope.burned = true;
    })
    .error(function(data) {
      feedback("error", data);
    });
  };

  $scope.attempt_decrypt = function() {
    $scope.decrypted_succesfully = decrypt($scope.password);
  };

  var id = decodeURIComponent(document.location.pathname);
  var password = decodeURIComponent(document.location.hash);
  id = id.substr(1, id.length-1);
  password = password.substr(1, password.length-1);
  password = sjcl.codec.base64url.toBits(password);

  $scope.decrypted_succesfully = decrypt(password);

  var time_elements = document.getElementsByTagName("time");
  for(var i = 0; i < time_elements.length; i++) {
    var el = time_elements[i];
    el.innerHTML = convertDate(el.attributes['datetime'].value).toLocaleString();    
  }  

}]);
