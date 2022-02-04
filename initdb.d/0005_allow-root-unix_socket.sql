-- allow programs running as root access w/o password
ALTER USER 'root'@'localhost' IDENTIFIED VIA unix_socket;

