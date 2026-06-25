-- ============================================
-- 考点通（ExamPoint AI）数据库初始化脚本
-- ============================================

CREATE DATABASE IF NOT EXISTS exam_point DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE exam_point;

-- 1. 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id`          BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    `phone`       VARCHAR(20)  NOT NULL COMMENT '手机号',
    `nickname`    VARCHAR(50)  DEFAULT '' COMMENT '昵称',
    `avatar`      VARCHAR(255) DEFAULT '' COMMENT '头像地址',
    `school_id`   BIGINT       DEFAULT NULL COMMENT '学校ID',
    `major_id`    BIGINT       DEFAULT NULL COMMENT '专业ID',
    `create_time` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY `uk_phone` (`phone`)
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
    `id`   BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '科目ID',
    `name` VARCHAR(50)  NOT NULL COMMENT '科目名称',
    `icon` VARCHAR(255) DEFAULT '' COMMENT '图标地址',
    `sort` INT          DEFAULT 0 COMMENT '排序'
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
    `answer`      TEXT         DEFAULT '' COMMENT '标准答案',
    `analysis`    TEXT         DEFAULT '' COMMENT '答案解析',
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
    `content`     TEXT        NOT NULL COMMENT '选项内容',
    `is_answer`   TINYINT     DEFAULT 0 COMMENT '是否正确答案：0否 1是',
    INDEX `idx_question_id` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选项表';

-- 9. 做题记录表（每题只保留最新一条记录）
CREATE TABLE IF NOT EXISTS `user_answer_record` (
    `id`          BIGINT      PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    `user_id`     BIGINT      NOT NULL COMMENT '用户ID',
    `question_id` BIGINT      NOT NULL COMMENT '题目ID',
    `user_answer` TEXT        DEFAULT '' COMMENT '用户答案',
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
    `error_msg`     TEXT         DEFAULT '' COMMENT '错误信息',
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

-- 12. 每日排行榜持久化表（实时排行用 Redis ZSet）
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


-- ============================================
-- 初始数据
-- ============================================

-- 科目
INSERT IGNORE INTO `subject` (`name`, `sort`) VALUES
('高等数学', 1),
('线性代数', 2),
('大学英语', 3),
('大学物理', 4),
('操作系统', 5),
('计算机网络', 6),
('数据结构', 7),
('数据库原理', 8);

-- 示例学校
INSERT IGNORE INTO `school` (`name`, `province`, `city`) VALUES
('示例大学', '北京', '北京');

-- 示例专业
INSERT IGNORE INTO `major` (`school_id`, `name`) VALUES
(1, '计算机科学与技术'),
(1, '软件工程'),
(1, '人工智能'),
(1, '信息安全');

-- 示例题库（公共）
INSERT IGNORE INTO `question_bank` (`subject_id`, `creator_id`, `name`, `visibility`, `question_count`) VALUES
(5, 0, '操作系统基础知识', 2, 5);

-- 示例题目
INSERT IGNORE INTO `question` (`bank_id`, `type`, `content`, `answer`, `analysis`, `difficulty`) VALUES
(1, 'single_choice', '在操作系统中，进程和线程的主要区别是：', 'A', '进程是操作系统资源分配的基本单位，而线程是CPU调度的基本单位。一个进程可以包含多个线程，线程共享进程的资源。', 1),
(1, 'single_choice', '以下哪种页面置换算法会产生Belady异常？', 'B', 'FIFO页面置换算法在某些情况下会出现分配的物理页框数增加但缺页率反而升高的现象，这称为Belady异常。LRU和OPT不会出现此现象。', 2),
(1, 'judge', '虚拟内存技术使得程序的执行速度比物理内存快。', 'F', '虚拟内存通过将部分程序放在外存来扩大可用内存空间，但由于需要页面置换，实际执行速度通常比纯物理内存慢。', 1),
(1, 'multiple_choice', '以下哪些是进程的状态？', 'ABC', '进程的基本状态包括：就绪、运行、阻塞（等待）。新建和终止是进程生命周期的状态，但不属于基本的三态模型。', 1),
(1, 'single_choice', '在分页存储管理中，页表的作用是：', 'A', '页表用于实现从逻辑页号到物理块号的地址映射，是分页存储管理的核心数据结构。', 1);

-- 示例选项
INSERT IGNORE INTO `question_option` (`question_id`, `option_key`, `content`, `is_answer`) VALUES
-- 题目1
(1, 'A', '进程是资源分配的基本单位', 1),
(1, 'B', '线程是资源分配的基本单位', 0),
(1, 'C', '进程和线程没有区别', 0),
(1, 'D', '线程不能独立执行', 0),
-- 题目2
(2, 'A', 'LRU算法', 0),
(2, 'B', 'FIFO算法', 1),
(2, 'C', 'OPT算法', 0),
(2, 'D', '时钟算法', 0),
-- 题目4
(4, 'A', '就绪', 1),
(4, 'B', '运行', 1),
(4, 'C', '阻塞', 1),
(4, 'D', '销毁', 0),
-- 题目5
(5, 'A', '实现逻辑页号到物理块号的映射', 1),
(5, 'B', '记录程序执行的指令', 0),
(5, 'C', '管理磁盘空间', 0),
(5, 'D', '实现进程调度', 0);
