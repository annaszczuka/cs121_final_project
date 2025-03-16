-- CS 121 24wi: Password Management (A6 and Final Project)
-- We drop previously created items if they exist
DROP FUNCTION IF EXISTS make_salt;
DROP TABLE IF EXISTS user_info;
DROP PROCEDURE IF EXISTS sp_add_user;
DROP FUNCTION IF EXISTS authenticate;
DROP PROCEDURE IF EXISTS sp_change_password;

-- (Provided) This function generates a specified number of characters for using as a
-- salt in passwords.
DELIMITER !
CREATE FUNCTION make_salt(num_chars INT)
RETURNS VARCHAR(20) DETERMINISTIC
BEGIN
    DECLARE salt VARCHAR(20) DEFAULT '';

    -- Don't want to generate more than 20 characters of salt.
    SET num_chars = LEAST(20, num_chars);

    -- Generate the salt!  Characters used are ASCII code 32 (space)
    -- through 126 ('z').
    WHILE num_chars > 0 DO
        SET salt = CONCAT(salt, CHAR(32 + FLOOR(RAND() * 95)));
        SET num_chars = num_chars - 1;
    END WHILE;

    RETURN salt;
END !
DELIMITER ;

-- Provided (you may modify in your FP if you choose)
-- This table holds information for authenticating users based on
-- a password.  Passwords are not stored plaintext so that they
-- cannot be used by people that shouldn't have them.
-- You may extend that table to include an is_admin or role attribute if you
-- have admin or other roles for users in your application
-- (e.g. store managers, data managers, etc.)
CREATE TABLE user_info (
    -- Usernames are up to 20 characters.
    username VARCHAR(20) PRIMARY KEY,

    -- Salt will be 8 characters all the time, so we can make this 8.
    salt CHAR(8) NOT NULL,

    -- We use SHA-2 with 256-bit hashes.  MySQL returns the hash
    -- value as a hexadecimal string, which means that each byte is
    -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
    -- We can use BINARY or CHAR here; BINARY simply has a different
    -- definition for comparison/sorting than CHAR.
    password_hash BINARY(64) NOT NULL, 

    -- is_admin is 0 if not admin and 1 if it is an admin
    is_admin TINYINT(1) NOT NULL DEFAULT 0
);

-- Adds a new user to the user_info table, using the specified password (max
-- of 20 characters). Salts the password with a newly-generated salt value,
-- and then the salt and hash values are both stored in the table.
DELIMITER !
CREATE PROCEDURE sp_add_user(new_username VARCHAR(20), password VARCHAR(20), admin_status TINYINT(1))
BEGIN
  -- Salt will be 8 characters all the time, so we can make this 8.
  DECLARE salt CHAR(8);
  -- We use SHA-2 with 256-bit hashes.  MySQL returns the hash
  -- value as a hexadecimal string, which means that each byte is
  -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
  -- We can use BINARY or CHAR here; BINARY simply has a different
  -- definition for comparison/sorting than CHAR.
  DECLARE password_hash BINARY(64);
  -- We call our make salt function
  SET salt = make_salt(8);
  -- Our hashed password is a hashing applied to the combination of our 
  -- previously generated salt and our password
  SET password_hash = UNHEX(SHA2(CONCAT(salt, password), 256));
  -- check if username already exists, if not, then insert into user info
  -- table
  IF NOT EXISTS (SELECT 1 FROM user_info WHERE username = new_username) THEN
    INSERT INTO user_info (username, salt, password_hash, is_admin) 
    VALUES(new_username, salt, password_hash, admin_status);
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
  -- We use SHA-2 with 256-bit hashes.  MySQL returns the hash
  -- value as a hexadecimal string, which means that each byte is
  -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
  -- We can use BINARY or CHAR here; BINARY simply has a different
  -- definition for comparison/sorting than CHAR.
  DECLARE true_password BINARY(64);
  DECLARE our_password BINARY(64);
  -- Salt will be 8 characters all the time, so we can make this 8.
  DECLARE true_salt CHAR(8);

  -- true salt and true password represent the user's accurate salt and 
  -- hashed password
  SELECT salt, password_hash INTO true_salt, true_password
  FROM user_info
  WHERE user_info.username = username;

  -- if there is no true password, then the user must not exist in the 
  -- user info table, and we return 0
  IF true_password = NULL THEN 
    return 0;
  END IF;

  SET our_password = UNHEX(SHA2(CONCAT(true_salt, password), 256));
  IF (true_password = our_password) THEN 
    IF admin_status = 1 THEN 
    -- 2 indicates is admin user
      return 2;
    ELSE 
      return 1;
    END IF;
  ELSE 
    return 0;
  END IF;
END !
DELIMITER ;


CALL sp_add_user("admin_user", "adminpass", 1);  -- Admin
CALL sp_add_user("normal_user", "userpass", 0);  -- Regular user


-- Create a procedure sp_change_password to generate a new salt and change the given
-- user's password to the given password (after salting and hashing)
DELIMITER !
CREATE PROCEDURE sp_change_password(requestor VARCHAR(20), username VARCHAR(20), new_password VARCHAR(20))
BEGIN
  DECLARE admin_status TINYINT(1);
  DECLARE new_salt CHAR(8);
  DECLARE new_password_hash BINARY(64);

  SELECT is_admin INTO admin_status FROM user_info 
  WHERE user_info.username = requestor;

  IF admin_status = 1 OR requestor = username THEN 
    SET new_salt = make_salt(8);
    SET new_password_hash = UNHEX(SHA2(CONCAT(new_salt, password), 256));
    UPDATE user_info SET salt = new_salt, password_hash = new_password_hash 
    WHERE user_info.username = username;
  END IF;

END !
DELIMITER ;
