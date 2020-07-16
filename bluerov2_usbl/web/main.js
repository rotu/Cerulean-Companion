// Elements by id
els = {};
window.addEventListener("error", (ev) => {
  add_to_log(
    "error",
    "javascript error: " + ev.message + " at " + ev.filename + ":" + ev.lineno
  );
});

function on_python_error(ev) {
  add_to_log("error", "Python error: " + ev.message + " \r\n\r\n " + ev.stack);
}

let api = null;

function init_api() {
  if (typeof pywebview === "undefined") {
    window.setTimeout(init_api, 10);
    return;
  }
  api = pywebview.api;
  debugger;
  api.get_serial_devices().then(on_list_usb_devices).catch(on_python_error);

  window.setInterval(() => {
    api.get_serial_devices().then(on_list_usb_devices);
  }, 5000);

  on_gps_change();
  els.gps_ok.addEventListener("change", on_gps_change);
  els.sel_dev_gps.addEventListener("change", on_gps_change);

  on_usbl_change();
  els.usbl_ok.addEventListener("change", on_usbl_change);
  els.sel_dev_usbl.addEventListener("change", on_usbl_change);

  on_mav_change();
  els.mav_ok.addEventListener("change", on_mav_change);
  els.input_mav.addEventListener("change", on_mav_change);

  on_echo_change();
  els.echo_ok.addEventListener("change", on_echo_change);
  els.input_echo.addEventListener("change", on_echo_change);
}

window.addEventListener("load", (event) => {
  for (let e of document.querySelectorAll("[id]")) {
    els[e.id] = e;
  }
  init_api();
});

function on_controller_attr_changed(key, value) {
  add_to_log("info", key + " is now " + value);
  //
  switch (key) {
    case "dev_usbl":
      if (value) {
        els.sel_dev_usbl.value = value;
      }
      els.usbl_ok.checked = !!value;
      break;
    case "dev_gps":
      if (value) {
        els.sel_dev_gps.value = value;
      }
      els.gps_ok.checked = !!value;
      break;
    case "addr_mav":
      if (value) {
        els.input_mav.value = value;
      }
      els.mav_ok.checked = !!value;
      break;
    case "addr_echo":
      if (value) {
        els.input_echo.value = value;
      }
      els.echo_ok.checked = !!value;
  }
}

function on_gps_change() {
  els.gps_ok.disabled = !els.sel_dev_gps.value;
  let dev = null;
  if (els.gps_ok.checked) {
    dev = els.sel_dev_gps.value || null;
  }
  api.controller_set_attr({ dev_gps: dev });
}

function on_usbl_change() {
  els.usbl_ok.disabled = !els.sel_dev_usbl.value;

  let dev = null;
  if (els.usbl_ok.checked) {
    dev = els.sel_dev_usbl.value || null;
  }
  add_to_log("info", "setting usbl to " + dev);
  window.pr = api.controller_set_attr({ dev_usbl: dev });
}

function on_echo_change() {
  els.echo_ok.disabled = !els.input_echo.value;

  let addr = null;
  if (els.echo_ok.checked) {
    addr = els.input_echo.value || null;
  }
  api.controller_set_attr({ addr_echo: addr });
}

function on_mav_change() {
  els.mav_ok.disabled = !els.input_mav.value;

  let addr = null;
  if (els.mav_ok.checked) {
    addr = els.input_mav.value || null;
  }
  api.controller_set_attr({ addr_mav: addr });
}

function log_json(record) {
  console.log("app log", record);
  add_to_log(record.levelname, "[" + record.name + "] " + record.msg);
}

function add_to_log(level, msg) {
  const event_log = document.getElementById("event_log");
  const isScrolledToBottom =
    event_log.scrollHeight - event_log.clientHeight <= event_log.scrollTop + 1;

  let li = document.createElement("li");
  li.className = level;
  li.innerText = msg;
  document.getElementById("event_log").append(li);

  if (isScrolledToBottom) {
    event_log.scrollTop = event_log.scrollHeight;
  }
}

function on_list_usb_devices(devices) {
  const datalist = document.getElementById("serial_ports");
  datalist.innerHTML = "";

  for (let device of devices) {
    let opt = document.createElement("option");
    opt.value = device;
    datalist.appendChild(opt);
  }
}
