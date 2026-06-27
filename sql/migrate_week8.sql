-- ============================================
-- 第八周迁移：user_statistics 改为用户级
-- ============================================

USE exam_point;

-- 1. 聚合旧数据到临时表
CREATE TABLE IF NOT EXISTS user_stats_temp AS
SELECT
    user_id,
    SUM(total_count) AS total_count,
    SUM(total_correct) AS total_correct,
    MAX(continue_days) AS continue_days,
    MAX(last_study_date) AS last_study_date
FROM user_statistics
GROUP BY user_id;

-- 2. 删除旧表
DROP TABLE IF EXISTS user_statistics;

-- 3. 创建新表（用户级）
CREATE TABLE IF NOT EXISTS user_statistics (
    `user_id`        BIGINT NOT NULL COMMENT '用户ID',
    `total_count`    INT    DEFAULT 0 COMMENT '累计做题数',
    `total_correct`  INT    DEFAULT 0 COMMENT '累计正确数',
    `continue_days`  INT    DEFAULT 0 COMMENT '连续学习天数',
    `last_study_date` DATE  DEFAULT NULL COMMENT '最后学习日期',
    PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户统计表';

-- 4. 插入聚合数据
INSERT INTO user_statistics (user_id, total_count, total_correct, continue_days, last_study_date)
SELECT * FROM user_stats_temp;

-- 5. 清理临时表
DROP TABLE IF EXISTS user_stats_temp;
