import pandas as pd
import json
from sqlalchemy import create_engine, text
from datetime import datetime
import os
from pathlib import Path

# Setup DB connection
DB_URI = 'mysql+pymysql://root:Parth4950*#@localhost/opsverse2.0'
engine = create_engine(DB_URI)

def process_log_entry(entry, node_id):
    try:
        return {
            "node_id": node_id,
            "timestamp": datetime.strptime(entry.get("timestamp", datetime.now().isoformat()), "%Y-%m-%dT%H:%M:%S"),
            "log_level": entry.get("level", "INFO"),
            "message": entry.get("message", ""),
            "ip_address": entry.get("ip", "0.0.0.0"),
            "request_type": entry.get("request_type", "GET"),
            "api": entry.get("api", "/unknown"),
            "protocol_version": entry.get("protocol", "HTTP/1.1"),
            "status_code": int(entry.get("status", 200)),
            "bytes_sent": int(entry.get("bytes_sent", 0)),
            "referrer": entry.get("referrer", ""),
            "user_agent": entry.get("user_agent", "Unknown"),
            "response_time": float(entry.get("response_time", 0.0))
        }
    except Exception as e:
        print(f"Error processing log entry: {e}")
        return None

def insert_node_if_needed(name, description="Auto-imported node"):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT id FROM nodes WHERE name = :name"), {"name": name})
            row = result.fetchone()
            if row:
                return row[0]
            result = conn.execute(
                text("INSERT INTO nodes (name, description) VALUES (:name, :description)"),
                {"name": name, "description": description}
            )
            return result.lastrowid
    except Exception as e:
        print(f"Database error in insert_node_if_needed: {e}")
        raise

def import_json(filepath, node_name):
    try:
        if not filepath.exists():
            print(f"Error: File not found at {filepath}")
            return

        with open(filepath, "r") as f:
            data = json.load(f)
            
        node_id = insert_node_if_needed(node_name)
        valid_entries = []
        
        for entry in data:
            processed = process_log_entry(entry, node_id)
            if processed:
                valid_entries.append(processed)
                
        if valid_entries:
            df = pd.DataFrame(valid_entries)
            df.to_sql("logs", con=engine, if_exists="append", index=False)
            print(f"Successfully imported {len(valid_entries)} entries from {filepath.name}")
        else:
            print(f"No valid entries found in {filepath.name}")

    except json.JSONDecodeError:
        print(f"Error: File is not valid JSON - {filepath}")
    except Exception as e:
        print(f"Error importing {filepath}: {e}")

def import_csv(filepath, node_name):
    try:
        if not filepath.exists():
            print(f"Error: File not found at {filepath}")
            return

        node_id = insert_node_if_needed(node_name)
        
        # Try different encodings if needed
        try:
            df = pd.read_csv(filepath)
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin1')

        # Add required columns if missing
        df["node_id"] = node_id
        if "timestamp" not in df.columns:
            df["timestamp"] = datetime.now()
        else:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
        if "response_time" not in df.columns:
            df["response_time"] = 0.0
        else:
            df["response_time"] = df["response_time"].astype(float)

        # Standardize column names
        column_mapping = {
            "level": "log_level",
            "ip": "ip_address",
            "request_type": "request_type",
            "url": "api",
            "protocol": "protocol_version",
            "status": "status_code",
            "bytes": "bytes_sent"
        }
        
        df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)

        # Ensure all required columns exist
        required_columns = [
            "log_level", "message", "ip_address", "request_type", "api", 
            "protocol_version", "status_code", "bytes_sent", "referrer", 
            "user_agent", "response_time"
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        df = df[[
            "node_id", "timestamp", "log_level", "message", "ip_address", 
            "request_type", "api", "protocol_version", "status_code", 
            "bytes_sent", "referrer", "user_agent", "response_time"
        ]]
        
        df.to_sql("logs", con=engine, if_exists="append", index=False)
        print(f"Successfully imported {len(df)} entries from {filepath.name}")

    except Exception as e:
        print(f"Error importing {filepath}: {e}")

def main():
    # Define base directory
    base_dir = Path(r"C:\Users\chand\Downloads\preprocessed\Thunderbird")
    
    # Verify base directory exists
    if not base_dir.exists():
        print(f"Error: Base directory not found at {base_dir}")
        return
    
    # List all files in directory for debugging
    print(f"Files found in {base_dir}:")
    for f in base_dir.glob("*"):
        print(f" - {f.name}")
    
    # Import files with error handling
    try:
        # JSON files (note: adding .json extension if needed)
        json_files = [
            ("Thunderbird.log_structured.csv", "Structured Logs"),
            ("Thunderbird.log_embedding_average", "Embedding average"),
            ("Thunderbird.log_embedding_staff", "Embedding Staff")
        ]
        
        for filename, node_name in json_files:
            filepath = base_dir / filename
            # Try with and without .json extension if file not found
            if not filepath.exists() and not filepath.suffix:
                filepath = filepath.with_suffix('.json')
            import_json(filepath, node_name)
        
        # CSV files
        csv_files = [
            ("Thunderbird.log_templates.csv", "Template Logs")
        ]
        
        for filename, node_name in csv_files:
            filepath = base_dir / filename
            import_csv(filepath, node_name)
            
    except Exception as e:
        print(f"Fatal error during import: {e}")

if __name__ == "__main__":
    main()