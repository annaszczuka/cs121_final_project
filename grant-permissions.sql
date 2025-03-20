# DROP USER IF EXISTS 'admin'@'localhost';
# DROP USER IF EXISTS 'client'@'localhost';
#
# -- Create Admin Users
# CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin_pw';
# CREATE USER 'client'@'localhost' IDENTIFIED BY 'client_pw';
#
# -- Grant Admin Privileges
# GRANT ALL PRIVILEGES ON retaildb.* TO 'admin'@'localhost';
#
# -- Grant Client (Read-Only) Privileges
# GRANT SELECT ON retaildb.* TO 'client'@'localhost';

DROP USER IF EXISTS 'admin'@'localhost';
DROP USER IF EXISTS 'client'@'localhost';

-- Create Admin Users
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin_pw';
CREATE USER 'client'@'localhost' IDENTIFIED BY 'client_pw';

-- Grant Admin Privileges
GRANT ALL PRIVILEGES ON retaildb.* TO 'admin'@'localhost';

-- Grant Client Privileges (Read-Only with Account Creation)
GRANT SELECT, INSERT ON retaildb.customer TO 'client'@'localhost';
GRANT EXECUTE ON FUNCTION retaildb.get_contact_email TO 'client'@'localhost';
GRANT EXECUTE ON PROCEDURE retaildb.sp_add_user TO 'client'@'localhost';
GRANT EXECUTE ON FUNCTION retaildb.authenticate TO 'client'@'localhost';
GRANT EXECUTE ON FUNCTION retaildb.store_id_to_store_chain TO 'client'@'localhost';
GRANT EXECUTE ON FUNCTION retaildb.store_count TO 'client'@'localhost';
GRANT EXECUTE ON FUNCTION retaildb.store_score TO 'client'@'localhost';

GRANT SELECT (username, first_name, last_name, is_admin) 
ON retaildb.user_info TO 'client'@'localhost';

GRANT SELECT ON retaildb.* TO 'client'@'localhost';
