CREATE TABLE nodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    log_level VARCHAR(50),
    message TEXT,
    ip_address VARCHAR(45),
    request_type VARCHAR(10),
    api VARCHAR(255),
    protocol_version VARCHAR(50),
    status_code INT,
    bytes_sent INT,
    referrer VARCHAR(255),
    user_agent TEXT,
    response_time FLOAT,
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);


CREATE TABLE issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_id INT,
    issue_type VARCHAR(255),
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES logs(id)
);
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       remote_log_name VARCHAR(255),
       user_id VARCHAR(255),
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );
      CREATE TABLE node_metrics (
       id INT AUTO_INCREMENT PRIMARY KEY,
       node_id INT,
       metric_name VARCHAR(255),
       metric_value FLOAT,
       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (node_id) REFERENCES nodes(id)
   );
      CREATE TABLE alerts (
       id INT AUTO_INCREMENT PRIMARY KEY,
       issue_id INT,
       alert_message TEXT,
       acknowledged BOOLEAN DEFAULT FALSE,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (issue_id) REFERENCES issues(id)
   );
      CREATE TABLE configuration (
       id INT AUTO_INCREMENT PRIMARY KEY,
       config_key VARCHAR(255) UNIQUE NOT NULL,
       config_value TEXT,
       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   );