const fs = require('fs');
const csv = require('csv-parser');
const mysql = require('mysql2');

// MySQL connection setup
const connection = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

// Function to insert data into MySQL
function insertData(row) {
  const {
    ip_address,
    request_type,
    api,
    protocol_version,
    status_code,
    bytes_sent,
    referrer,
    user_agent,
    response_time
  } = row;

  // Insert into logs table
  connection.query(
    'INSERT INTO logs (ip_address, request_type, api, protocol_version, status_code, bytes_sent, referrer, user_agent, response_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
    [ip_address, request_type, api, protocol_version, status_code, bytes_sent, referrer, user_agent, response_time],
    (err, results) => {
      if (err) throw err;
      console.log('Log inserted:', results.insertId);
    }
  );
}

// Read and process the CSV file
fs.createReadStream('path/to/your/dataset.csv')
  .pipe(csv())
  .on('data', (row) => {
    insertData(row);
  })
  .on('end', () => {
    console.log('CSV file successfully processed');
    connection.end();
  });
