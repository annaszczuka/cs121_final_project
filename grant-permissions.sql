DROP USER IF EXISTS 'admin'@'localhost';
DROP USER IF EXISTS 'client'@'localhost';

-- Create Admin Users
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin_pw';
CREATE USER 'client'@'localhost' IDENTIFIED BY 'client_pw';

-- Grant Admin Privileges
GRANT ALL PRIVILEGES ON retaildb.* TO 'admin'@'localhost';

-- Grant Client (Read-Only) Privileges
GRANT SELECT ON retaildb.* TO 'client'@'localhost';
