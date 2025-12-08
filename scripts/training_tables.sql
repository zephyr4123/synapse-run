-- ============================================
-- 中长跑训练数据表结构
-- 用于存储用户历史训练记录,供AI Agent分析挖掘
-- ============================================

-- ----------------------------
-- 训练记录主表
-- ----------------------------
DROP TABLE IF EXISTS `training_records`;
CREATE TABLE `training_records` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
    `user_id` VARCHAR(64) DEFAULT 'default_user' COMMENT '用户ID (预留字段,支持多用户)',

    -- 基础训练信息
    `exercise_type` VARCHAR(32) NOT NULL COMMENT '运动类型 (跑步/骑行/游泳等)',
    `duration_seconds` INT NOT NULL COMMENT '运动时长(秒)',
    `start_time` DATETIME NOT NULL COMMENT '开始时间',
    `end_time` DATETIME NOT NULL COMMENT '结束时间',

    -- 运动指标
    `calories` INT DEFAULT NULL COMMENT '消耗卡路里',
    `distance_meters` DECIMAL(10, 2) DEFAULT NULL COMMENT '运动距离(米)',
    `avg_heart_rate` INT DEFAULT NULL COMMENT '平均心率',
    `max_heart_rate` INT DEFAULT NULL COMMENT '最大心率',

    -- 详细数据 (JSON格式存储)
    `heart_rate_data` LONGTEXT DEFAULT NULL COMMENT '心率记录数组 (JSON格式: ["108","109",...])',

    -- 元数据
    `add_ts` BIGINT NOT NULL COMMENT '记录添加时间戳',
    `last_modify_ts` BIGINT NOT NULL COMMENT '记录最后修改时间戳',
    `data_source` VARCHAR(64) DEFAULT 'manual_import' COMMENT '数据来源 (manual_import/wearable_device/app等)',

    PRIMARY KEY (`id`),
    KEY `idx_training_user_id` (`user_id`),
    KEY `idx_training_start_time` (`start_time`),
    KEY `idx_training_exercise_type` (`exercise_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='训练记录表';

-- ----------------------------
-- 训练统计视图 (便于快速查询分析)
-- ----------------------------
CREATE OR REPLACE VIEW `training_stats` AS
SELECT
    `user_id`,
    `exercise_type`,
    COUNT(*) as total_sessions,
    SUM(`duration_seconds`) as total_duration,
    AVG(`duration_seconds`) as avg_duration,
    SUM(`distance_meters`) as total_distance,
    AVG(`distance_meters`) as avg_distance,
    AVG(`avg_heart_rate`) as overall_avg_heart_rate,
    MAX(`max_heart_rate`) as peak_heart_rate,
    DATE_FORMAT(`start_time`, '%Y-%m') as month
FROM `training_records`
GROUP BY `user_id`, `exercise_type`, DATE_FORMAT(`start_time`, '%Y-%m');

-- ----------------------------
-- 索引优化说明
-- ----------------------------
-- 1. user_id: 支持多用户查询
-- 2. start_time: 支持时间范围查询 (最近7天/30天/1年等)
-- 3. exercise_type: 支持按运动类型筛选
