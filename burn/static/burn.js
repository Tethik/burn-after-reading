var module = angular.module('burn', [], function($compileProvider) {
  $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|data):/);
});

var files = [];

function readFiles(target_files) {
  // Clear old files
  files = [];
  console.log(target_files);

  for(var i = 0; i < target_files.length; ++i) {
    var file = target_files[i];
    if (!file) {
      return;
    }

    (function(file) {
      var reader = new FileReader();
      reader.onload = function(e) {
        var contents = e.target.result;
        files.push({ filename: file.name, binary: btoa(contents) });
      };
      reader.readAsBinaryString(file);
    })(file);
  }
}

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
  $scope.burn_after_reading = false;
  $scope.step = 1;
  $scope.expiry = "hour";

  $scope.maxlength = parseInt(document.getElementById('server_says_maxlength_is').value);

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
      password = sjcl.random.randomWords(8); // 32 bits per word. 8*32 = 256 bits.
    } else {
      if(!$scope.user_password || $scope.user_password.length == 0) {
        return feedback("info", "Password can't be empty!");
      }
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

    feedback("info", "encrypting...")
    var rp = {}
    message = sjcl.encrypt(password, message, {}, rp)
    console.log(message)        
    message = JSON.stringify(message)
    console.log(message.length)
    password = rp.key

    encrypted_files = [];
    console.log(files.length)
    if(files) {
      feedback("info", "encrypting files...")
      for(var i = 0; i < files.length; i += 1) {        
        json_file = JSON.stringify(files[i])        
        encrypted_file = sjcl.encrypt(password, json_file, {}, {})
        encrypted_files.push(encrypted_file)        
      }
    }

    feedback("info", "sending to server...")

    $http.post("/create", {
      message: message,
      expiry: expiry_time,
      anonymize_ip: $scope.anonymize_ip,
      burn_after_reading: $scope.burn_after_reading,
      files: encrypted_files,
    })
    .success(function(data) {
      step2(data, password);
    })
    .error(function(data) {
      feedback("error flash", data);
    })
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

  var _decrypt = function(password) {
      $scope.decrypted_files = [];
      var message = document.getElementById("themessage").value;

      message = JSON.parse(message)
      $scope.decrypted = sjcl.decrypt(password, message)

      $scope.decrypted_files = []
      var encrypted_files = document.getElementsByName("files")
      for(var i = 0; i < encrypted_files.length; i += 1) {
        feedback("info", "decrypting file " + (i + 1));
        var encrypted_file = encrypted_files[i].value
        console.log(encrypted_file)
        var decrypted_file = JSON.parse(sjcl.decrypt(password, encrypted_file))
        console.log(decrypted_file)
        $scope.decrypted_files.push(decrypted_file)
      }
  }

  var decrypt = function(password) {

    feedback("info", "decrypting...");

    var fixed = document.getElementById("expiry").value.replace(" ","T");
    var date = convertDate(fixed);
    $scope.expiry = date.toLocaleString();

    try {
      _decrypt(password);
    } catch(err) {
      // Try the base64 decoded, just in case the user copy pasted the url password.
      try {
        _decrypt(sjcl.codec.base64url.toBits(password));
      } catch(err) {
        feedback("error", "Failed to decrypt. Please provide the correct password.");
        console.log(err);
        return false;
      }
    }

    feedback("info", "Successfully decrypted the message.");
    console.log($scope.decrypted);

    return true;
  };

  $scope.copy = function() {
    document.getElementById("thebox").select();
    if(document.execCommand('copy')) {
      feedback("info", "The URL has been copied to your clipboard.")
    } else {
      feedback("error", "Could not copy the URL to your keyboard, your browser may not support this feature.")
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
  $scope.burned = $scope.burn_was_auto = document.getElementById("burned").value == "1";
  

  var time_elements = document.getElementsByTagName("time");
  for(var i = 0; i < time_elements.length; i++) {
    var el = time_elements[i];
    el.innerHTML = convertDate(el.attributes['datetime'].value).toLocaleString();    
  }  

}]);
