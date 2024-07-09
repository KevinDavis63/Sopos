const {Server} = require("socket.io");

const {get_conf} = require("./node_utils");
const conf = get_conf();

const {get_redis_subscriber} = require('../frappe/node_utils');

let io = new Server({
    cors: {
        // Should be fine since we are ensuring whether hostname and origin are same before adding setting listeners for s socket
        origin: true,
        credentials: false,
    },
    cleanupEmptyChildNamespaces: true,
})

const user_room = (user) => "user:" + user;

const realtime = io.of(/^\/.*$/);

// const authenticate_with_frappe = require("./middleware");
// realtime.use(authenticate_with_frappe);

function on_connection(socket) {
    socket.join("all");
    socket.join(user_room(socket.user));
}

realtime.on("connection", on_connection);
const subscriber = get_redis_subscriber();

(async () => {
    await subscriber.connect();
    subscriber.subscribe("events", (message) => {
    	console.log("we have new events ", message);
        message = JSON.parse(message);

        let namespace = "/" + message.namespace;

        if (message.room) {
            io.of(namespace).to(message.room).emit(message.event, message.message);
        } else {
            // publish to ALL sites only used for things like build event.
            realtime.emit(message.event, message.message);
        }
    });
})();

let port = conf.fsocketio_port;
io.listen(port);
console.log("Realtime service listening on: ", port);
