# main_window.py SQL Query Analysis

## Summary
- **Total SQL queries found:** 45 instances of execute_query/execute_non_query
- **Methods requiring refactoring:** ~20 methods
- **Estimated lines to remove:** ~250-300 lines of direct SQL
- **Repository integration:** All 4 repositories will be used

---

## SQL Queries by Category

### 1. Job Type Operations (JobTypeRepository)

#### refresh_job_types() - Line 715-742
**Current SQL:**
```sql
SELECT id, job_name FROM job_types ORDER BY job_name
```
**Replace with:**
```python
job_type_repo.get_all_job_types()
```

#### add_job_type() - Line 1178-1192
**Current SQL:**
```sql
INSERT INTO job_types (job_name) VALUES (?)
```
**Replace with:**
```python
job_type_repo.create_job_type(job_name)
```

#### delete_job_type() - Line 1194-1221
**Current SQL:**
```sql
DELETE FROM job_types WHERE id = ?
```
**Replace with:**
```python
job_type_repo.delete_job_type(job_id)
```

#### refresh_report_job_types() - Line 1498-1513
**Current SQL:**
```sql
SELECT id, job_name FROM job_types ORDER BY job_name
```
**Replace with:**
```python
job_type_repo.get_all_job_types()
```

---

### 2. Sub Job Type Operations (SubJobRepository)

#### refresh_sub_job_list() - Line 780-813
**Current SQL:**
```sql
SELECT id, sub_job_name, description
FROM sub_job_types
WHERE main_job_id = ? AND is_active = 1
ORDER BY sub_job_name
```
**Replace with:**
```python
sub_job_repo.get_by_main_job(main_job_id, active_only=True)
```

#### add_sub_job_type() - Line 836-879
**Current SQL:**
```sql
SELECT COUNT(*) as count
FROM sub_job_types
WHERE main_job_id = ? AND sub_job_name = ? AND is_active = 1

INSERT INTO sub_job_types (main_job_id, sub_job_name, description)
VALUES (?, ?, ?)
```
**Replace with:**
```python
if sub_job_repo.sub_job_exists(main_job_id, sub_job_name):
    # show warning
else:
    sub_job_repo.create_sub_job(main_job_id, sub_job_name, description)
```

#### delete_sub_job_type() - Line 890-928
**Current SQL:**
```sql
UPDATE sub_job_types SET is_active = 0 WHERE id = ?
```
**Replace with:**
```python
sub_job_repo.deactivate_sub_job(sub_job_id)
```

#### edit_sub_job_type() - Line 993-1005
**Current SQL:**
```sql
SELECT COUNT(*) as count
FROM sub_job_types
WHERE main_job_id = ? AND sub_job_name = ? AND id != ?

UPDATE sub_job_types
SET sub_job_name = ?, description = ?
WHERE id = ?
```
**Replace with:**
```python
# Check for duplicate with different ID
if not sub_job_repo.sub_job_exists(main_job_id, new_name, exclude_id=sub_job_id):
    sub_job_repo.update_sub_job(sub_job_id, new_name, new_description)
```

#### on_report_job_type_change() - Line 1515-1556
**Current SQL:**
```sql
SELECT id, sub_job_name
FROM sub_job_types
WHERE main_job_id = ? AND is_active = 1
ORDER BY sub_job_name

# Or for "ทั้งหมด":
SELECT id, sub_job_name
FROM sub_job_types
WHERE is_active = 1
ORDER BY sub_job_name
```
**Replace with:**
```python
if job_type_id:
    results = sub_job_repo.get_by_main_job(job_type_id, active_only=True)
else:
    results = sub_job_repo.get_all_active()
```

**NOTE:** `get_all_active()` method doesn't exist in SubJobRepository yet. Need to add it.

---

### 3. Scan Log Operations (ScanLogRepository)

#### refresh_scanning_history() - Line 670-713
**Current SQL:**
```sql
SELECT TOP 50
    sl.id, sl.barcode, sl.scan_date, sl.job_type as main_job_name,
    sjt.sub_job_name, sl.notes, sl.user_id
FROM scan_logs sl
LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
ORDER BY sl.scan_date DESC
```
**Replace with:**
```python
scan_log_repo.get_recent_scans(limit=50, include_sub_job_name=True)
```

#### process_barcode() - Line 1240-1310
**Current SQL:**
```sql
SELECT id FROM sub_job_types
WHERE main_job_id = ? AND sub_job_name = ? AND is_active = 1

SELECT scan_date, user_id FROM scan_logs
WHERE barcode = ? AND job_id = ? AND sub_job_id = ?
ORDER BY scan_date DESC

INSERT INTO scan_logs (barcode, scan_date, job_type, user_id, job_id, sub_job_id, notes)
VALUES (?, GETDATE(), ?, ?, ?, ?, ?)

SELECT @@IDENTITY as scan_id
```
**Replace with:**
```python
# Get sub job ID
sub_jobs = sub_job_repo.get_by_main_job(main_job_id, active_only=True)
sub_job = next((sj for sj in sub_jobs if sj['sub_job_name'] == sub_job_type), None)
sub_job_id = sub_job['id'] if sub_job else None

# Check duplicate
existing = scan_log_repo.check_duplicate(barcode, job_id=main_job_id, hours=24*365)
if existing and existing['sub_job_id'] == sub_job_id:
    # show duplicate warning
    return

# Create scan
scan_log_repo.create_scan(barcode, job_type, user_id, main_job_id, sub_job_id, notes)
```

#### search_history() - Line 1455-1496
**Current SQL:**
```sql
SELECT sl.id, sl.barcode, sl.scan_date, sl.job_type as main_job_name,
       sjt.sub_job_name, sl.notes, sl.user_id
FROM scan_logs sl
LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
WHERE 1=1
  [AND CAST(sl.scan_date AS DATE) = ?]
  [AND sl.barcode LIKE ?]
  [AND sl.job_type = ?]
ORDER BY sl.scan_date DESC
```
**Replace with:**
```python
scan_log_repo.search_history(
    barcode=barcode_search,
    start_date=date_str,
    end_date=date_str,
    job_id=job_id,  # Need to convert job_name to job_id
    limit=None
)
```

**NOTE:** Current search uses job_type (string), but repository expects job_id (int). Need conversion.

#### generate_report() - Line 1630-1700
**Current SQL:**
```sql
# Complex query with different branches for job_id and sub_job_id filtering
SELECT sl.id, sl.barcode, sl.scan_date, sl.notes, sl.user_id,
       jt.job_name as job_type_name,
       ISNULL(sjt.sub_job_name, 'ไม่มี') as sub_job_type_name
FROM scan_logs sl
LEFT JOIN job_types jt ON sl.job_id = jt.id
LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
WHERE CAST(sl.scan_date AS DATE) = ?
  [AND sl.job_id = ?]
  [AND sl.sub_job_id = ?]
  [AND sl.notes LIKE ?]
ORDER BY sl.scan_date DESC
```
**Replace with:**
```python
if job_type_id and sub_job_type_id:
    results = scan_log_repo.get_report_with_sub_job(
        start_date=report_date,
        end_date=report_date,
        job_id=job_type_id,
        sub_job_id=sub_job_type_id
    )
elif job_type_id:
    results = scan_log_repo.get_report_main_job_only(
        start_date=report_date,
        end_date=report_date,
        job_id=job_type_id
    )
else:
    results = scan_log_repo.get_report_with_sub_job(
        start_date=report_date,
        end_date=report_date
    )

# Note: Repository methods don't support note_filter parameter
# Will need to add this feature or filter results in Python
```

#### delete_history_record() - Line 1762
**Current SQL:**
```sql
DELETE FROM scan_logs WHERE id = ?
```
**Replace with:**
```python
# Repository doesn't have delete method
# Options:
# 1. Add delete method to BaseRepository
# 2. Use db.execute_non_query directly (keep this one as direct SQL)
# 3. Use scan_log_repo.db.execute_non_query()
```

**DECISION:** Keep this as direct SQL for now, or add delete method to BaseRepository.

#### load_today_summary() - Various locations
**Current SQL:**
```sql
SELECT COUNT(*) as total_count
FROM scan_logs
WHERE CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)
  AND job_id = ?
  [AND sub_job_id = ?]
```
**Replace with:**
```python
if sub_job_id:
    count = scan_log_repo.get_today_summary_count(job_id=job_id, sub_job_id=sub_job_id)
else:
    count = scan_log_repo.get_today_summary_count(job_id=job_id)
```

---

### 4. Dependency Operations (DependencyRepository)

#### check_dependencies() - Line 1312-1350
**Current SQL:**
```sql
SELECT jd.required_job_id, jt.job_name
FROM job_dependencies jd
JOIN job_types jt ON jd.required_job_id = jt.id
WHERE jd.job_id = ?

SELECT COUNT(*) as count
FROM scan_logs
WHERE barcode = ? AND job_id = ?
```
**Replace with:**
```python
required_jobs = dependency_repo.get_required_jobs(current_job_id)

for required_job in required_jobs:
    duplicate = scan_log_repo.check_duplicate(
        barcode=barcode,
        job_id=required_job['required_job_id'],
        hours=24*365
    )
    if duplicate is None:
        # show error
        return False
return True
```

#### save_dependencies() - Line 1129-1168
**Current SQL:**
```sql
SELECT id, job_name FROM job_types WHERE id != ? ORDER BY job_name

SELECT jd.required_job_id
FROM job_dependencies jd
WHERE jd.job_id = ?

DELETE FROM job_dependencies WHERE job_id = ?

INSERT INTO job_dependencies (job_id, required_job_id, created_date)
VALUES (?, ?, GETDATE())
```
**Replace with:**
```python
all_jobs = job_type_repo.get_all_job_types()
current_deps = dependency_repo.get_required_jobs(job_id)

# Remove all current dependencies
dependency_repo.remove_all_dependencies(job_id)

# Add new dependencies
for required_job_id in selected_required_jobs:
    dependency_repo.add_dependency(job_id, required_job_id)
```

#### delete_job_type() - Line 1210
**Current SQL:**
```sql
DELETE FROM job_dependencies WHERE job_id = ? OR required_job_id = ?
```
**Replace with:**
```python
# Remove as dependent job
dependency_repo.remove_all_dependencies(job_id)

# Remove as required job (need new method)
dependency_repo.remove_where_required(job_id)
```

**NOTE:** Need to add `remove_where_required(required_job_id)` method to DependencyRepository.

---

### 5. Import/Export Operations (Multiple Repositories)

#### validate_import_data() - Lines 2437-2478
**Current SQL:**
```sql
SELECT job_name FROM job_types WHERE id = ?

SELECT id, sub_job_name
FROM sub_job_types
WHERE main_job_id = ? AND is_active = 1

SELECT scan_date, user_id FROM scan_logs
WHERE barcode = ? AND job_id = ? AND sub_job_id = ?
```
**Replace with:**
```python
job_type = job_type_repo.find_by_id(main_job_id)
sub_jobs = sub_job_repo.get_by_main_job(main_job_id, active_only=True)
existing = scan_log_repo.check_duplicate(barcode, job_id=main_job_id, hours=24*365)
```

**NOTE:** Need to add `find_by_id(id)` method to JobTypeRepository.

#### import_scans() - Lines 2547-2551
**Current SQL:**
```sql
SELECT job_name FROM job_types WHERE id = ?

INSERT INTO scan_logs (barcode, scan_date, job_type, user_id, job_id, sub_job_id, notes)
VALUES (?, ?, ?, ?, ?, ?, ?)
```
**Replace with:**
```python
job_type = job_type_repo.find_by_id(main_job_id)
scan_log_repo.create_scan(barcode, job_type['job_name'], user_id, main_job_id, sub_job_id, notes)
```

#### export_to_excel() - Lines 2602-2645
**Current SQL:**
```sql
SELECT id FROM job_types WHERE job_name = ?

SELECT id, sub_job_name
FROM sub_job_types
WHERE main_job_id = ? AND is_active = 1

SELECT COUNT(*) as count FROM scan_logs WHERE 1=1 [filters...]
```
**Replace with:**
```python
job_type = job_type_repo.find_by_name(job_name)
sub_jobs = sub_job_repo.get_by_main_job(job_id, active_only=True)
count = scan_log_repo.count({'job_id': job_id, ...})
```

**NOTE:** Need to add `find_by_name(name)` method to JobTypeRepository.

---

## Missing Repository Methods

Based on the analysis, we need to add these methods to repositories:

### JobTypeRepository
1. `find_by_id(job_id)` - Get job type by ID
2. `find_by_name(job_name)` - Get job type by name
3. Already has: `get_all_job_types()`, `create_job_type()`, `delete_job_type()`

### SubJobRepository
1. `get_all_active()` - Get all active sub jobs (no main_job_id filter)
2. `find_by_name(main_job_id, sub_job_name)` - Get sub job by name within main job
3. Already has: `get_by_main_job()`, `create_sub_job()`, `deactivate_sub_job()`, `update_sub_job()`

### ScanLogRepository
1. Support for `note_filter` parameter in report methods
2. Already has: Most needed methods

### DependencyRepository
1. `remove_where_required(required_job_id)` - Remove all dependencies where this job is required
2. Already has: Most needed methods

### BaseRepository
1. `delete(id)` - Delete record by ID (for scan log deletion)

---

## Refactoring Strategy

### Phase 1: Add missing repository methods
1. Add `find_by_id()` and `find_by_name()` to JobTypeRepository
2. Add `get_all_active()` and `find_by_name()` to SubJobRepository
3. Add `remove_where_required()` to DependencyRepository
4. Add `delete()` to BaseRepository
5. Write tests for all new methods (aim for 100% coverage)

### Phase 2: Import repositories to main_window.py
1. Add import statements
2. Create global repository variables
3. Initialize repositories in `__init__()`

### Phase 3: Refactor methods (in order)
1. **Simple reads first:**
   - refresh_job_types()
   - refresh_sub_job_list()
   - refresh_report_job_types()

2. **Simple writes:**
   - add_job_type()
   - add_sub_job_type()

3. **Complex operations:**
   - process_barcode()
   - check_dependencies()
   - search_history()
   - generate_report()

4. **Management operations:**
   - save_dependencies()
   - delete_job_type()
   - edit_sub_job_type()

5. **Import/Export:**
   - validate_import_data()
   - import_scans()
   - export_to_excel()

### Phase 4: Testing
1. Run all 88 existing tests
2. Manually test main_window.py functionality
3. Verify no regressions

---

## Expected Results

- **Lines removed:** ~250-300 lines of SQL code
- **SQL queries reduced:** 45 → ~5-10 (only complex JOINs kept)
- **Code duplication:** Further reduction (15% → ~10%)
- **Maintainability:** Significantly improved
- **Test coverage:** Maintained at 100%

---

**Last Updated:** 2025-11-09
**Next Step:** Add missing repository methods
