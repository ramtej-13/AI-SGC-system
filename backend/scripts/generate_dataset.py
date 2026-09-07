import os
import csv
import random

random.seed(42)

CATEGORIES = [
    "IT / Network",
    "Electrical",
    "Plumbing",
    "Cleaning / Housekeeping",
    "Laboratory",
    "Infrastructure / Maintenance",
    "Academic",
    "Hostel / Canteen",
    "Other / Manual Review"
]

TEMPLATES = {
    "IT / Network": [
        "The Wi-Fi in {location} is completely disconnected and throwing DNS probe errors since morning.",
        "Wi-Fi is not working in our CSE lab.",
        "The Wi-Fi connection in our CSE lab has stopped working since morning.",
        "Unable to connect to campus wifi in {location}, captive portal page keeps timing out.",
        "wifi not working in lab.",
        "wifi is very slow in {location}.",
        "internet gone in cse lab.",
        "college portal not opening on our systems.",
        "network keeps disconnecting during online coding assessment.",
        "Ethernet LAN port number {num} at {location} has no signal or link light.",
        "Internet speed is terribly slow in {location}, ping is over 800ms and cannot download study materials.",
        "The computers in our laboratory suddenly lost access to the internet.",
        "The college ERP portal is throwing 500 Internal Server Error when trying to submit fee receipt.",
        "Moodle LMS server is down or unreachable from hostel network.",
        "Projector in {location} cannot detect HDMI signal from laptop during seminar presentation.",
        "Printer in computer center {location} is jammed and showing offline status on network.",
        "Eduroam authentication fails repeatedly with bad credentials error even after password reset.",
        "Firewall is blocking access to academic research paper repositories and IEEE Xplore.",
        "Lab system {num} in {location} has IP address conflict and cannot access intranet.",
        "Cannot access university email account, getting unauthorized access error.",
        "Cyber security certificate error showing on campus intranet portal in browser.",
        "CSE lab systems are unable to clone github repositories due to proxy timeout.",
        "Slow network connectivity across the computer center systems.",
        "Campus broadband router in {location} keeps rebooting constantly.",
        "Students unable to login to the campus portal due to authentication gateway timeout.",
        "WLAN signal strength in {location} is very poor, signal dropping every minute.",
        "Network switch in server rack is blinking red and all connected desktop systems are offline.",
        "Domain name resolution DNS failure when opening official university examination website.",
        "LAN cable connector is damaged at workstation {num} in computer lab.",
        "Static IP allocation issue on desktop machines in room {num}."
    ],
    "Electrical": [
        "The classroom fan is not working.",
        "The fan in room {num} has stopped working.",
        "The fan in room 203 is not working.",
        "The ceiling fan in room 305 has stopped working.",
        "The classroom lights are not working.",
        "Ceiling fan in {location} is making extreme grinding noise and rotating at very low speed.",
        "Tube light in {location} is flickering violently and causing severe headache during lectures.",
        "Power socket on desk {num} in {location} is sparking and smells like burning plastic.",
        "Sudden power outage in {location}, MCB breaker seems to have tripped.",
        "Air conditioner in {location} is blowing warm air and compressor is not engaging.",
        "Switchboard on the wall of {location} is loose and exposed live wires are visible.",
        "Street light outside {location} is completely dark making it unsafe to walk at night.",
        "Voltage fluctuations in {location} caused desktop monitors to shut down abruptly.",
        "Exhaust fan in {location} has stopped running and room is becoming suffocating.",
        "Extension board provided in {location} has a melted plug point.",
        "Main switch lever in {location} feels hot to touch and needs immediate electrician inspection.",
        "Short circuit happened near the water cooler power outlet at {location}.",
        "Cooling unit in {location} is leaking electric current when touched.",
        "Frequent power tripping in {location} whenever heavy electrical load is turned on.",
        "Three tube lights are fused and completely dead in lecture hall {location}.",
        "Electrical hazard: loose electrical cable hanging from the false ceiling in {location}.",
        "Wall socket is loose and throwing sparks whenever plug is inserted in {location}.",
        "The regulator for fan number {num} is broken and fan is stuck at maximum speed.",
        "Classroom projector power supply cable is damaged and power is cutting out.",
        "Power points near back benches in room {num} have no voltage output.",
        "Emergency backup inverter power is not kicking in during electricity cuts in {location}.",
        "Electrical distribution panel on 2nd floor is making loud buzzing sound.",
        "AC thermostat in seminar room {location} is malfunctioning and room is freezing cold.",
        "Exposed wiring near doorway of {location} requires urgent insulating tape and repair."
    ],
    "Plumbing": [
        "Water is leaking from the washroom tap.",
        "The washroom tap near block B is leaking.",
        "The tap near the second floor washroom is continuously leaking.",
        "Water has been continuously dripping from the bathroom faucet.",
        "Water tap on 2nd floor of {location} is broken and spraying water with high pressure.",
        "Major water leakage from ceiling pipe in {location} flooding the corridor floor.",
        "Flush valve in toilet stall {num} of {location} is broken and running continuously.",
        "Washbasin drain in {location} is severely clogged and dirty water is backing up.",
        "No running water available in {location} washrooms since early morning.",
        "Drinking water cooler near {location} is dispensing murky brownish water.",
        "Foul sewage smell rising from floor drainage trap in {location}.",
        "Water pipe joint burst near {location}, water pooling all over the pathway.",
        "Low water pressure on top floor of {location}, impossible to wash hands.",
        "Geyser in {location} is leaking water from the bottom valve onto floor.",
        "Hostel bathroom tap handle snapped off and water cannot be turned off.",
        "Urinal sensor valve in {location} is jammed open and wasting gallons of water.",
        "Septic line overflow noticed near back exit of {location}.",
        "Cold drinking water dispenser in {location} has broken push button and leaks constantly.",
        "Washroom drainage line is blocked causing stagnant water on the floor in {location}.",
        "Broken PVC water pipe behind the canteen is spilling freshwater continuously.",
        "Overhead water tank in {location} is overflowing and cascading down the building facade.",
        "Restroom taps have zero water flow, whole floor is facing severe water shortage.",
        "Water filter tap is loose and dripping constantly in the corridor of {location}.",
        "Sewer pipe leaking foul smelling wastewater near the entrance of {location}.",
        "Plumbing valve under sink {num} is cracked and leaking water under the counter."
    ],
    "Cleaning / Housekeeping": [
        "Restrooms in {location} are extremely dirty, unhygienic and lack liquid soap or paper towels.",
        "Garbage bins in {location} are overflowing with food waste attracting flies and stray dogs.",
        "Benches and desks in {location} are covered in thick layer of dust and bird droppings.",
        "Spilled juice / beverage on the floor of {location} has dried into sticky mess and smells bad.",
        "Cobwebs and accumulated debris along the ceiling corners of {location} have not been cleaned for weeks.",
        "Classroom {location} blackboard is completely smudged and no clean duster or chalk available.",
        "Sanitation staff has not visited {location} for the past three days.",
        "Corridor outside {location} is littered with discarded plastic cups and wrappers.",
        "Staircase leading to {location} has stagnant puddles of dirty mop water.",
        "Hand sanitizer dispensers in {location} are all empty and broken.",
        "Floor in {location} is muddy and requires immediate wet scrubbing.",
        "Waste disposal bins outside {location} have been tipped over by stray animals.",
        "Window glass panes in {location} are stained with grime and blocking daylight.",
        "Classroom floor is strewn with torn papers and biscuit wrappers after afternoon class.",
        "Dustbins in the hallway of {location} have not been emptied since yesterday.",
        "Foul smell in lecture hall {num} because food leftovers were dumped in corner bin.",
        "Spider webs and dirt accumulated behind the classroom podium in {location}.",
        "Housekeeping is neglected in {location}, floors need sweeping and mopping urgently.",
        "Toilet seats in {location} are stained and unwashed.",
        "Broken glass pieces on corridor floor in {location} need immediate cleaning."
    ],
    "Laboratory": [
        "Digital storage oscilloscope in {location} is showing calibration error code Err-04.",
        "Microscope light illumination source in {location} is burnt out and slides cannot be examined.",
        "Chemical reagents including concentrated HCl and ethanol are out of stock in {location}.",
        "Fume hood exhaust ventilation in {location} is not drawing air, chemical fumes spreading in room.",
        "Precision micro-pipettes in {location} are uncalibrated and giving erratic volume measurements.",
        "Lathe machine in {location} has a jammed emergency stop button and loose chuck key.",
        "FPGA development board in {location} fails to configure via JTAG USB interface.",
        "3D printer in {location} has clogged extruder nozzle and heating element failure.",
        "Vernier calipers and screw gauges in {location} have severe zero-error and damaged jaws.",
        "Bunsen burner gas nozzle in {location} has gas leak near tubing connector.",
        "Centrifuge machine in {location} vibrates dangerously at speeds above 2000 RPM.",
        "Analytical weighing balance in {location} drift error exceeds 50mg, calibration weights missing.",
        "PCB etching tank heater in {location} is broken and etching solution is cold.",
        "Multimeter probes in electrical machine workbench {num} are frayed and broken.",
        "Spectrophotometer optical sensor in {location} is failing self-test diagnostic.",
        "Microbiology incubator temperature controller is erratic, ruining bacterial cultures in {location}.",
        "Hydraulics test bench pressure gauge is stuck at zero despite pump running in {location}.",
        "Microcontroller development kits are missing USB connection cables in {location}.",
        "Glassware including burettes and volumetric flasks are cracked in {location}.",
        "Lab apparatus table {num} has broken clamp stands and missing test tube holders."
    ],
    "Infrastructure / Maintenance": [
        "Wooden desk in {location} has sharp exposed nail that tore my backpack and scratched a student.",
        "Window glass pane in {location} is cracked and about to fall off onto the pathway below.",
        "Classroom door handle in {location} is jammed and students were locked inside for 20 minutes.",
        "Plaster chunks from ceiling in {location} fell down during class; serious safety hazard.",
        "Floor tiles in {location} are cracked, uneven and loose, causing students to trip.",
        "Handrail on staircase near {location} is shaky and detached from concrete wall.",
        "Elevator in {location} got stuck between floors and emergency alarm button was unresponsive.",
        "Roof is leaking rainwater directly over students desks in {location}.",
        "Auditorium acoustic wall panel in {location} is hanging loose and likely to collapse.",
        "Whiteboard surface in {location} is peeling off and markers cannot be erased.",
        "Main entrance door glass of {location} is shattered and edges are taped with scotch tape.",
        "Notice board glass shutter in {location} is broken with sharp jagged shards exposed.",
        "Curtain rods in seminar hall {location} fell down during guest lecture.",
        "Broken bench wooden planks in classroom {num} making it unusable.",
        "Classroom door hinges are completely broken and door cannot be closed properly.",
        "Wall plaster peeling off in large sheets inside lecture hall {location}.",
        "False ceiling tiles have fallen down in the corridor of {location}.",
        "Staircase steps are broken and cracked near 3rd floor landing.",
        "Podium in seminar room {location} has broken wheels and tilted surface."
    ],
    "Academic": [
        "Semester grade sheet shows absent for Subject Code CS{num} although I signed the attendance sheet.",
        "Internal assessment marks for {subject} were uploaded incorrectly on student portal.",
        "Timetable clash between elective course {subject} and core subject lecture on Monday.",
        "Attendance percentage in portal dropped by 15 percent due to system glitch after server update.",
        "Faculty assigned for {subject} did not conduct scheduled tutorial classes for three weeks.",
        "Course syllabus for {subject} is only 40 percent complete with end semester exams starting next week.",
        "Examination hall ticket is not generating on college portal showing fee due despite full fee clearance.",
        "Revaluation results for odd semester {subject} examination have not been published after two months.",
        "Library system charged Rs {num} overdue fine for book returned before due date; librarian refusing waiver.",
        "Bonafide and character certificate request submitted on portal has been pending for three weeks.",
        "Lab exam schedule overlaps with competitive examination GATE slot.",
        "Credit calculation error in final degree audit for batch {num}.",
        "Course registration portal timed out while selecting open electives, assigning unwanted course automatically.",
        "Professor did not return midterm answer scripts for review before submitting final internals.",
        "Subject elective change request form was submitted before deadline but rejected without explanation.",
        "Clash in final examination schedule between two backlog subjects on the same date.",
        "College academic calendar does not account for mandatory national internship dates."
    ],
    "Hostel / Canteen": [
        "Dead insect / worm found inside vegetable curry served in {location} during dinner.",
        "Food served in {location} is stale, lukewarm and multiple students have fallen sick with food poisoning.",
        "Canteen vendor is charging higher than MRP on packaged drinking water and biscuits.",
        "Drinking water filtration unit in {location} has not replaced carbon filters and water tastes metallic.",
        "Hostel mess menu is not being followed and nutritional protein items are consistently skipped.",
        "Loud music and shouting in room {num} of {location} past midnight disturbing quiet study hours.",
        "Hostel warden is not allocating allotted room {num} despite verified fee receipt.",
        "Commercial washing machine in {location} laundry room is giving error code and tearing clothes.",
        "Uncooked rice and contaminated dal served in {location} lunch session.",
        "Hostel room {num} door lock is defective and cannot be locked from outside.",
        "Stray dogs roaming freely inside {location} dining hall posing rabies threat to hostelers.",
        "Canteen staff handling food items without hairnets or gloves in unhygienic conditions.",
        "Hot water supply in hostel {location} has been discontinued without prior announcement.",
        "Mess food quality has deteriorated severely with oily food and undercooked chapattis.",
        "Breakfast served in hostel canteen was cold and milk was curdled and sour.",
        "Hostel room {num} window mesh is torn allowing swarms of mosquitoes inside.",
        "Drinking water cooler in hostel mess is uncleaned and emitting foul odor."
    ],
    "Other / Manual Review": [
        "I have a general question regarding college timing changes next semester.",
        "Lost my college ID card somewhere near the sports ground, please help find it.",
        "College bus route {num} arrives 25 minutes late every morning causing students to miss first hour.",
        "Campus parking lot is overflowing with two-wheelers and bicycles are getting damaged.",
        "Need permission from principal to put up a poster for cultural fest club activity.",
        "Everything in this college needs improvement, please take immediate action.",
        "Query regarding bus pass renewal procedure for students residing in outer suburbs.",
        "Someone took my notebook from the reading table in Central Library.",
        "I want to request scholarship inquiry contact details for state government scheme.",
        "General complaint about campus security guards speaking rudely at the entrance gate.",
        "Can someone explain the procedure to apply for duplicate mark sheet from university?",
        "Please help me with an issue I am facing, contact me as soon as possible.",
        "Lost my black laptop bag with scientific calculator in college premises yesterday.",
        "Inquiry regarding gym membership fee and badminton court booking slots.",
        "Something seems very weird and strange in life.",
        "Unclear request about college policies and general inquiries.",
        "Please look into the matter as discussed over phone.",
        "Random student inquiry without specific department or clear grievance details."
    ]
}

LOCATIONS = [
    "Block A Room 101", "Block B 2nd Floor", "Block C 3rd Floor", "CS Department",
    "ECE Seminar Hall", "Mechanical Block", "Civil Dept Hall",
    "Central Library 1st Floor", "Boys Hostel Block 1", "Girls Hostel Block 2", "Main Campus Cafeteria",
    "Science Block Room 305", "Auditorium Annex", "Ground Floor Corridor", "East Wing Washroom",
    "West Wing Restrooms", "PG Block Room 402", "Administrative Block",
    "Robotics Center", "Physics Department", "Hostel Mess Hall", "Sports Complex"
]

SUBJECTS = [
    "Data Structures and Algorithms", "Operating Systems", "Computer Networks", "Database Management Systems",
    "Theory of Computation", "Machine Learning", "Microprocessors and Microcontrollers", "Digital Signal Processing",
    "VLSI Design", "Fluid Mechanics", "Thermodynamics", "Structural Analysis", "Organic Chemistry",
    "Software Engineering", "Artificial Intelligence"
]

def introduce_variations(text):
    transforms = [
        ("Wi-Fi", random.choice(["wifi", "wi-fi", "WIFI", "internet wifi", "net"])),
        ("WiFi", random.choice(["wifi", "wi-fi", "WIFI"])),
        ("LMS", random.choice(["lms", "moodle", "online portal"])),
        ("ERP", random.choice(["erp", "college portal", "erp site"])),
        ("computer", random.choice(["pc", "system", "computer"])),
        ("Air conditioner", random.choice(["AC", "A/C", "air conditioner", "ac unit"])),
        ("washroom", random.choice(["toilet", "restroom", "washroom", "bathroom"])),
        ("washrooms", random.choice(["toilets", "restrooms", "washrooms", "bathrooms"])),
        ("cafeteria", random.choice(["canteen", "cafeteria", "mess"])),
        ("urgent", random.choice(["urgent", "asap", "emergency", "immediately"])),
        ("please", random.choice(["pls", "plz", "please", "kindly"])),
    ]
    for orig, repl in transforms:
        if random.random() < 0.35 and orig in text:
            text = text.replace(orig, repl)
    
    if random.random() < 0.12:
        typos = [("problem", "problm"), ("working", "wrking"), ("broken", "brokn"),
                 ("complaint", "complnt"), ("service", "servce"), ("request", "reqst")]
        for good, bad in typos:
            if good in text:
                text = text.replace(good, bad)
                break
    return text

def generate_records():
    records = []
    # 140 per category = 9 * 140 = 1260 records
    target_per_cat = 140
    
    for cat in CATEGORIES:
        tmpl_list = TEMPLATES[cat]
        count = 0
        while count < target_per_cat:
            t = random.choice(tmpl_list)
            loc = random.choice(LOCATIONS)
            subj = random.choice(SUBJECTS)
            num = str(random.randint(101, 599))
            
            # Format
            text = t.format(location=loc, subject=subj, num=num)
            
            # Optional prefix or suffix for diversity
            prefix = random.choice([
                "", "Sir, ", "Respected admin, ", "Hello, ", "Reporting that ", "Complaint: ",
                "Urgent issue: ", "Notice: ", "Student grievance: ", "Dear Sir/Madam, "
            ]) if random.random() < 0.35 else ""
            
            suffix = random.choice([
                "", " Please resolve this as soon as possible.", " Kindly look into this matter immediately.",
                " It has been like this for two days.", " Affecting our daily study.", " Thanks.",
                " Please send technician.", " Urgent attention required."
            ]) if random.random() < 0.35 else ""
            
            full_text = introduce_variations((prefix + text + suffix).strip())
            records.append((full_text, cat))
            count += 1
            
    random.shuffle(records)
    return records

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "grievances.csv")
    
    records = generate_records()
    
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category"])
        for r in records:
            writer.writerow(r)
            
    print(f"Generated {len(records)} grievances across {len(CATEGORIES)} categories into {output_csv}")

if __name__ == "__main__":
    main()
