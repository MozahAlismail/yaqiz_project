# Database Troubleshooting Guide

## Common Issues with init_db.py

### Issue 1: "Cannot connect to PostgreSQL server"

**Error message:**
```
❌ Cannot connect to PostgreSQL server!
   Error: could not connect to server...
```

**Solutions:**

1. **Check if PostgreSQL is running:**

   **Windows:**
   ```cmd
   # Open Services (services.msc) and look for PostgreSQL
   # Or use command:
   sc query postgresql
   ```

   **Linux/Ubuntu:**
   ```bash
   sudo systemctl status postgresql
   # If not running:
   sudo systemctl start postgresql
   ```

   **macOS:**
   ```bash
   brew services list
   # If not running:
   brew services start postgresql@15
   ```

2. **Check your .env file exists and has correct values:**
   ```bash
   # Make sure .env file exists:
   ls -la .env

   # Check the content:
   cat .env
   ```

   Should contain:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres123
   ```

3. **Test PostgreSQL connection manually:**
   ```bash
   psql -h localhost -U postgres -d postgres
   ```

---

### Issue 2: "Password authentication failed"

**Error message:**
```
FATAL: password authentication failed for user "postgres"
```

**Solutions:**

1. **Update password in .env file:**
   ```env
   DB_PASSWORD=your_actual_password
   ```

2. **Reset PostgreSQL password:**

   **Linux/Ubuntu:**
   ```bash
   sudo -u postgres psql
   ALTER USER postgres PASSWORD 'postgres123';
   \q
   ```

   **Windows:**
   ```cmd
   # Run as administrator
   psql -U postgres
   ALTER USER postgres PASSWORD 'postgres123';
   \q
   ```

3. **Check pg_hba.conf authentication method:**
   - Location:
     - Linux: `/etc/postgresql/*/main/pg_hba.conf`
     - Windows: `C:\Program Files\PostgreSQL\*\data\pg_hba.conf`
     - macOS: `/usr/local/var/postgres/pg_hba.conf`

   - Change authentication from `peer` or `ident` to `md5`:
     ```
     # Change this:
     local   all   postgres   peer

     # To this:
     local   all   postgres   md5
     ```

   - Restart PostgreSQL after changes

---

### Issue 3: "ModuleNotFoundError: No module named 'psycopg2'"

**Error message:**
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution:**

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt
```

---

### Issue 4: "ModuleNotFoundError: No module named 'dotenv'"

**Error message:**
```
ModuleNotFoundError: No module named 'dotenv'
```

**Solution:**

```bash
pip install python-dotenv
# Or reinstall all requirements:
pip install -r requirements.txt
```

---

### Issue 5: "database already exists" but tables not created

**Symptoms:**
- Database exists but tables are missing
- Previous initialization failed halfway

**Solution:**

**Option 1: Drop and recreate:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Drop database
DROP DATABASE emergency_dispatch;

# Exit and run init script again
\q
python data/init_db.py
```

**Option 2: Manual table creation:**
```bash
# Connect to the database
psql -U postgres -d emergency_dispatch

# Check what tables exist
\dt

# If tables are missing, run init_db.py again
# It will skip database creation and just create tables
```

---

### Issue 6: Port 5432 already in use / Connection refused

**Error message:**
```
could not connect to server: Connection refused
```

**Solutions:**

1. **Check if another PostgreSQL instance is running:**
   ```bash
   # Linux/Mac
   sudo lsof -i :5432

   # Windows
   netstat -ano | findstr :5432
   ```

2. **Check if PostgreSQL is listening on correct port:**
   ```bash
   psql -U postgres -p 5432
   ```

3. **Change port in .env if PostgreSQL is on different port:**
   ```env
   DB_PORT=5433  # or whatever port PostgreSQL is using
   ```

---

### Issue 7: Permission denied for database

**Error message:**
```
ERROR: permission denied for database emergency_dispatch
```

**Solution:**

```bash
# Connect as postgres superuser
psql -U postgres

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE emergency_dispatch TO postgres;
\c emergency_dispatch
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

\q
```

---

### Issue 8: .env file not being read

**Symptoms:**
- Script uses default values instead of .env values
- "Could not load .env file" warning

**Solutions:**

1. **Check .env file location:**
   ```
   Your project structure should be:

   Hakathon/.dev/
   ├── .env              ← File should be here
   ├── data/
   │   └── init_db.py
   └── ...
   ```

2. **Check .env file permissions:**
   ```bash
   # Linux/Mac
   chmod 644 .env

   # Windows - right-click → Properties → Security
   ```

3. **Manually load environment variables:**
   ```bash
   # Linux/Mac
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=emergency_dispatch
   export DB_USER=postgres
   export DB_PASSWORD=postgres123

   # Windows (cmd)
   set DB_HOST=localhost
   set DB_PORT=5432
   set DB_NAME=emergency_dispatch
   set DB_USER=postgres
   set DB_PASSWORD=postgres123

   # Windows (PowerShell)
   $env:DB_HOST="localhost"
   $env:DB_PORT="5432"
   $env:DB_NAME="emergency_dispatch"
   $env:DB_USER="postgres"
   $env:DB_PASSWORD="postgres123"

   # Then run init script
   python data/init_db.py
   ```

---

## Quick Diagnosis Script

Run this to diagnose common issues:

```bash
# Save as check_db.sh (Linux/Mac) or check_db.bat (Windows)

echo "=== PostgreSQL Diagnosis ==="
echo ""

echo "1. Checking if PostgreSQL is installed..."
which psql && echo "✓ PostgreSQL is installed" || echo "✗ PostgreSQL not found"

echo ""
echo "2. Checking if PostgreSQL is running..."
pg_isready -h localhost -p 5432 && echo "✓ PostgreSQL is running" || echo "✗ PostgreSQL is not running"

echo ""
echo "3. Checking .env file..."
test -f .env && echo "✓ .env file exists" || echo "✗ .env file missing"

echo ""
echo "4. Checking Python packages..."
python -c "import psycopg2; print('✓ psycopg2 installed')" 2>/dev/null || echo "✗ psycopg2 not installed"
python -c "import dotenv; print('✓ python-dotenv installed')" 2>/dev/null || echo "✗ python-dotenv not installed"

echo ""
echo "5. Testing database connection..."
python data/init_db.py
```

---

## Still Having Issues?

1. **Check logs:** Look in `logs/app.log` for detailed error messages

2. **Verify Python version:**
   ```bash
   python --version  # Should be 3.10+
   ```

3. **Verify PostgreSQL version:**
   ```bash
   psql --version  # Should be 12+
   ```

4. **Try the test script:**
   ```bash
   python test_db_connection.py
   ```

5. **Check PostgreSQL logs:**
   - Linux: `/var/log/postgresql/postgresql-*.log`
   - Windows: `C:\Program Files\PostgreSQL\*\data\log\`
   - macOS: `/usr/local/var/log/postgres.log`

---

## Clean Reinstall

If all else fails, try a clean reinstall:

```bash
# 1. Backup any existing data if needed

# 2. Drop the database
psql -U postgres -c "DROP DATABASE IF EXISTS emergency_dispatch;"

# 3. Delete virtual environment
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows

# 4. Create new virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 5. Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# 6. Copy .env.example to .env and edit
cp .env.example .env
# Edit .env with your settings

# 7. Run initialization
python data/init_db.py
```

---

## Need More Help?

If you're still having issues:

1. Check the GitHub issues
2. Review `INSTALLATION_GUIDE.md` for detailed setup instructions
3. Make sure all prerequisites are installed (Python 3.10+, PostgreSQL 12+)
