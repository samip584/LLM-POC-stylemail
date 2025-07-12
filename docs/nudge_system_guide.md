# Nudge System Guide

## Overview

The StyleMail nudge system provides intelligent employee performance tracking and automated communication generation. It stores nudges in PostgreSQL and generates personalized summaries and emails based on employee performance data.

## Database Schema

### Tables

#### `employees`
Stores employee information.

| Column      | Type     | Description                    |
| ----------- | -------- | ------------------------------ |
| id          | String   | Unique employee ID (PK)        |
| name        | String   | Employee full name             |
| email       | String   | Employee email (unique)        |
| department  | String   | Department name                |
| position    | String   | Job title/position             |
| manager_id  | String   | Reference to manager (FK)      |
| created_at  | DateTime | Record creation timestamp      |

#### `nudges`
Individual performance nudges for employees.

| Column                  | Type     | Description                           |
| ----------------------- | -------- | ------------------------------------- |
| id                      | Integer  | Auto-increment ID (PK)                |
| employee_id             | String   | Reference to employee (FK)            |
| nudge_type              | String   | performance, attendance, peer_review  |
| title                   | String   | Short nudge description               |
| message                 | Text     | Detailed nudge message                |
| instructions            | Text     | Action items for employee             |
| metric_name             | String   | Name of measured metric               |
| metric_value            | Float    | Current metric value                  |
| threshold               | Float    | Expected threshold value              |
| operator                | String   | Comparison operator                   |
| unit                    | String   | Measurement unit (%, count, etc.)     |
| date_range_from         | DateTime | Start of measurement period           |
| date_range_to           | DateTime | End of measurement period             |
| prior_date_range_from   | DateTime | Start of comparison period            |
| prior_date_range_to     | DateTime | End of comparison period              |
| status                  | String   | active, resolved, dismissed           |
| created_at              | DateTime | Nudge creation timestamp              |

#### `attendance_records`
Employee clock-in/clock-out tracking.

| Column        | Type     | Description                        |
| ------------- | -------- | ---------------------------------- |
| id            | Integer  | Auto-increment ID (PK)             |
| employee_id   | String   | Reference to employee (FK)         |
| date          | DateTime | Attendance date                    |
| clock_in      | DateTime | Clock-in timestamp                 |
| clock_out     | DateTime | Clock-out timestamp                |
| status        | String   | on_time, late, early, absent       |
| minutes_late  | Integer  | Minutes arrived late               |
| minutes_early | Integer  | Minutes arrived early              |

#### `nudge_summaries`
Generated AI summaries of employee nudges (cached).

| Column        | Type     | Description                     |
| ------------- | -------- | ------------------------------- |
| id            | Integer  | Auto-increment ID (PK)          |
| employee_id   | String   | Reference to employee (FK)      |
| summary       | Text     | Generated summary text          |
| nudge_snippet | Text     | Summary of included nudges      |
| created_at    | DateTime | Summary generation timestamp    |

#### `nudge_emails`
Generated emails for nudges.

| Column        | Type     | Description                     |
| ------------- | -------- | ------------------------------- |
| id            | Integer  | Auto-increment ID (PK)          |
| employee_id   | String   | Reference to employee (FK)      |
| subject       | String   | Email subject line              |
| body          | Text     | Email body content              |
| nudge_snippet | Text     | Summary of included nudges      |
| sent          | Boolean  | Whether email was sent          |
| sent_at       | DateTime | Email send timestamp            |
| created_at    | DateTime | Email generation timestamp      |

## API Endpoints

### Fetch Nudge Data
`POST /fetch-nudge-data`

Retrieves active nudges for an employee from PostgreSQL.

**Request:**
```json
{
  "user_id": "manager_123",
  "prompt": "unused",
  "email": "unused@example.com",
  "password": "unused",
  "employee_id": "emp_001"
}
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "nudge_type": "performance",
      "metric_value": 12.0,
      "config": {
        "message": "Declining Code Review Participation",
        "metaData": "Instructions...",
        "threshold": 20.0,
        "metric": "code_reviews_completed",
        "unit": "count",
        "operator": "less_than",
        "dateRange": {"from": "...", "to": "..."},
        "priorDateRange": {"from": "...", "to": "..."}
      }
    }
  ]
}
```

### Generate Nudge Summary
`POST /nudge-summary`

Generates an AI-powered summary of employee nudges. Results are cached in `nudge_summaries` table.

**Request:**
```json
{
  "user_id": "manager_123",
  "prompt": "Create a professional summary",
  "email": "unused",
  "password": "unused",
  "employee_id": "emp_001"
}
```

**Response:**
```json
{
  "summary": "### Professional Summary...\n\n#### 1. Issue Name\n- Details..."
}
```

**Caching:** If a summary exists for the same employee with the same set of nudges, it returns the cached version instead of generating a new one.

### Generate Nudge Email
`POST /nudge-email`

Generates a personalized email based on employee nudges. Saves generated email to `nudge_emails` table.

**Request:**
```json
{
  "user_id": "manager_123",
  "prompt": "Write a supportive email",
  "email": "unused",
  "password": "unused",
  "employee_id": "emp_001"
}
```

**Response:**
```json
{
  "subject": "Performance Discussion",
  "body": "Dear Employee,\n\n..."
}
```

## Seeding Demo Data

### Running the Seed Script

```bash
# Using Docker
docker compose exec app python seed_nudges.py

# Or locally (ensure DATABASE_URL is set)
python seed_nudges.py
```

### What Gets Seeded

1. **3 Employees:**
   - `emp_001`: Sarah Johnson (Senior Software Engineer)
   - `emp_002`: Michael Chen (Marketing Specialist)
   - `emp_003`: Emily Rodriguez (Sales Representative)

2. **6 Nudges:**
   - **Performance** (emp_001): Code review participation, sprint velocity
   - **Attendance** (emp_001): Late arrivals
   - **Peer Review** (emp_002): Pending feedback
   - **Collaboration** (emp_002): Meeting attendance
   - **Training** (emp_003): Overdue compliance training

3. **12 Attendance Records** for emp_001:
   - 6 late arrivals (ranging from 18 to 65 minutes late)
   - 4 on-time arrivals
   - 2 early arrivals

## Nudge Types

| Type          | Description                                  | Example Metrics                  |
| ------------- | -------------------------------------------- | -------------------------------- |
| performance   | Work output and quality metrics              | code_reviews, story_points       |
| attendance    | Punctuality and presence                     | late_arrivals, absences          |
| peer_review   | Peer feedback and collaboration              | reviews_pending, feedback_given  |
| collaboration | Team interaction and meeting participation   | meeting_attendance_rate          |
| training      | Required courses and certifications          | overdue_modules, completion_rate |

## Example Workflow

1. **Seed Data:**
   ```bash
   docker compose exec app python seed_nudges.py
   ```

2. **Fetch Nudges:**
   ```bash
   curl -X POST http://localhost:8000/fetch-nudge-data \
     -H "Content-Type: application/json" \
     -d '{"user_id":"mgr","prompt":"","email":"","password":"","employee_id":"emp_001"}'
   ```

3. **Generate Summary:**
   ```bash
   curl -X POST http://localhost:8000/nudge-summary \
     -H "Content-Type: application/json" \
     -d '{"user_id":"mgr","prompt":"Professional summary","email":"","password":"","employee_id":"emp_001"}'
   ```

4. **Generate Email:**
   ```bash
   curl -X POST http://localhost:8000/nudge-email \
     -H "Content-Type: application/json" \
     -d '{"user_id":"mgr","prompt":"Supportive email","email":"","password":"","employee_id":"emp_001"}'
   ```

5. **Check Database:**
   ```bash
   docker compose exec postgres psql -U stylemail -d stylemail_db -c "SELECT * FROM nudge_summaries;"
   ```

## Best Practices

1. **Caching:** Nudge summaries are automatically cached. If nudges change for an employee, the old cache is invalidated and a new summary is generated.

2. **Performance:** Use database indexes on frequently queried columns (employee_id, status, date fields).

3. **Data Cleanup:** Periodically archive or delete old resolved nudges to maintain performance.

4. **Monitoring:** Track the `sent` field in `nudge_emails` to ensure emails are being delivered.

5. **Privacy:** Ensure proper access controls are in place for employee performance data.
