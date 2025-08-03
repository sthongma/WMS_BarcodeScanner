#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Models Module
Contains data structures and models for the application
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class JobType:
    """โมเดลสำหรับ Job Type"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    is_active: bool = True
    created_date: Optional[datetime] = None
    created_by: str = ""
    modified_date: Optional[datetime] = None
    modified_by: str = ""


@dataclass
class SubJobType:
    """โมเดลสำหรับ Sub Job Type"""
    id: Optional[int] = None
    main_job_id: int = 0
    name: str = ""
    description: str = ""
    is_active: bool = True
    created_date: Optional[datetime] = None
    created_by: str = ""
    modified_date: Optional[datetime] = None
    modified_by: str = ""


@dataclass
class ScanRecord:
    """โมเดลสำหรับ Scan Record"""
    id: Optional[int] = None
    barcode: str = ""
    job_type_id: int = 0
    sub_job_type_id: Optional[int] = None
    scan_date: Optional[datetime] = None
    scanned_by: str = ""
    status: str = "Active"
    notes: str = ""
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None


@dataclass
class DatabaseConfig:
    """โมเดลสำหรับการตั้งค่าฐานข้อมูล"""
    server: str = ""
    database: str = ""
    auth_type: str = "SQL"  # Windows หรือ SQL
    username: str = ""
    password: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """แปลงเป็น dictionary"""
        return {
            "server": self.server,
            "database": self.database,
            "auth_type": self.auth_type,
            "username": self.username,
            "password": self.password
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseConfig':
        """สร้างจาก dictionary"""
        return cls(
            server=data.get("server", ""),
            database=data.get("database", ""),
            auth_type=data.get("auth_type", "SQL"),
            username=data.get("username", ""),
            password=data.get("password", "")
        )


@dataclass
class ImportData:
    """โมเดลสำหรับข้อมูลที่นำเข้า"""
    barcode: str
    job_type: str
    sub_job_type: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """แปลงเป็น dictionary"""
        return {
            "barcode": self.barcode,
            "job_type": self.job_type,
            "sub_job_type": self.sub_job_type or "",
            "notes": self.notes
        }


@dataclass
class ReportFilter:
    """โมเดลสำหรับตัวกรองรายงาน"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    job_type_id: Optional[int] = None
    sub_job_type_id: Optional[int] = None
    status: Optional[str] = None
    scanned_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """แปลงเป็น dictionary"""
        return {
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "job_type_id": self.job_type_id,
            "sub_job_type_id": self.sub_job_type_id,
            "status": self.status,
            "scanned_by": self.scanned_by
        }


@dataclass
class ScanDependency:
    """โมเดลสำหรับ dependencies ของการสแกน"""
    id: Optional[int] = None
    job_type_id: int = 0
    dependent_job_type_id: int = 0
    dependency_order: int = 1
    is_required: bool = True
    created_date: Optional[datetime] = None
    created_by: str = ""


class ScanHistory:
    """คลาสสำหรับจัดการประวัติการสแกน"""
    
    def __init__(self):
        self.records: List[ScanRecord] = []
    
    def add_record(self, record: ScanRecord) -> None:
        """เพิ่มรายการสแกน"""
        self.records.append(record)
    
    def get_records_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ScanRecord]:
        """รับรายการสแกนตามช่วงวันที่"""
        return [
            record for record in self.records
            if record.scan_date and start_date <= record.scan_date <= end_date
        ]
    
    def get_records_by_job_type(self, job_type_id: int) -> List[ScanRecord]:
        """รับรายการสแกนตาม job type"""
        return [
            record for record in self.records
            if record.job_type_id == job_type_id
        ]
    
    def get_records_by_barcode(self, barcode: str) -> List[ScanRecord]:
        """รับรายการสแกนตาม barcode"""
        return [
            record for record in self.records
            if record.barcode == barcode
        ]
    
    def to_dataframe(self) -> 'pd.DataFrame':
        """แปลงเป็น pandas DataFrame"""
        import pandas as pd
        
        data = []
        for record in self.records:
            data.append({
                'id': record.id,
                'barcode': record.barcode,
                'job_type_id': record.job_type_id,
                'sub_job_type_id': record.sub_job_type_id,
                'scan_date': record.scan_date,
                'scanned_by': record.scanned_by,
                'status': record.status,
                'notes': record.notes,
                'created_date': record.created_date,
                'modified_date': record.modified_date
            })
        
        return pd.DataFrame(data) 