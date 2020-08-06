let api = null;

const data = {
    gps_port: null, // '/home/dan/Documents/Cerulean-Companion/testdata/raw_gps_data.txt',
    gps_baud: null,
    rovl_port: null, // '/home/dan/Documents/Cerulean-Companion/testdata/raw_rth_data.txt',
    gcs_host: "localhost",
    gcs_port: 27000,
    rov_host: "192.168.2.2",
    rov_port: 25100,
    events: [
        // {level: 'error', message: 'some error happened', detail: 'once upon a time...'}
    ],
    serial_ports: [],
    serial_baud: [4800, 9600, 38400, 57600],
    is_connected: false,
};

window.addEventListener("error", (ev) => {
    add_to_log(
        "error",
        "javascript error: " + ev.message + " at " + ev.filename + ":" + ev.lineno
    );
});

function on_python_error(err) {
    add_to_log("error", "Python error: " + err.message, err.stack);
}

window.addEventListener("pywebviewready", (event) => {
    if (typeof pywebview === "undefined") {
        window.setTimeout(init_api, 10);
        return;
    }

    api = pywebview.api;
    api
        .get_serial_devices()
        .then((devices) => {
            data.serial_ports = devices;
        })
        .catch(on_python_error);

    window.setInterval(() => {
        api
            .get_serial_devices()
            .then((devices) => {
                data.serial_ports = devices;
            })
            .catch(on_python_error);
    }, 5000);
});

window.addEventListener("load", (event) => {
    new Vue({
        el: "#main",
        data: data,
        methods: {
            connect: function (ev) {
                let args = {
                    rovl_port: data.rovl_port,
                    gps_port: data.gps_port,
                    gps_baud: data.gps_baud,
                    gcs_host: data.gcs_host,
                    gcs_port: data.gcs_port || 27000,
                    rov_host: data.rov_host,
                    rov_port: data.rov_port || 25100,
                };
                api
                    .connect(args)
                    .then(() => {
                        data.is_connected = true;
                    })
                    .catch(on_python_error);
            },
            disconnect: function (ev) {
                api
                    .disconnect()
                    .then(() => {
                        data.is_connected = false;
                    })
                    .catch(on_python_error);
            },
            sync_location: function (ev) {
                api.sync_location().catch(on_python_error);
            },
            scroll_to_me: function (ev) {
                ev.source.scrollIntoViewIfNeeded();
            },
        },
    });
});

function log_json(record) {
    console.log("app log", record);
    add_to_log(record.levelname, "[" + record.name + "] " + record.msg);
}

function add_to_log(level, message, detail) {
    data.events.push({level: level, message: message, detail: detail});
}
