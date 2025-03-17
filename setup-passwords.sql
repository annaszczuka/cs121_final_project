-- CS 121 24wi: Password Management (Final Project modified from A6)
-- We drop previously created items if they exist
DROP FUNCTION IF EXISTS make_salt;
DROP TABLE IF EXISTS client;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS user_info;
DROP PROCEDURE IF EXISTS sp_add_user;
DROP FUNCTION IF EXISTS authenticate;
DROP PROCEDURE IF EXISTS sp_change_pw;

-- (Provided) This function generates a specified number of characters for using as a
-- salt in passwords.
DELIMITER !
CREATE FUNCTION make_salt(num_chars INT)
RETURNS VARCHAR(20) DETERMINISTIC
BEGIN
    DECLARE salt VARCHAR(20) DEFAULT '';

    -- Don't want to generate more than 20 characters of salt.
    SET num_chars = LEAST(20, num_chars);

    -- Generate the salt:  Characters used are ASCII code 32 (space)
    -- through 126 ('z').
    WHILE num_chars > 0 DO
        SET salt = CONCAT(salt, CHAR(32 + FLOOR(RAND() * 95)));
        SET num_chars = num_chars - 1;
    END WHILE;

    RETURN salt;
END !
DELIMITER ;

-- This table holds information for authenticating users based on
-- a password.  Passwords are not stored plaintext so that they
-- cannot be used by people that shouldn't have them.
-- You may extend that table to include an is_admin or role attribute if you
-- have admin or other roles for users in your application
-- (e.g. store managers, data managers, etc.)
CREATE TABLE user_info (
    -- Usernames are up to 20 characters.
    username VARCHAR(20) PRIMARY KEY,

    first_name VARCHAR(50) NOT NULL,
    last_name  VARCHAR(50) NOT NULL, 

    -- Salt will be 8 characters all the time, so we can make this 8.
    salt CHAR(8) NOT NULL,

    -- We use SHA-2 with 256-bit hashes.  MySQL returns the hash
    -- value as a hexadecimal string, which means that each byte is
    -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
    -- We can use BINARY or CHAR here; BINARY simply has a different
    -- definition for comparison/sorting than CHAR.
    password_hash BINARY(64) NOT NULL, 

    -- is_admin is 0 if not admin and 1 if it is an admin
    is_admin TINYINT NOT NULL DEFAULT 0
);

-- create the client table
CREATE TABLE client (
    -- unique identifier for each client 
    username          VARCHAR(20) PRIMARY KEY,
    -- unique contact email for the client
    contact_email     VARCHAR(255) UNIQUE NOT NULL,
    -- indicates if client is a store manager
    is_store_manager  BOOLEAN NOT NULL DEFAULT FALSE, 
    -- optional phone number for source of client contact
    phone_number      VARCHAR(20), 
    FOREIGN KEY(username) REFERENCES user_info(username)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- create the admin table
CREATE TABLE admin (
    -- unique identifier for each admin
    username         VARCHAR(20) PRIMARY KEY, 
    -- admin role in organization 
    -- options: researcher, engineer, scientist
    employee_type  ENUM('researcher', 'engineer', 'scientist') NOT NULL, 
    FOREIGN KEY(username) REFERENCES user_info(username) 
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Adds a new user to the user_info table, using the specified password (max
-- of 20 characters). Salts the password with a newly-generated salt value,
-- and then the salt and hash values are both stored in the table.
DELIMITER !
CREATE PROCEDURE sp_add_user(new_username VARCHAR(20), password VARCHAR(20),
admin_status TINYINT, first_name VARCHAR(50), last_name VARCHAR(50),
-- only applicable for clients
contact_email VARCHAR(255), 
-- only applicable for clients
is_store_manager TINYINT,
-- only applicable for clients
phone_number VARCHAR(20), 
-- only applicable for admins
employee_type ENUM('researcher', 'engineer', 'scientist')
)
BEGIN
  -- Salt will be 8 characters all the time, so we can make this 8.
  DECLARE salt CHAR(8);
  -- We use SHA-2 with 256-bit hashes.  MySQL returns the hash
  -- value as a hexadecimal string, which means that each byte is
  -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
  -- We can use BINARY or CHAR here; BINARY simply has a different
  -- definition for comparison/sorting than CHAR.
  DECLARE password_hash BINARY(64);

  -- Generate salt and password hash
  SET salt = make_salt(8);
  SET password_hash = UNHEX(SHA2(CONCAT(salt, password), 256));

  -- Ensure the username does not already exist
  IF NOT EXISTS (SELECT 1 FROM user_info WHERE username = new_username) THEN
    -- Insert user into user_info table
    INSERT INTO user_info (username, first_name, last_name, salt, password_hash, is_admin)
    VALUES (new_username, first_name, last_name, salt, password_hash, admin_status);

    -- If admin, insert into admin table
    IF admin_status = 1 THEN
      INSERT INTO admin (username, employee_type) 
      VALUES (new_username, employee_type);
    ELSE
      -- If client, insert into client table
      INSERT INTO client (username, contact_email, is_store_manager, phone_number) 
      VALUES (new_username, contact_email, is_store_manager, phone_number);
    END IF;
  END IF;
END !
DELIMITER ;

-- Authenticates the specified username and password against the data
-- in the user_info table.  Returns 1 if the user appears in the table, and the
-- specified password hashes to the value for the user. Otherwise returns 0.
DELIMITER !
CREATE FUNCTION authenticate(username VARCHAR(20), password VARCHAR(20))
RETURNS TINYINT DETERMINISTIC
BEGIN
  -- variables for storing salt and salted_password, and number of users
  -- with the same hashed password 
  DECLARE salt_entry CHAR(8); 
  DECLARE salted_password BINARY(64);
  DECLARE user_count INT;

  -- find salt of the specified user 
  SELECT salt INTO salt_entry
  FROM user_info 
  WHERE user_info.username = username; 

  -- count the number of users where a generated hash from the inputted 
  -- password is equal to the users actual hash
  SELECT UNHEX(SHA2(CONCAT(salt_entry, password), 256)) INTO salted_password;
  SELECT COUNT(*) INTO user_count 
  FROM user_info 
  WHERE user_info.password_hash = salted_password;

  -- return whether or not a matching user was found
  IF user_count = 1 THEN
    RETURN 1;
  ELSE
    RETURN 0;
  END IF;
  
END !
DELIMITER ;

-- a procedure sp_change_password to generate a new salt and change the given
-- user's password to the given password (after salting and hashing)
DELIMITER !
CREATE PROCEDURE sp_change_pw(
    username VARCHAR(20),
    new_password VARCHAR(20)
)
BEGIN 
    -- Generate variables to store salt and salted_password
    DECLARE salt CHAR(8); 
    DECLARE salted_password BINARY(64);

    -- Generate salt and hash salt
    SELECT make_salt(8) INTO salt;
    SELECT UNHEX(SHA2(CONCAT(salt, new_password), 256)) INTO salted_password;

    -- Update a user's salt and password
    UPDATE user_info
    SET password_hash = salted_password, salt = salt
    WHERE user_info.username = username;

END !
DELIMITER ;