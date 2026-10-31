import pandas as pd
import os
import uuid
from pathlib import Path
from datetime import date


# =====================================================
# 1. DATA STORAGE CONFIGURATION
# =====================================================

DATA_FOLDER = Path(__file__).parent / "installation_data"

DATA_FOLDER.mkdir(exist_ok=True)

EQUIPMENT_FILE = DATA_FOLDER / "equipment.csv"
CHECKLIST_FILE = DATA_FOLDER / "installation_checklist.csv"
MAINTENANCE_FILE = DATA_FOLDER / "maintenance.csv"
INSPECTION_FILE = DATA_FOLDER / "inspections.csv"


# =====================================================
# 2. DATA STRUCTURES
# =====================================================

EQUIPMENT_COLUMNS = [
    "Equipment ID",
    "Equipment Name",
    "Category",
    "Location",
    "Quantity",
    "Installation Date",
    "Status"
]

CHECKLIST_COLUMNS = [
    "Equipment ID",
    "Activity",
    "Status",
    "Remarks",
    "Date"
]

MAINTENANCE_COLUMNS = [
    "Maintenance ID",
    "Equipment ID",
    "Equipment Name",
    "Maintenance Activity",
    "Scheduled Date",
    "Frequency",
    "Status"
]

INSPECTION_COLUMNS = [
    "Inspection ID",
    "Equipment ID",
    "Equipment Name",
    "Inspection Date",
    "Condition",
    "Fault Description",
    "Corrective Action"
]


# =====================================================
# 3. DATA LOADING AND SAVING
# =====================================================

def load_data(filename, columns):
    """Load records from a CSV file."""

    if filename.exists():
        return pd.read_csv(filename)

    return pd.DataFrame(columns=columns)


def save_data(dataframe, filename):
    """Save records to a CSV file."""

    dataframe.to_csv(filename, index=False)


def load_equipment():
    return load_data(EQUIPMENT_FILE, EQUIPMENT_COLUMNS)


def load_checklist():
    return load_data(CHECKLIST_FILE, CHECKLIST_COLUMNS)


def load_maintenance():
    return load_data(MAINTENANCE_FILE, MAINTENANCE_COLUMNS)


def load_inspections():
    return load_data(INSPECTION_FILE, INSPECTION_COLUMNS)


# =====================================================
# 4. EQUIPMENT REGISTRATION
# =====================================================

def register_equipment(
    equipment_name,
    category,
    location,
    quantity,
    installation_date,
    status
):
    """Register new GSM base station equipment."""

    if not str(location).strip():
        raise ValueError("Installation location is required.")

    if int(quantity) < 1:
        raise ValueError("Quantity must be at least one.")

    if status not in ["Pending", "Installed"]:
        raise ValueError("Invalid installation status.")

    equipment = load_equipment()

    new_equipment = {
        "Equipment ID": str(uuid.uuid4())[:8].upper(),
        "Equipment Name": equipment_name,
        "Category": category,
        "Location": location,
        "Quantity": int(quantity),
        "Installation Date": str(installation_date),
        "Status": status
    }

    equipment = pd.concat(
        [equipment, pd.DataFrame([new_equipment])],
        ignore_index=True
    )

    save_data(equipment, EQUIPMENT_FILE)

    return new_equipment


# =====================================================
# 5. INSTALLATION CHECKLIST
# =====================================================

def add_installation_record(
    equipment_id,
    activity,
    status,
    remarks=""
):
    """Record completion of an installation activity."""

    if status not in ["Pending", "In Progress", "Completed"]:
        raise ValueError("Invalid installation activity status.")

    equipment = load_equipment()

    if equipment_id not in equipment["Equipment ID"].values:
        raise ValueError("Equipment ID does not exist.")

    checklist = load_checklist()

    new_record = {
        "Equipment ID": equipment_id,
        "Activity": activity,
        "Status": status,
        "Remarks": remarks,
        "Date": str(date.today())
    }

    checklist = pd.concat(
        [checklist, pd.DataFrame([new_record])],
        ignore_index=True
    )

    save_data(checklist, CHECKLIST_FILE)

    return new_record


def get_installation_progress():
    """Calculate the percentage of completed recorded activities."""

    checklist = load_checklist()

    if checklist.empty:
        return 0

    completed = len(
        checklist[checklist["Status"] == "Completed"]
    )

    total = len(checklist)

    return (completed / total) * 100


# =====================================================
# 6. PREVENTIVE MAINTENANCE
# =====================================================

def schedule_maintenance(
    equipment_id,
    maintenance_activity,
    scheduled_date,
    frequency
):
    """Create a preventive maintenance schedule."""

    equipment = load_equipment()

    selected = equipment[
        equipment["Equipment ID"] == equipment_id
    ]

    if selected.empty:
        raise ValueError("Equipment ID does not exist.")

    maintenance = load_maintenance()

    new_schedule = {
        "Maintenance ID": str(uuid.uuid4())[:8].upper(),
        "Equipment ID": equipment_id,
        "Equipment Name": selected.iloc[0]["Equipment Name"],
        "Maintenance Activity": maintenance_activity,
        "Scheduled Date": str(scheduled_date),
        "Frequency": frequency,
        "Status": "Pending"
    }

    maintenance = pd.concat(
        [maintenance, pd.DataFrame([new_schedule])],
        ignore_index=True
    )

    save_data(maintenance, MAINTENANCE_FILE)

    return new_schedule


def update_maintenance_status(maintenance_id, status):
    """Update the status of a maintenance activity."""

    if status not in ["Pending", "Completed"]:
        raise ValueError("Invalid maintenance status.")

    maintenance = load_maintenance()

    if maintenance_id not in maintenance["Maintenance ID"].values:
        raise ValueError("Maintenance record does not exist.")

    maintenance.loc[
        maintenance["Maintenance ID"] == maintenance_id,
        "Status"
    ] = status

    save_data(maintenance, MAINTENANCE_FILE)


def get_overdue_maintenance():
    """Return all pending maintenance activities past their due date."""

    maintenance = load_maintenance()

    if maintenance.empty:
        return maintenance

    maintenance_dates = pd.to_datetime(
        maintenance["Scheduled Date"],
        errors="coerce"
    )

    overdue = maintenance[
        (maintenance["Status"] == "Pending") &
        (maintenance_dates.dt.date < date.today())
    ]

    return overdue


def get_upcoming_maintenance():
    """Return pending maintenance activities due today or later."""

    maintenance = load_maintenance()

    if maintenance.empty:
        return maintenance

    maintenance_dates = pd.to_datetime(
        maintenance["Scheduled Date"],
        errors="coerce"
    )

    upcoming = maintenance[
        (maintenance["Status"] == "Pending") &
        (maintenance_dates.dt.date >= date.today())
    ]

    return upcoming


# =====================================================
# 7. INSPECTION AND FAULT REPORTING
# =====================================================

def add_inspection(
    equipment_id,
    inspection_date,
    condition,
    fault_description="",
    corrective_action=""
):
    """Record equipment inspection findings."""

    if condition not in ["Good", "Fair", "Poor", "Faulty"]:
        raise ValueError("Invalid equipment condition.")

    equipment = load_equipment()

    selected = equipment[
        equipment["Equipment ID"] == equipment_id
    ]

    if selected.empty:
        raise ValueError("Equipment ID does not exist.")

    inspections = load_inspections()

    new_inspection = {
        "Inspection ID": str(uuid.uuid4())[:8].upper(),
        "Equipment ID": equipment_id,
        "Equipment Name": selected.iloc[0]["Equipment Name"],
        "Inspection Date": str(inspection_date),
        "Condition": condition,
        "Fault Description": fault_description,
        "Corrective Action": corrective_action
    }

    inspections = pd.concat(
        [inspections, pd.DataFrame([new_inspection])],
        ignore_index=True
    )

    save_data(inspections, INSPECTION_FILE)

    return new_inspection


# =====================================================
# 8. SYSTEM STATISTICS
# =====================================================

def get_dashboard_summary():
    """Calculate installation and maintenance statistics."""

    equipment = load_equipment()
    checklist = load_checklist()
    maintenance = load_maintenance()
    inspections = load_inspections()

    total_equipment = len(equipment)

    installed = (
        len(equipment[equipment["Status"] == "Installed"])
        if not equipment.empty else 0
    )

    pending = (
        len(equipment[equipment["Status"] == "Pending"])
        if not equipment.empty else 0
    )

    completed_activities = (
        len(checklist[checklist["Status"] == "Completed"])
        if not checklist.empty else 0
    )

    overdue = len(get_overdue_maintenance())

    return {
        "total_equipment": total_equipment,
        "installed_equipment": installed,
        "pending_equipment": pending,
        "completed_installation_activities": completed_activities,
        "installation_progress": get_installation_progress(),
        "overdue_maintenance": overdue,
        "total_maintenance_records": len(maintenance),
        "total_inspections": len(inspections)
    }
