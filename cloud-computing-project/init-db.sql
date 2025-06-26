CREATE DATABASE cloud_monitor_db;
USE cloud_monitor_db;

CREATE TABLE container_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    container_id VARCHAR(255) NOT NULL,
    container_name VARCHAR(255) NOT NULL,
    cpu_usage DECIMAL(5,2) NOT NULL,
    memory_usage DECIMAL(5,2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE service_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    status ENUM('running', 'down', 'warning') NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO service_status (service_name, status) VALUES
('api-gateway', 'running'),
('user-service', 'running'),
('data-service', 'running');    