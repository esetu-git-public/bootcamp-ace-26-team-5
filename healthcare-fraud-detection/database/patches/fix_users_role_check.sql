-- SQL Patch to fix the role check constraint in Supabase
-- Run this in your Supabase SQL Editor to allow customer registrations.

ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('customer', 'employee', 'admin'));
