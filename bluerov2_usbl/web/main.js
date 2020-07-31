const data = {
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
  ],
  is_connected: false,
}

window.addEventListener("error", (ev) => {
  add_to_log(
    "error",
    "javascript error: " + ev.message + " at " + ev.filename + ":" + ev.lineno
  );
});

function on_python_error(err) {
  add_to_log("error", "Python error: " + err.message , err.stack);
}

let api = null;

function init_api() {
  if (typeof pywebview === "undefined") {
    window.setTimeout(init_api, 10);
    return;
  }

  api = pywebview.api;
  api.get_serial_devices().then((devices)=>{data.serial_ports=devices}).catch(on_python_error);

  window.setInterval(() => {
    api.get_serial_devices().then((devices)=>{data.serial_ports=devices}).catch(on_python_error);
  }, 5000);

}

window.addEventListener("load", (event) => {
  init_api();

  new Vue({
    el: '#main',
    data: data,
    methods: {
      connect: function(ev){
        let args = {
          rovl_port: data.rovl_port,
          gps_port: data.gps_port,
          gps_baud: data.gps_baud,
          addr_gcs: data.gcs_host + ':' + data.gcs_port || 27000,
          addr_rov: data.rov_host + ':' + data.rov_port || 25100,
        }

        api.connect(args).then(()=>{data.is_connected=true}).catch(on_python_error)
      },
      disconnect: function(ev){
        api.disconnect().catch(on_python_error)
      },
      sync_location: function(ev){
        api.sync_location().catch(on_python_error)
      },
    }
  })
});

function log_json(record) {
  console.log("app log", record);
  add_to_log(record.levelname, "[" + record.name + "] " + record.msg);
}

function add_to_log(level, message, detail) {
  data.events.push(
      {level:level, message:message, detail:detail}
    )
}
