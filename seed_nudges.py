#!/usr/bin/env python3
"""
Nudge Data Seeding Script for StyleMail POC

This script populates the PostgreSQL database with sample employee and nudge data
to demonstrate the nudge summary and email generation features.
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, Employee, Nudge, AttendanceRecord, init_db

def seed_employees(db: Session):
    """Seed sample employees"""
    employees = [
        Employee(
            id="emp_001",
            name="Sarah Johnson",
            email="sarah.johnson@company.com",
            department="Engineering",
            position="Senior Software Engineer",
            manager_id=None
        ),
        Employee(
            id="emp_002",
            name="Michael Chen",
            email="michael.chen@company.com",
            department="Marketing",
            position="Marketing Specialist",
            manager_id=None
        ),
        Employee(
            id="emp_003",
            name="Emily Rodriguez",
            email="emily.rodriguez@company.com",
            department="Sales",
            position="Sales Representative",
            manager_id=None
        ),
    ]
    
    for employee in employees:
        existing = db.query(Employee).filter(Employee.id == employee.id).first()
        if not existing:
            db.add(employee)
            print(f"✅ Created employee: {employee.name} ({employee.id})")
        else:
            print(f"⏭️  Employee already exists: {employee.name} ({employee.id})")
    
    db.commit()
    return employees


def seed_attendance_records(db: Session, employee_id: str):
    """Seed attendance records for an employee"""
    today = datetime.now()
    standard_start = datetime.strptime("09:00", "%H:%M").time()
    
    # Generate 30 days of attendance
    attendance_data = [
        # Late arrivals
        {"days_ago": 2, "clock_in": "09:35", "status": "late", "minutes_late": 35},
        {"days_ago": 5, "clock_in": "09:22", "status": "late", "minutes_late": 22},
        {"days_ago": 8, "clock_in": "09:45", "status": "late", "minutes_late": 45},
        {"days_ago": 12, "clock_in": "09:18", "status": "late", "minutes_late": 18},
        {"days_ago": 15, "clock_in": "10:05", "status": "late", "minutes_late": 65},
        {"days_ago": 20, "clock_in": "09:27", "status": "late", "minutes_late": 27},
        
        # On time
        {"days_ago": 1, "clock_in": "08:55", "status": "on_time", "minutes_late": 0},
        {"days_ago": 3, "clock_in": "08:58", "status": "on_time", "minutes_late": 0},
        {"days_ago": 6, "clock_in": "09:00", "status": "on_time", "minutes_late": 0},
        {"days_ago": 10, "clock_in": "08:50", "status": "on_time", "minutes_late": 0},
        
        # Early arrivals
        {"days_ago": 4, "clock_in": "08:30", "status": "early", "minutes_early": 30},
        {"days_ago": 7, "clock_in": "08:40", "status": "early", "minutes_early": 20},
    ]
    
    for record in attendance_data:
        date = today - timedelta(days=record["days_ago"])
        clock_in_time = datetime.strptime(record["clock_in"], "%H:%M").time()
        clock_in_datetime = datetime.combine(date.date(), clock_in_time)
        clock_out_datetime = clock_in_datetime + timedelta(hours=8)
        
        attendance = AttendanceRecord(
            employee_id=employee_id,
            date=date,
            clock_in=clock_in_datetime,
            clock_out=clock_out_datetime,
            status=record["status"],
            minutes_late=record.get("minutes_late", 0),
            minutes_early=record.get("minutes_early", 0)
        )
        db.add(attendance)
    
    db.commit()
    print(f"✅ Created {len(attendance_data)} attendance records for {employee_id}")


def seed_nudges(db: Session):
    """Seed sample nudges for employees"""
    today = datetime.now()
    
    nudges_data = [
        # Performance-related nudges
        {
            "employee_id": "emp_001",
            "nudge_type": "performance",
            "title": "Declining Code Review Participation",
            "message": "Your code review activity has decreased by 40% compared to last month",
            "instructions": "Please increase your participation in code reviews. Aim to review at least 5 pull requests per week and provide constructive feedback to team members.",
            "metric_name": "code_reviews_completed",
            "metric_value": 12.0,
            "threshold": 20.0,
            "operator": "less_than",
            "unit": "count",
            "date_range_from": today - timedelta(days=30),
            "date_range_to": today,
            "prior_date_range_from": today - timedelta(days=60),
            "prior_date_range_to": today - timedelta(days=30),
        },
        {
            "employee_id": "emp_001",
            "nudge_type": "performance",
            "title": "Low Sprint Velocity",
            "message": "Your story points completed this sprint are 35% below team average",
            "instructions": "Review your task breakdown and time management. Consider pair programming sessions if you're blocked on complex issues. Reach out to your tech lead for support.",
            "metric_name": "story_points_completed",
            "metric_value": 13.0,
            "threshold": 20.0,
            "operator": "less_than",
            "unit": "points",
            "date_range_from": today - timedelta(days=14),
            "date_range_to": today,
            "prior_date_range_from": today - timedelta(days=28),
            "prior_date_range_to": today - timedelta(days=14),
        },
        
        # Attendance-related nudges
        {
            "employee_id": "emp_001",
            "nudge_type": "attendance",
            "title": "Frequent Late Arrivals",
            "message": "You've been late 6 times in the past 20 working days",
            "instructions": "Please ensure you arrive by 9:00 AM. If you're experiencing commute issues, discuss flexible hours with your manager. Consistent tardiness impacts team standup meetings.",
            "metric_name": "late_arrivals",
            "metric_value": 6.0,
            "threshold": 3.0,
            "operator": "greater_than",
            "unit": "days",
            "date_range_from": today - timedelta(days=20),
            "date_range_to": today,
            "prior_date_range_from": today - timedelta(days=40),
            "prior_date_range_to": today - timedelta(days=20),
        },
        
        # Peer review nudge
        {
            "employee_id": "emp_002",
            "nudge_type": "peer_review",
            "title": "Pending Peer Feedback Collection",
            "message": "You have 3 pending peer review requests that need completion",
            "instructions": "Please complete peer reviews for your colleagues by end of this week. Your feedback is important for their performance evaluations and professional development.",
            "metric_name": "peer_reviews_pending",
            "metric_value": 3.0,
            "threshold": 0.0,
            "operator": "greater_than",
            "unit": "count",
            "date_range_from": today - timedelta(days=7),
            "date_range_to": today,
            "prior_date_range_from": None,
            "prior_date_range_to": None,
        },
        
        # Collaboration nudge
        {
            "employee_id": "emp_002",
            "nudge_type": "collaboration",
            "title": "Low Meeting Attendance Rate",
            "message": "Your meeting attendance rate is 65%, below the expected 90%",
            "instructions": "Please make an effort to attend scheduled team meetings. If you have conflicts, notify the organizer in advance and review meeting notes afterward.",
            "metric_name": "meeting_attendance_rate",
            "metric_value": 65.0,
            "threshold": 90.0,
            "operator": "less_than",
            "unit": "%",
            "date_range_from": today - timedelta(days=30),
            "date_range_to": today,
            "prior_date_range_from": today - timedelta(days=60),
            "prior_date_range_to": today - timedelta(days=30),
        },
        
        # Training nudge
        {
            "employee_id": "emp_003",
            "nudge_type": "training",
            "title": "Overdue Compliance Training",
            "message": "You have 2 mandatory training modules that are overdue",
            "instructions": "Complete the following trainings by end of week: 1) Data Privacy & Security (2 hours), 2) Workplace Harassment Prevention (1.5 hours). These are required for all employees.",
            "metric_name": "overdue_training_modules",
            "metric_value": 2.0,
            "threshold": 0.0,
            "operator": "greater_than",
            "unit": "modules",
            "date_range_from": today - timedelta(days=60),
            "date_range_to": today,
            "prior_date_range_from": None,
            "prior_date_range_to": None,
        },
    ]
    
    for nudge_data in nudges_data:
        nudge = Nudge(**nudge_data)
        db.add(nudge)
        print(f"✅ Created nudge: {nudge.title} for {nudge.employee_id}")
    
    db.commit()
    print(f"\n✅ Successfully seeded {len(nudges_data)} nudges")


def main():
    """Main seeding function"""
    print("=" * 70)
    print("StyleMail Nudge Data Seeding Script")
    print("=" * 70)
    print()
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print()
    
    # Create database session
    db = SessionLocal()
    
    try:
        print("Seeding employees...")
        print("-" * 70)
        employees = seed_employees(db)
        print()
        
        print("Seeding attendance records...")
        print("-" * 70)
        seed_attendance_records(db, "emp_001")
        print()
        
        print("Seeding nudges...")
        print("-" * 70)
        seed_nudges(db)
        print()
        
        print("=" * 70)
        print("✨ Seeding completed successfully!")
        print()
        print("Sample Employees:")
        for emp in employees:
            print(f"  - {emp.name} ({emp.id}) - {emp.position}")
        print()
        print("You can now use these employee IDs in your nudge API calls:")
        print("  - emp_001: Sarah Johnson (has performance + attendance nudges)")
        print("  - emp_002: Michael Chen (has peer review + collaboration nudges)")
        print("  - emp_003: Emily Rodriguez (has training nudge)")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
