-- 迁移脚本：删除 users 表中的 nickname 和 status 字段
-- 执行日期: 2024-12-08
-- 说明: 移除冗余字段，nickname 功能由 username 替代，status 功能由 is_active 替代

-- 删除 nickname 字段
ALTER TABLE users DROP COLUMN nickname;

-- 删除 status 字段
ALTER TABLE users DROP COLUMN status;

