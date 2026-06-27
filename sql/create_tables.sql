-- ============================================
-- 考点通 建表脚本
-- ============================================

CREATE DATABASE IF NOT EXISTS exam_point DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE exam_point;

-- 1. 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id`          BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    `phone`       VARCHAR(20)  DEFAULT NULL COMMENT '手机号',
    `openid`      VARCHAR(100) DEFAULT NULL COMMENT '微信openid',
    `nickname`    VARCHAR(50)  DEFAULT '' COMMENT '昵称',
    `avatar`      VARCHAR(255) DEFAULT '' COMMENT '头像地址',
    `school_name` VARCHAR(100) DEFAULT NULL COMMENT '学校名称',
    `major_name`  VARCHAR(100) DEFAULT NULL COMMENT '专业名称',
    `create_time` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY `uk_phone` (`phone`),
    UNIQUE KEY `uk_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 学校表
CREATE TABLE IF NOT EXISTS `school` (
    `id`       BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '学校ID',
    `name`     VARCHAR(100) NOT NULL COMMENT '学校名称',
    `province` VARCHAR(50)  DEFAULT '' COMMENT '省份',
    `city`     VARCHAR(50)  DEFAULT '' COMMENT '城市',
    UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学校表';

-- 3. 专业表
CREATE TABLE IF NOT EXISTS `major` (
    `id`        BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '专业ID',
    `school_id` BIGINT       NOT NULL COMMENT '学校ID',
    `name`      VARCHAR(100) NOT NULL COMMENT '专业名称',
    INDEX `idx_school_id` (`school_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业表';

-- 4. 科目表
CREATE TABLE IF NOT EXISTS `subject` (
    `id`     BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '科目ID',
    `name`   VARCHAR(50)  NOT NULL COMMENT '科目名称',
    `icon`   VARCHAR(255) DEFAULT '' COMMENT '图标地址',
    `sort`   INT          DEFAULT 0 COMMENT '排序',
    `source` TINYINT      DEFAULT 0 COMMENT '来源：0管理员添加 1用户添加'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='科目表';

-- 5. 用户科目关联表
CREATE TABLE IF NOT EXISTS `user_subject` (
    `user_id`    BIGINT NOT NULL COMMENT '用户ID',
    `subject_id` BIGINT NOT NULL COMMENT '科目ID',
    PRIMARY KEY (`user_id`, `subject_id`),
    INDEX `idx_subject_id` (`subject_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户科目关联表';

-- 6. 题库表
CREATE TABLE IF NOT EXISTS `question_bank` (
    `id`             BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '题库ID',
    `subject_id`     BIGINT       NOT NULL COMMENT '所属科目ID',
    `creator_id`     BIGINT       NOT NULL COMMENT '创建用户ID',
    `name`           VARCHAR(100) NOT NULL COMMENT '题库名称',
    `visibility`     TINYINT      DEFAULT 0 COMMENT '可见范围：0私有 1学校共享 2公共题库',
    `question_count` INT          DEFAULT 0 COMMENT '题目数量',
    `source_file`    VARCHAR(255) DEFAULT '' COMMENT '原始文件地址',
    `create_time`    DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_subject_id` (`subject_id`),
    INDEX `idx_creator_id` (`creator_id`),
    INDEX `idx_visibility` (`visibility`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题库表';

-- 7. 题目表
CREATE TABLE IF NOT EXISTS `question` (
    `id`          BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '题目ID',
    `bank_id`     BIGINT       NOT NULL COMMENT '题库ID',
    `type`        VARCHAR(30)  NOT NULL COMMENT '题目类型：single_choice/multiple_choice/judge/fill_blank/short_answer',
    `content`     TEXT         NOT NULL COMMENT '题目内容',
    `answer`      TEXT         COMMENT '标准答案',
    `analysis`    TEXT         COMMENT '答案解析',
    `difficulty`  TINYINT      DEFAULT 1 COMMENT '难度等级：1简单 2中等 3困难',
    `create_time` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_bank_id` (`bank_id`),
    INDEX `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目表';

-- 8. 选项表
CREATE TABLE IF NOT EXISTS `question_option` (
    `id`          BIGINT      PRIMARY KEY AUTO_INCREMENT COMMENT '选项ID',
    `question_id` BIGINT      NOT NULL COMMENT '题目ID',
    `option_key`  VARCHAR(5)  NOT NULL COMMENT '选项标识：A/B/C/D/E/F',
    `content`     TEXT         NOT NULL COMMENT '选项内容',
    `is_answer`   TINYINT     DEFAULT 0 COMMENT '是否正确答案：0否 1是',
    INDEX `idx_question_id` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选项表';

-- 9. 做题记录表
CREATE TABLE IF NOT EXISTS `user_answer_record` (
    `id`          BIGINT      PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    `user_id`     BIGINT      NOT NULL COMMENT '用户ID',
    `question_id` BIGINT      NOT NULL COMMENT '题目ID',
    `user_answer` TEXT         COMMENT '用户答案',
    `is_correct`  TINYINT     DEFAULT 0 COMMENT '是否正确：0错误 1正确',
    `cost_time`   INT         DEFAULT 0 COMMENT '耗时秒数',
    `create_time` DATETIME    DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_question_id` (`question_id`),
    UNIQUE INDEX `uk_user_question` (`user_id`, `question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='做题记录表';

-- 10. 上传任务表
CREATE TABLE IF NOT EXISTS `upload_task` (
    `id`            BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '任务ID',
    `user_id`       BIGINT       NOT NULL COMMENT '上传用户',
    `subject_id`    BIGINT       NOT NULL COMMENT '所属科目',
    `file_url`      VARCHAR(255) NOT NULL COMMENT '文件地址',
    `bank_id`       BIGINT       DEFAULT NULL COMMENT '生成的题库ID',
    `status`        TINYINT      DEFAULT 0 COMMENT '任务状态：0等待 1解析中 2成功 3失败',
    `success_count` INT          DEFAULT 0 COMMENT '成功解析题数',
    `fail_count`    INT          DEFAULT 0 COMMENT '失败题数',
    `error_msg`     TEXT         COMMENT '错误信息',
    `create_time`   DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上传任务表';

-- 11. 用户统计表
CREATE TABLE IF NOT EXISTS `user_statistics` (
    `user_id`        BIGINT NOT NULL COMMENT '用户ID',
    `subject_id`     BIGINT NOT NULL COMMENT '科目ID',
    `today_count`    INT    DEFAULT 0 COMMENT '今日做题数',
    `today_correct`  INT    DEFAULT 0 COMMENT '今日正确数',
    `week_count`     INT    DEFAULT 0 COMMENT '本周做题数',
    `total_count`    INT    DEFAULT 0 COMMENT '累计做题数',
    `total_correct`  INT    DEFAULT 0 COMMENT '累计正确数',
    `continue_days`  INT    DEFAULT 0 COMMENT '连续学习天数',
    `last_study_date` DATE  DEFAULT NULL COMMENT '最后学习日期',
    PRIMARY KEY (`user_id`, `subject_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户统计表';

-- 12. 每日排行榜持久化表
CREATE TABLE IF NOT EXISTS `daily_ranking` (
    `id`            BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    `user_id`       BIGINT NOT NULL COMMENT '用户ID',
    `subject_id`    BIGINT NOT NULL COMMENT '科目ID',
    `study_date`    DATE   NOT NULL COMMENT '学习日期',
    `daily_count`   INT    DEFAULT 0 COMMENT '当日刷题数',
    `daily_correct` INT    DEFAULT 0 COMMENT '当日正确数',
    UNIQUE KEY `uk_user_subject_date` (`user_id`, `subject_id`, `study_date`),
    INDEX `idx_subject_date_count` (`subject_id`, `study_date`, `daily_count` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日排行榜持久化表';
