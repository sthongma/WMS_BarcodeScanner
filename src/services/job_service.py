#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Service
Handles job types and sub job types business logic
"""

from typing import Dict, Any, Optional, List
from database.database_manager import DatabaseManager


class JobService:
    """บริการจัดการประเภทงาน"""
    
    def __init__(self, context: str = "Service: JobService"):
        self.db = DatabaseManager.get_instance(None, context)
    
    def get_all_job_types(self) -> List[Dict[str, Any]]:
        """ดึงประเภทงานทั้งหมด"""
        try:
            query = "SELECT id, job_name FROM job_types ORDER BY job_name"
            results = self.db.execute_query(query)
            
            job_types = []
            for row in results:
                job_types.append({
                    'id': row['id'],
                    'name': row['job_name']
                })
            
            return job_types
            
        except Exception as e:
            print(f"Error getting job types: {str(e)}")
            return []
    
    def get_sub_job_types(self, main_job_id: int) -> List[Dict[str, Any]]:
        """ดึงประเภทงานย่อยตาม main job ID"""
        try:
            query = """
                SELECT id, sub_job_name 
                FROM sub_job_types 
                WHERE main_job_id = ? AND is_active = 1 
                ORDER BY sub_job_name
            """
            results = self.db.execute_query(query, (main_job_id,))
            
            sub_job_types = []
            for row in results:
                sub_job_types.append({
                    'id': row['id'],
                    'name': row['sub_job_name']
                })
            
            return sub_job_types
            
        except Exception as e:
            print(f"Error getting sub job types: {str(e)}")
            return []
    
    def create_job_type(self, job_name: str) -> bool:
        """สร้างประเภทงานใหม่"""
        try:
            # Check if already exists
            check_query = "SELECT COUNT(*) as count FROM job_types WHERE job_name = ?"
            result = self.db.execute_query(check_query, (job_name,))

            if result[0]['count'] > 0:
                raise ValueError(f"ประเภทงาน '{job_name}' มีอยู่แล้ว")

            # Insert new job type
            insert_query = "INSERT INTO job_types (job_name) VALUES (?)"
            self.db.execute_non_query(insert_query, (job_name,))

            return True

        except Exception as e:
            print(f"Error creating job type: {str(e)}")
            return False

    def update_job_type(self, job_id: int, job_name: str) -> bool:
        """อัปเดตประเภทงานหลัก"""
        try:
            # Check if new name already exists for a different job
            check_query = "SELECT COUNT(*) as count FROM job_types WHERE job_name = ? AND id != ?"
            result = self.db.execute_query(check_query, (job_name, job_id))

            if result[0]['count'] > 0:
                raise ValueError(f"ประเภทงาน '{job_name}' มีอยู่แล้ว")

            update_query = "UPDATE job_types SET job_name = ? WHERE id = ?"
            self.db.execute_non_query(update_query, (job_name, job_id))

            return True

        except Exception as e:
            print(f"Error updating job type: {str(e)}")
            return False
    
    def create_sub_job_type(self, main_job_id: int, sub_job_name: str, description: str = None) -> bool:
        """สร้างประเภทงานย่อยใหม่"""
        try:
            # Check if already exists for this main job
            check_query = """
                SELECT COUNT(*) as count 
                FROM sub_job_types 
                WHERE main_job_id = ? AND sub_job_name = ?
            """
            result = self.db.execute_query(check_query, (main_job_id, sub_job_name))
            
            if result[0]['count'] > 0:
                raise ValueError(f"ประเภทงานย่อย '{sub_job_name}' มีอยู่แล้วในงานหลักนี้")
            
            # Insert new sub job type
            insert_query = """
                INSERT INTO sub_job_types (main_job_id, sub_job_name, description, is_active)
                VALUES (?, ?, ?, 1)
            """
            self.db.execute_non_query(insert_query, (main_job_id, sub_job_name, description))
            
            return True
            
        except Exception as e:
            print(f"Error creating sub job type: {str(e)}")
            return False
    
    def update_sub_job_type(self, sub_job_id: int, sub_job_name: str, description: str = None) -> bool:
        """อัปเดตประเภทงานย่อย"""
        try:
            update_query = """
                UPDATE sub_job_types 
                SET sub_job_name = ?, description = ?, updated_date = GETDATE()
                WHERE id = ?
            """
            self.db.execute_non_query(update_query, (sub_job_name, description, sub_job_id))
            
            return True
            
        except Exception as e:
            print(f"Error updating sub job type: {str(e)}")
            return False
    
    def delete_sub_job_type(self, sub_job_id: int) -> bool:
        """ลบประเภทงานย่อย (soft delete)"""
        try:
            # Check if there are any scan logs using this sub job type
            check_query = "SELECT COUNT(*) as count FROM scan_logs WHERE sub_job_id = ?"
            result = self.db.execute_query(check_query, (sub_job_id,))
            
            if result[0]['count'] > 0:
                # Soft delete - just mark as inactive
                update_query = "UPDATE sub_job_types SET is_active = 0 WHERE id = ?"
                self.db.execute_non_query(update_query, (sub_job_id,))
            else:
                # Hard delete - no scan logs reference this
                delete_query = "DELETE FROM sub_job_types WHERE id = ?"
                self.db.execute_non_query(delete_query, (sub_job_id,))
            
            return True
            
        except Exception as e:
            print(f"Error deleting sub job type: {str(e)}")
            return False
    
    def get_job_dependencies(self, job_id: int) -> List[Dict[str, Any]]:
        """ดึง dependencies ของงาน"""
        try:
            query = """
                SELECT jd.required_job_id, jt.job_name 
                FROM job_dependencies jd
                JOIN job_types jt ON jd.required_job_id = jt.id
                WHERE jd.job_id = ?
            """
            results = self.db.execute_query(query, (job_id,))
            
            dependencies = []
            for row in results:
                dependencies.append({
                    'required_job_id': row['required_job_id'],
                    'required_job_name': row['job_name']
                })
            
            return dependencies
            
        except Exception as e:
            print(f"Error getting job dependencies: {str(e)}")
            return []
    
    def check_job_dependencies(self, barcode: str, job_id: int) -> Dict[str, Any]:
        """ตรวจสอบ dependencies ของงาน"""
        try:
            dependencies = self.get_job_dependencies(job_id)
            
            if not dependencies:
                return {'success': True, 'message': 'ไม่มี dependencies'}
            
            # Check each dependency
            for dep in dependencies:
                check_query = """
                    SELECT COUNT(*) as count 
                    FROM scan_logs 
                    WHERE barcode = ? AND job_id = ?
                """
                result = self.db.execute_query(check_query, (barcode, dep['required_job_id']))
                
                if result[0]['count'] == 0:
                    return {
                        'success': False,
                        'message': f'ต้องสแกนงาน "{dep["required_job_name"]}" ก่อน'
                    }
            
            return {'success': True, 'message': 'Dependencies ถูกต้อง'}
            
        except Exception as e:
            print(f"Error checking job dependencies: {str(e)}")
            return {'success': False, 'message': f'เกิดข้อผิดพลาดในการตรวจสอบ: {str(e)}'}
    
    def ensure_tables_exist(self) -> bool:
        """ตรวจสอบและสร้างตารางที่จำเป็น"""
        try:
            # Check and create job_types table
            try:
                check_query = "SELECT COUNT(*) as count FROM job_types"
                self.db.execute_query(check_query)
            except:
                create_query = """
                CREATE TABLE job_types (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    job_name VARCHAR(100) NOT NULL UNIQUE
                )
                """
                self.db.execute_non_query(create_query)
                
                # Insert sample data
                sample_jobs = [
                    '1.Release', '2.Inprocess', '3.Outbound', 
                    '4.Loading', '5.Return', '6.Repack'
                ]
                
                for job_name in sample_jobs:
                    insert_query = "INSERT INTO job_types (job_name) VALUES (?)"
                    try:
                        self.db.execute_non_query(insert_query, (job_name,))
                    except:
                        pass  # Job might already exist
            
            # Check and create sub_job_types table
            try:
                check_query = "SELECT COUNT(*) as count FROM sub_job_types"
                self.db.execute_query(check_query)
            except:
                create_query = """
                CREATE TABLE sub_job_types (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    main_job_id INT NOT NULL,
                    sub_job_name NVARCHAR(255) NOT NULL,
                    description NVARCHAR(500) NULL,
                    created_date DATETIME2 DEFAULT GETDATE(),
                    updated_date DATETIME2 DEFAULT GETDATE(),
                    is_active BIT DEFAULT 1,
                    CONSTRAINT FK_sub_job_types_main_job 
                        FOREIGN KEY (main_job_id) REFERENCES job_types(id) 
                        ON DELETE CASCADE,
                    CONSTRAINT UQ_sub_job_types_name_per_main 
                        UNIQUE (main_job_id, sub_job_name)
                )
                """
                self.db.execute_non_query(create_query)
            
            # Check and create job_dependencies table
            try:
                check_query = "SELECT COUNT(*) as count FROM job_dependencies"
                self.db.execute_query(check_query)
            except:
                create_query = """
                CREATE TABLE job_dependencies (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    job_id INT NOT NULL,
                    required_job_id INT NOT NULL,
                    created_date DATETIME2 DEFAULT GETDATE(),
                    CONSTRAINT FK_job_dependencies_job_id 
                        FOREIGN KEY (job_id) REFERENCES job_types(id),
                    CONSTRAINT FK_job_dependencies_required_job_id 
                        FOREIGN KEY (required_job_id) REFERENCES job_types(id),
                    CONSTRAINT UQ_job_dependencies_unique 
                        UNIQUE (job_id, required_job_id)
                )
                """
                self.db.execute_non_query(create_query)
            
            return True
            
        except Exception as e:
            print(f"Error ensuring tables exist: {str(e)}")
            return False