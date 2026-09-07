import os
import sys
import json
import random
from datetime import datetime, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.models import (
    Department, User, UserRole, Grievance, GrievanceStatus,
    GrievanceHistory, ModelPrediction, ManualReview
)
from app.services.auth import get_password_hash
from app.services.routing import get_department_for_category
from app.services.priority import calculate_priority
from app.ml.predict import get_classifier

def seed():
    print("[*] Rebuilding database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # 1. Departments
    departments_data = [
        ("DEPT-IT", "IT & Network Services", "Campus internet, wifi, ERP, portals, systems, server room", "it-support@college.local"),
        ("DEPT-ELEC", "Electrical Maintenance", "Power grid, switchboards, lighting, fans, air conditioning, generators", "electrical-works@college.local"),
        ("DEPT-PLUMB", "Plumbing & Water Works", "Drinking water, pipelines, restrooms, drainage, overhead tanks", "plumbing-works@college.local"),
        ("DEPT-HOUSEKEEPING", "Sanitation & Housekeeping", "Classroom cleanliness, garbage clearance, restroom hygiene", "housekeeping@college.local"),
        ("DEPT-LAB", "Laboratory & Technical Infrastructure", "Lab equipment, consumables, chemicals, test apparatus, workshops", "lab-incharge@college.local"),
        ("DEPT-INFRA", "Estate & Civil Infrastructure", "Classroom furniture, windows, doors, plaster, buildings, elevators", "estate-infra@college.local"),
        ("DEPT-ACADEMIC", "Academic Affairs & Examination", "Grades, attendance records, exam schedules, hall tickets, certificates", "dean-academic@college.local"),
        ("DEPT-HOSTEL", "Hostel Administration & Dining", "Hostel rooms, mess food quality, canteen hygiene, warden operations", "hostel-warden@college.local"),
        ("DEPT-ADMIN", "General Helpdesk & Central Administration", "Cross-departmental grievances, manual review, college transport, security", "principal-office@college.local")
    ]

    dept_map = {}
    for code, name, desc, email in departments_data:
        d = Department(code=code, name=name, description=desc, contact_email=email, is_active=True)
        db.add(d)
        db.flush()
        dept_map[code] = d
    print(f"[+] Seeded {len(dept_map)} departments.")

    # 2. Users (Admin, Students)
    users_data = [
        ("admin@college.local", "Admin@123", "System Administrator", UserRole.ADMIN, dept_map["DEPT-ADMIN"].id),
        ("student@college.local", "Student@123", "Aarav Patel (Final Year CSE)", UserRole.STUDENT, None),
        ("student2@college.local", "Student@123", "Priya Nair (Third Year ECE)", UserRole.STUDENT, None),
        ("student3@college.local", "Student@123", "Rohan Mehta (Second Year Mech)", UserRole.STUDENT, None),
    ]

    user_map = {}
    for email, pwd, name, role, dept_id in users_data:
        u = User(
            email=email,
            hashed_password=get_password_hash(pwd),
            full_name=name,
            role=role,
            department_id=dept_id,
            is_active=True
        )
        db.add(u)
        db.flush()
        user_map[email] = u
    print(f"[+] Seeded {len(user_map)} users with secure bcrypt hashes.")

    # 3. Seed Grievances (~40 cases across categories, statuses, priorities)
    classifier = get_classifier()

    sample_grievances = [
        # IT / Network
        ("Wi-Fi down in CS Block 2", "The Wi-Fi in CS Department Lab 2 has stopped connecting since this morning and keeps giving DNS probe finished error.", "Resolved", 12),
        ("ERP portal throwing 500 error", "College ERP portal is throwing 500 Internal Server Error when trying to submit examination fee receipt. Today is the deadline.", "In Progress", 4),
        ("LAN port dead on bench 14", "Ethernet LAN port number 14 in computer center has no signal or link light. Need it for lab programming exam.", "Assigned", 2),
        ("Moodle LMS unreachable", "Moodle LMS server is completely unreachable from hostel network. Cannot upload assignment.", "Submitted", 1),
        ("Projector HDMI failure in Seminar Hall", "Projector in ECE Seminar Hall cannot detect HDMI signal from laptop during final year presentation.", "Resolved", 8),

        # Electrical
        ("Sparking switchboard in Room 302", "Power socket on desk 4 in Block C 3rd Floor is sparking and smells like burning plastic. Emergency safety hazard.", "In Progress", 3),
        ("Corridor tube lights flickering", "Tube light in Ground Floor Corridor is flickering violently and causing severe headache during lectures.", "Resolved", 20),
        ("Ceiling fan making screeching noise", "Ceiling fan in Block A Room 101 is making extreme grinding noise and rotating at very low speed.", "Assigned", 5),
        ("Street light dark near Boys Hostel", "Street light outside Boys Hostel Block 1 is completely dark making it unsafe to walk at night.", "Submitted", 1),
        ("AC unit blowing warm air", "Air conditioner in CS Department Lab 2 is blowing warm air and compressor is not engaging, systems overheating.", "In Progress", 6),

        # Plumbing
        ("Water pipe leakage in 3rd floor washroom", "Major water leakage from ceiling pipe in East Wing Washroom flooding the corridor floor. Slipping hazard.", "In Progress", 2),
        ("Broken flush valve in toilet", "Flush valve in toilet stall 3 of West Wing Restrooms is broken and running continuously wasting water.", "Resolved", 15),
        ("Clogged washbasin backing up", "Washbasin drain in Block B 2nd Floor is severely clogged and dirty water is backing up onto floor.", "Assigned", 4),
        ("Water cooler dispensing murky water", "Drinking water cooler near Central Library 1st Floor is dispensing murky brownish water. Unsafe to drink.", "Submitted", 1),
        ("Low water pressure in science block", "Low water pressure on top floor of Science Block Room 305, impossible to wash hands.", "Resolved", 30),

        # Cleaning / Housekeeping
        ("Unhygienic restroom condition", "Restrooms in Block A Room 101 are extremely dirty, unhygienic and lack liquid soap or paper towels.", "In Progress", 5),
        ("Overflowing trash bins near cafeteria", "Garbage bins in Main Campus Cafeteria are overflowing with food waste attracting flies and stray dogs.", "Resolved", 10),
        ("Classroom desks covered with dust", "Benches and desks in PG Block Room 402 are covered in thick layer of dust and bird droppings.", "Assigned", 2),
        ("Sticky beverage spill on corridor floor", "Spilled juice on the floor of Ground Floor Corridor has dried into sticky mess and smells bad.", "Resolved", 25),
        ("Littered stairwell in engineering block", "Corridor outside ECE Seminar Hall is littered with discarded plastic cups and wrappers.", "Submitted", 1),

        # Laboratory
        ("Oscilloscope calibration error in lab", "Digital storage oscilloscope in Robotics Lab is showing calibration error code Err-04 during experiment.", "Assigned", 3),
        ("Chemical reagents exhausted", "Chemical reagents including concentrated HCl and ethanol are out of stock in Chemical Engineering Lab.", "In Progress", 7),
        ("Microscope light source burnt", "Microscope light illumination source in Physics Lab is burnt out and slides cannot be examined.", "Resolved", 14),
        ("Fume hood exhaust malfunction", "Fume hood exhaust ventilation in Chemistry Lab is not drawing air, chemical fumes spreading in room.", "In Progress", 2),
        ("Lathe emergency stop jammed", "Lathe machine in Mechanical Workshop has a jammed emergency stop button and loose chuck key.", "Submitted", 1),

        # Infrastructure / Maintenance
        ("Exposed sharp nail on classroom desk", "Wooden desk in Block B 2nd Floor has sharp exposed nail that tore my backpack and scratched a student.", "In Progress", 4),
        ("Cracked window glass pane", "Window glass pane in Science Block Room 305 is cracked and about to fall off onto the pathway below.", "Assigned", 2),
        ("Classroom door lock jammed", "Classroom door handle in Block C 3rd Floor is jammed and students were locked inside for 20 minutes.", "Resolved", 18),
        ("Roof leaking rainwater over desks", "Roof is leaking rainwater directly over students desks in PG Block Room 402 during heavy showers.", "In Progress", 6),
        ("Elevator stuck between 2nd and 3rd floor", "Elevator in Administrative Block got stuck between floors and emergency alarm button was unresponsive.", "Resolved", 12),

        # Academic
        ("Internal marks uploaded incorrectly", "Internal assessment marks for Data Structures and Algorithms were uploaded incorrectly on student portal.", "In Progress", 5),
        ("Timetable clash for electives", "Timetable clash between elective course Machine Learning and core subject lecture on Monday.", "Resolved", 16),
        ("Attendance shortage glitch in portal", "Attendance percentage in portal dropped by 15 percent due to system glitch after server update.", "Assigned", 3),
        ("Hall ticket generation fee due error", "Examination hall ticket is not generating on college portal showing fee due despite full fee clearance.", "Submitted", 1),
        ("Revaluation result delay", "Revaluation results for odd semester Operating Systems examination have not been published after two months.", "In Progress", 8),

        # Hostel / Canteen
        ("Worms found in mess dinner curry", "Dead insect / worm found inside vegetable curry served in Hostel Mess Hall during dinner. Food safety hazard.", "In Progress", 2),
        ("Canteen vendor overcharging MRP", "Canteen vendor is charging higher than MRP on packaged drinking water and biscuits in cafeteria.", "Resolved", 22),
        ("Hostel laundry washing machine broken", "Commercial washing machine in Boys Hostel Block 1 laundry room is giving error code and tearing clothes.", "Assigned", 4),
        ("Hostel room door latch defective", "Hostel room 108 door lock is defective and cannot be locked from outside, risk of theft.", "Submitted", 1),
        ("Drinking water filter metallic taste", "Drinking water filtration unit in Girls Hostel Block 2 has not replaced carbon filters and water tastes metallic.", "Resolved", 15),

        # 4 Explicit Low-Confidence / Ambiguous Grievances for Manual Review
        ("Need clarification on campus regulations", "Could someone provide me details regarding the dress code and general library entry regulations during weekends?", "Submitted", 1),
        ("Lost blue backpack in campus area", "Lost my blue backpack with study notes and water bottle near the sports ground yesterday evening. Please help me locate it.", "Submitted", 2),
        ("Bus route timing modification issue", "College bus route 12 arrived 30 minutes later than usual schedule today, please look into this transit problem.", "Submitted", 3),
        ("General enquiry regarding cultural club budget", "We need official clarification on funding allocation and sports council approvals for the upcoming inter-college summit.", "Submitted", 4),
    ]

    students = [user_map["student@college.local"]]

    seeded_count = 0
    for idx, (title, desc, target_status, days_ago) in enumerate(sample_grievances, start=1):
        stud = students[(idx - 1) % len(students)]
        base_time = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(1, 10))

        # Check if this is one of our deliberate low-confidence cases
        is_deliberate_low_conf = "clarification on campus" in title.lower() or "lost blue backpack" in title.lower() or "bus route timing" in title.lower() or "cultural club" in title.lower()

        pred_res = classifier.predict(desc)
        if is_deliberate_low_conf:
            # Enforce low confidence characteristics
            cat = "Other / Manual Review"
            is_low_conf = True
            raw_conf = 0.42
            raw_cat = pred_res["raw_predicted_category"]
        else:
            cat = pred_res["predicted_category"]
            is_low_conf = pred_res["is_low_confidence"]
            raw_conf = pred_res["raw_confidence"]
            raw_cat = pred_res["raw_predicted_category"]

        dept = get_department_for_category(cat, db)
        prio, prio_reason = calculate_priority(desc, cat)
        ticket_num = f"GRV-2026-{idx:04d}"

        updated_time = base_time + timedelta(hours=random.randint(2, 24)) if target_status in ["In Progress", "Resolved", "Closed"] else base_time

        g = Grievance(
            ticket_number=ticket_num,
            student_id=stud.id,
            title=title,
            description=desc,
            category=cat,
            department_id=dept.id,
            priority=prio,
            priority_reason=prio_reason,
            status=target_status,
            is_low_confidence=is_low_conf,
            resolution_remarks=f"Action taken and verified by {dept.name} maintenance team." if target_status == "Resolved" else None,
            created_at=base_time,
            updated_at=updated_time
        )
        db.add(g)
        db.flush()

        # Model prediction
        top_preds = pred_res["top_predictions"]
        mp = ModelPrediction(
            grievance_id=g.id,
            predicted_category=cat,
            confidence_score=raw_conf if not is_low_conf else 0.45,
            is_fallback=is_low_conf,
            raw_predicted_category=raw_cat,
            raw_confidence=raw_conf,
            top_classes_json=json.dumps(top_preds),
            raw_text_cleaned=pred_res["cleaned_text"],
            inference_time_ms=random.uniform(4.5, 12.8),
            created_at=base_time
        )
        db.add(mp)

        # If low-confidence, create pending manual review record
        if is_low_conf:
            mr = ManualReview(
                grievance_id=g.id,
                original_category=raw_cat,
                status="pending",
                review_notes=f"Prediction confidence ({raw_conf:.2f}) is below the required 0.70 threshold. Triage required.",
                created_at=base_time
            )
            db.add(mr)

        # Audit History
        h1 = GrievanceHistory(
            grievance_id=g.id,
            changed_by_user_id=stud.id,
            previous_status=None,
            new_status=GrievanceStatus.SUBMITTED,
            remarks=f"Ticket submitted by {stud.full_name}. AI classified as '{cat}' (Confidence: {raw_conf:.2f}).",
            created_at=base_time
        )
        db.add(h1)

        admin_user = user_map["admin@college.local"]

        if target_status in ["Assigned", "In Progress", "Resolved", "Closed"]:
            h2 = GrievanceHistory(
                grievance_id=g.id,
                changed_by_user_id=admin_user.id,
                previous_status=GrievanceStatus.SUBMITTED,
                new_status=GrievanceStatus.ASSIGNED,
                remarks=f"Ticket reviewed by Admin and assigned to {dept.name}.",
                created_at=base_time + timedelta(hours=1)
            )
            db.add(h2)

        if target_status in ["In Progress", "Resolved", "Closed"]:
            h3 = GrievanceHistory(
                grievance_id=g.id,
                changed_by_user_id=admin_user.id,
                previous_status=GrievanceStatus.ASSIGNED,
                new_status=GrievanceStatus.IN_PROGRESS,
                remarks=f"Work coordinated with {dept.name}; repair in active progress.",
                created_at=base_time + timedelta(hours=3)
            )
            db.add(h3)

        if target_status in ["Resolved", "Closed"]:
            h4 = GrievanceHistory(
                grievance_id=g.id,
                changed_by_user_id=admin_user.id,
                previous_status=GrievanceStatus.IN_PROGRESS,
                new_status=GrievanceStatus.RESOLVED,
                remarks=f"Issue inspected, resolved, and verified by Central Admin.",
                created_at=updated_time
            )
            db.add(h4)

        seeded_count += 1

    db.commit()
    db.close()
    print(f"[+] Successfully seeded {seeded_count} realistic demo grievances with history and predictions.")

if __name__ == "__main__":
    seed()
