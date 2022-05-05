-- allow programs running as root access w/o password
SELECT Password INTO @oldpw FROM mysql.user WHERE Host = 'localhost' and User = 'root';
SET @updateroot = CONCAT('ALTER USER \'root\'@\'localhost\' IDENTIFIED VIA mysql_native_password USING \'', @oldpw, '\' or unix_socket');
PREPARE stmt from @updateroot;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

