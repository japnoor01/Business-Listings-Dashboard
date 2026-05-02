-- ============================================================
-- Business Listings Dashboard - MySQL Schema
-- ============================================================

-- Create and select database
CREATE DATABASE IF NOT EXISTS business_dashboard
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE business_dashboard;

-- ============================================================
-- Table: listing_master
-- ============================================================
CREATE TABLE IF NOT EXISTS listing_master (
    id            INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    business_name VARCHAR(255)    NOT NULL,
    category      VARCHAR(100)    NOT NULL,
    city          VARCHAR(100)    NOT NULL,
    address       VARCHAR(500)    DEFAULT NULL,
    phone         VARCHAR(20)     DEFAULT NULL,
    source        VARCHAR(50)     NOT NULL,
    created_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- Indexes for dashboard query performance
    INDEX idx_city        (city),
    INDEX idx_category    (category),
    INDEX idx_source      (source),
    INDEX idx_created_at  (created_at)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Master table for business listings scraped from multiple directories';


-- ============================================================
-- Dashboard Views (optional convenience layer)
-- ============================================================

-- City-wise count view
CREATE OR REPLACE VIEW vw_city_wise AS
SELECT
    city                          AS name,
    COUNT(*)                      AS count
FROM listing_master
GROUP BY city
ORDER BY count DESC;

-- Category-wise count view
CREATE OR REPLACE VIEW vw_category_wise AS
SELECT
    category                      AS name,
    COUNT(*)                      AS count
FROM listing_master
GROUP BY category
ORDER BY count DESC;

-- Source-wise count view
CREATE OR REPLACE VIEW vw_source_wise AS
SELECT
    source                        AS name,
    COUNT(*)                      AS count
FROM listing_master
GROUP BY source
ORDER BY count DESC;

-- ============================================================
-- Sample data verification queries
-- ============================================================
-- SELECT * FROM listing_master LIMIT 10;
-- SELECT * FROM vw_city_wise;
-- SELECT * FROM vw_category_wise;
-- SELECT * FROM vw_source_wise;
-- SELECT COUNT(*) AS total FROM listing_master;
