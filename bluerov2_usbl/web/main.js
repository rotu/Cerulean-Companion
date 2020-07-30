let data = {
  gps_port: '',
  gps_baud: 9600,
  rovl_port: '',
  gcs_host: 'localhost',
  gcs_port: '',
  rov_host: '192.168.2.2',
  rov_port: 25100,
  events: [],
  serial_ports: [],
  serial_baud: [
      4800,
      9600,
      38400,
      57600,
  ]
}

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
  api.get_serial_devices().then((devices)=>{
    console.log(devices);    data.serial_ports=devices}).catch(on_python_error);

  window.setInterval(() => {
    api.get_serial_devices().then(on_list_usb_devices);
  }, 5000);
}

window.addEventListener("load", (event) => {
  for (let e of document.querySelectorAll("[id]")) {
    els[e.id] = e;
  }
  init_api();

  new Vue({
    el: '#main',
    data: data,
  })
});

function log_json(record) {
  console.log("app log", record);
  add_to_log(record.levelname, "[" + record.name + "] " + record.msg);
}

function add_to_log(level, message) {
  data.events.push(
      {level:level,  message:message}
    )
}

function on_list_usb_devices(devices) {
  data.serial_ports = devices
}
