(function () {
  var KEY = "dfcal_ok";
  var PASS = "sinofate";
  if (sessionStorage.getItem(KEY) === "1") return;
  document.documentElement.style.visibility = "hidden";
  function showGate() {
    var gate = document.createElement("div");
    gate.id = "login-gate";
    gate.innerHTML =
      '<div class="login-card"><h1>东风日历</h1><p>请输入访问密码</p>' +
      '<form id="login-form"><input id="login-pass" type="password" autocomplete="current-password" placeholder="密码" autofocus>' +
      '<button type="submit">进入</button></form><p id="login-err" class="err" hidden>密码不对</p></div>';
    document.body.prepend(gate);
    document.documentElement.style.visibility = "visible";
    document.getElementById("login-form").addEventListener("submit", function (e) {
      e.preventDefault();
      var v = document.getElementById("login-pass").value || "";
      if (v === PASS) {
        sessionStorage.setItem(KEY, "1");
        gate.remove();
      } else {
        document.getElementById("login-err").hidden = false;
      }
    });
  }
  if (document.body) showGate();
  else document.addEventListener("DOMContentLoaded", showGate);
})();
