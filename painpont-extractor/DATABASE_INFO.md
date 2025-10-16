# PostgreSQL Database Information

## Database Setup Complete ✓

Successfully installed PostgreSQL and loaded 75 records from `data.json` into the database.

## Connection Details

- **Database Name**: `topics_db`
- **User**: `postgres`
- **Table Name**: `topics`
- **Total Records**: 75

## Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer (PRIMARY KEY) | Auto-incrementing unique identifier |
| `topic` | varchar(500) | Topic name |
| `volume` | varchar(50) | Search volume |
| `growth` | varchar(50) | Growth percentage |
| `description` | text | Detailed description |
| `url` | varchar(1000) | Topic URL |
| `time_period` | varchar(50) | Time period (e.g., "2 Years", "10 Years") |
| `created_at` | timestamp | Record creation timestamp |

## Useful Commands

### Connect to Database
```bash
sudo -u postgres psql -d topics_db
```

### View All Records
```bash
sudo -u postgres psql -d topics_db -c "SELECT * FROM topics;"
```

### Count Total Records
```bash
sudo -u postgres psql -d topics_db -c "SELECT COUNT(*) FROM topics;"
```

### Search by Topic
```bash
sudo -u postgres psql -d topics_db -c "SELECT * FROM topics WHERE topic ILIKE '%AI%';"
```

### Get Top Growth Topics
```bash
sudo -u postgres psql -d topics_db -c "SELECT topic, volume, growth FROM topics ORDER BY id LIMIT 10;"
```

### Filter by Time Period
```bash
sudo -u postgres psql -d topics_db -c "SELECT topic, growth FROM topics WHERE time_period = '2 Years';"
```

## Sample Data (First 10 Records)

| ID | Topic | Volume | Growth | Time Period |
|----|-------|--------|--------|-------------|
| 1 | Pdrn toner | 880 | +6600% | 2 Years |
| 2 | Soursop bitters | 110K | +725% | 2 Years |
| 3 | Together AI | 2K | +689% | 2 Years |
| 4 | Shilajit honey | 4K | +645% | 2 Years |
| 5 | Lash Clusters | 165K | +575% | 2 Years |
| 6 | Wifi 7 router | 5K | +428% | 2 Years |
| 7 | Secops | 1K | +353% | 2 Years |
| 8 | Build ai | 9K | +238% | 2 Years |
| 9 | 20K PowerBank | 6K | +204% | 2 Years |
| 10 | Sitegpt | 1K | +184% | 2 Years |

## Python Script

The data loading script is available at:
- `/root/dbas/backend-final/painpont-extractor/load_data_to_postgres.py`
- `/tmp/load_data_to_postgres.py`

To reload data:
```bash
cd /tmp && sudo -u postgres python3 load_data_to_postgres.py
```

## Database Management

### Backup Database
```bash
sudo -u postgres pg_dump topics_db > topics_db_backup.sql
```

### Restore Database
```bash
sudo -u postgres psql topics_db < topics_db_backup.sql
```

### Stop PostgreSQL Service
```bash
sudo service postgresql stop
```

### Start PostgreSQL Service
```bash
sudo service postgresql start
```

### Check PostgreSQL Status
```bash
sudo service postgresql status
```

