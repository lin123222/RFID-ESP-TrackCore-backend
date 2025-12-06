-- 数据库迁移脚本：更新包裹记录表结构
-- 版本：001
-- 描述：将单一温度字段扩展为最高温度、平均湿度、超阈值时间

-- 1. 备份现有数据
CREATE TABLE package_records_backup AS 
SELECT * FROM package_records;

-- 2. 添加新字段
ALTER TABLE package_records 
ADD COLUMN max_temperature REAL;

ALTER TABLE package_records 
ADD COLUMN avg_humidity REAL;

ALTER TABLE package_records 
ADD COLUMN over_threshold_time INTEGER;

-- 3. 迁移现有数据（将原temperature字段复制到max_temperature）
UPDATE package_records 
SET max_temperature = temperature,
    avg_humidity = 50.0,  -- 默认湿度值
    over_threshold_time = 0  -- 默认超阈值时间
WHERE max_temperature IS NULL;

-- 4. 设置新字段为非空
ALTER TABLE package_records 
ALTER COLUMN max_temperature SET NOT NULL;

ALTER TABLE package_records 
ALTER COLUMN avg_humidity SET NOT NULL;

ALTER TABLE package_records 
ALTER COLUMN over_threshold_time SET NOT NULL;

-- 5. 删除旧的temperature字段（可选，建议先测试）
-- ALTER TABLE package_records DROP COLUMN temperature;

-- 6. 更新表注释
COMMENT ON TABLE package_records IS '包裹环境监测记录表';
COMMENT ON COLUMN package_records.max_temperature IS '最高温度(°C)';
COMMENT ON COLUMN package_records.avg_humidity IS '平均湿度(%)';
COMMENT ON COLUMN package_records.over_threshold_time IS '超阈值时间(秒)';

-- 7. 验证迁移结果
SELECT 
    COUNT(*) as total_records,
    COUNT(max_temperature) as max_temp_count,
    COUNT(avg_humidity) as humidity_count,
    COUNT(over_threshold_time) as over_time_count
FROM package_records;
