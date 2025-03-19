-- call procedure to add a user
CALL sp_add_user('admin_username_engineer_john', 'securepass', 1, 'John', 
'Doe', NULL, NULL, NULL, 'engineer');
CALL sp_add_user('jsmith', 'clientpass', 0, 'Jane', 'Smith', 
'jane@example.com', 1, '123-456-7890', NULL);
CALL sp_add_user('cbrown', 'snoopy', 0, 'Charlie', 'Brown', 
'cbrown@gmail.com', 0, '111-222-3333', NULL);
CALL sp_add_user('jwoodwell', 'securepass_woodwell', 1, 'James', 
'Woodwell', NULL, NULL, NULL, 'engineer');

-- test authenticate function 
-- Should return 0 (false)
SELECT authenticate('chaka', 'hello'); 
-- Should return 0 (false)
SELECT authenticate('alex', 'goodbye');
-- Should return 1 (true)
SELECT authenticate('admin_username_engineer_john', 'securepass');
-- Should return 0 (false)
SELECT authenticate('alex', 'HELLO'); 
-- Should return 1 (true)
SELECT authenticate('jsmith', 'clientpass');
-- Should return 0 (false) (because it is the wrong password)
SELECT authenticate('jsmith', 'clientpasswrong');
-- Should return 1 (true) 
SELECT authenticate('cbrown', 'snoopy');

-- test changing password ability
CALL sp_change_pw('cbrown', 'snoopydoopy'); 
CALL sp_change_pw('jwoodwell', '1234567'); 

-- Should return 0 (false)
SELECT authenticate('cbrown', 'snoopy'); 
-- Should return 1 (true)
SELECT authenticate('cbrown', 'snoopydoopy');

-- Should return 0 (false)
SELECT authenticate('jwoodwell', 'securepass_woodwell'); 
-- Should return 1 (true)
SELECT authenticate('jwoodwell', '1234567');
