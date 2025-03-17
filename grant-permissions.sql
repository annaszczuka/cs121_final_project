DROP USER IF EXISTS 'sreeyur_admin'@'localhost';
DROP USER IF EXISTS 'aszszcuka_admin'@'localhost';
DROP USER IF EXISTS 'ewang_admin'@'localhost';
DROP USER IF EXISTS 'store_manager'@'localhost';

-- Create Admin Users
CREATE USER 'sreeyur_admin'@'localhost' IDENTIFIED BY 'admin1';
CREATE USER 'aszszcuka_admin'@'localhost' IDENTIFIED BY 'admin2';
CREATE USER 'ewang_admin'@'localhost' IDENTIFIED BY 'admin3';

-- Create Client User
CREATE USER 'store_manager'@'localhost' IDENTIFIED BY 'client_manager';

-- Grant Admin Privileges
GRANT ALL PRIVILEGES ON retail_db.* TO 'sreeyur_admin'@'localhost';
GRANT ALL PRIVILEGES ON retail_db.* TO 'aszszcuka_admin'@'localhost';
GRANT ALL PRIVILEGES ON retail_db.* TO 'ewang_admin'@'localhost';

-- Grant Client (Read-Only) Privileges
GRANT SELECT ON retail_db.* TO 'store_manager'@'localhost';

-- Apply Changes
FLUSH PRIVILEGES;
