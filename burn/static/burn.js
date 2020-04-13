var module = angular.module("burn", [], function ($compileProvider) {
  $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|data):/);
});

var files = [];

async function encrypt(password, message, options, rp) {
  var ciphertext = sjcl.encrypt(password, message, options, rp);
  return ciphertext;
}

function readFile(file) {
  return new Promise((resolve) => {
    (function (file) {
      var reader = new FileReader();
      reader.onload = function (e) {
        var contents = e.target.result;
        resolve({ filename: file.name, data_url: contents });
      };
      reader.readAsDataURL(file);
    })(file);
  });
}

module.factory("_feedback", [
  () => (scope, status, reason) => {
    if (status.indexOf("error") > -1) {
      var el = document.getElementById("statusbox");
      el.classList.remove("flash");
      el.offsetWidth = el.offsetWidth;
      el.classList.add("flash");
    }

    scope.status = status;
    scope.reason = reason;
  },
]);

module.controller("CreateCtl", [
  "$scope",
  "$http",
  "_feedback",
  function ($scope, $http, _feedback) {
    $scope.generate_password = true;
    $scope.anonymize_ip = true;
    $scope.burn_after_reading = false;
    $scope.step = 1;
    $scope.expiry = "hour";
    $scope.message = "";

    $scope.maxlength = (parseInt(document.getElementById("server_says_maxlength_is").value) * 3) / 4;

    var feedback = function (status, reason) {
      _feedback($scope, status, reason);
    };

    var step3 = function (storage_key, encryption_key) {
      feedback("info", "Done!");
      b64 = sjcl.codec.base64url.fromBits(encryption_key);
      $scope.share_url = document.location + storage_key + "#" + b64;
      $scope.step = 3;
    };

    $scope.copy = function () {
      document.getElementById("theurlbox").select();
      if (document.execCommand("copy")) {
        feedback("info", "The message has been copied to your clipboard.");
      } else {
        feedback("error", "Could not copy the message to your keyboard, your browser may not support this feature.");
      }
    };

    $scope.check_filesize = (input) => {
      var files = input.files;
      var s = $scope.message.length;
      for (var i = 0; i < files.length; ++i) {
        s += files[i].size;
      }
      $scope.file_bytes = s;
    };

    // $scope.check_filesize(document.getElementById("files"));

    $scope.send = async function (message) {
      var files = document.getElementById("files").files;
      if ((!message || message.length == 0) && (!files || files.length == 0)) {
        return feedback("info", "Please add a message or files to submit.");
      }

      feedback("info", "generating a password...");
      const password = sjcl.random.randomWords(8); // 32 bits per word. 8*32 = 256 bits.

      var expiry_time = Date.now();
      if ($scope.expiry == "hour") {
        expiry_time += 1000 * 60 * 60;
      } else if ($scope.expiry == "day") {
        expiry_time += 1000 * 60 * 60 * 24;
      } else if ($scope.expiry == "week") {
        expiry_time += 1000 * 60 * 60 * 24 * 7;
      }

      feedback("info", "encrypting...");
      $scope.step = 2;

      const doc = {
        message,
        files: [],
      };

      const fileReads = [];
      if (files) {
        for (var i = 0; i < files.length; i += 1) {
          fileReads.push(readFile(files[i]));
        }
      }
      doc.files = await Promise.all(fileReads);

      const encryptedDocument = await encrypt(password, JSON.stringify(doc));

      feedback("info", "sending to server...");

      $http
        .post("/api/create", {
          expiry: expiry_time,
          anonymize_ip: $scope.anonymize_ip,
          burn_after_reading: $scope.burn_after_reading,
          message: encryptedDocument,
        })
        .then(
          (response) => {
            step3(response.data.id, password);
          },
          (response) => {
            console.error(response.data.error);
            feedback("error flash", response.data.error);
          }
        );
    };
  },
]);

module.controller("OpenCtl", [
  "$scope",
  "$http",
  "_feedback",
  ($scope, $http, _feedback) => {
    var feedback = (status, reason) => {
      _feedback($scope, status, reason);
    };

    // var convertDate = (datestring) => {
    //   var date = new Date(datestring);
    //   var newDate = new Date(
    //     date.getTime() + date.getTimezoneOffset() * 60 * 1000
    //   );
    //   var offset = date.getTimezoneOffset() / 60;
    //   var hours = date.getHours();
    //   newDate.setHours(hours - offset);
    //   return newDate;
    // };

    var decrypt = (encrypted_content, password) => {
      feedback("info", "Decrypting...");
      $scope.decrypted = JSON.parse(sjcl.decrypt(password, encrypted_content));
      feedback("info", "Successfully decrypted the message.");
      return true;
    };

    $scope.copy = () => {
      if (document.execCommand("copy")) {
        feedback("info", "The message has been copied to your clipboard.");
      } else {
        feedback("error", "Could not copy the message to your keyboard, your browser may not support this feature.");
      }
    };

    $scope.burn = () => {
      feedback("info", "Telling server to delete the message...");
      $http.delete("/api/" + id).then(
        () => {
          feedback("info", "The message was deleted.");
          $scope.burned = true;
        },
        (data) => feedback("error", data)
      );
    };

    let id = decodeURIComponent(document.location.pathname);
    let password = decodeURIComponent(document.location.hash);
    id = id.substr(1, id.length - 1);
    password = password.substr(1, password.length - 1);
    password = sjcl.codec.base64url.toBits(password);

    feedback("info", "Fetching message from server...");
    $http.get("/api/" + id).then(
      (response) => {
        $scope.meta = response.data;
        $scope.burned = $scope.meta.burn_after_reading;
        $scope.decrypted_succesfully = decrypt($scope.meta.content, password);
      },
      () => {
        $scope.not_found = true;
        feedback("", "");
      }
    );
  },
]);
