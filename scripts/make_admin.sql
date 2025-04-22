-- This script promotes a user to admin status based on their email address
-- Replace 'user@example.com' with the email of the user you want to make an admin

UPDATE users 
SET role = 1 
WHERE email = 'user@example.com';

-- To verify the change, run:
-- SELECT id, username, email, role FROM users WHERE email = 'user@example.com';
-- A role value of 1 indicates admin status