function authenticate_with_frappe(socket, next) {
    const token = socket?.handshake?.auth?.token || null;
    const user = socket?.handshake?.auth?.user || null;

    console.log("we are passing ", socket.handshake)
    let namespace = socket.nsp.name;
    namespace = namespace.slice(1, namespace.length); // remove leading `/`
    socket.namespace
    next()
    //
    if (!token) {
        next(new Error("Unauthenticated"));
    }
    if (!user) {
        next(new Error("Unauthenticated"));
    }
    socket.user = user;
    next();
}

module.exports = authenticate_with_frappe;
