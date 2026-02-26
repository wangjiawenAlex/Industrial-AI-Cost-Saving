CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS business_data (
  id SERIAL PRIMARY KEY,
  order_id VARCHAR(20) UNIQUE NOT NULL,
  customer_name VARCHAR(100),
  status VARCHAR(30) NOT NULL,
  status_code VARCHAR(10),
  progress_percentage INTEGER,
  details TEXT,
  expected_completion VARCHAR(30),
  last_update VARCHAR(30),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS query_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  raw_query TEXT NOT NULL,
  order_id VARCHAR(20),
  llm_extracted_intent TEXT,
  business_raw_response TEXT,
  llm_final_response TEXT,
  status VARCHAR(20) DEFAULT 'success',
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_order_id ON query_logs(order_id);
