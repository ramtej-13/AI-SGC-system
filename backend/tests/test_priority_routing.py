import pytest
from app.services.priority import calculate_priority
from app.services.routing import route_category_to_department_code

def test_priority_high_safety_keywords():
    # Sparking / Fire
    prio, reason = calculate_priority("The switchboard is sparking and throwing fire sparks")
    assert prio == "High"
    assert "Critical" in reason

    # Stuck in elevator
    prio, reason = calculate_priority("Students are stuck in elevator on 2nd floor")
    assert prio == "High"

    # Food poisoning
    prio, reason = calculate_priority("Multiple students got severe food poisoning after dinner")
    assert prio == "High"

def test_priority_medium_operational_keywords():
    # Leaking water
    prio, reason = calculate_priority("Water pipe is leaking in the washroom")
    assert prio == "Medium"
    assert "Operational" in reason

    # Wifi down
    prio, reason = calculate_priority("The wifi down in the library")
    assert prio == "Medium"

def test_priority_low_default():
    prio, reason = calculate_priority("I have a general enquiry regarding sports equipment")
    assert prio == "Low"

def test_routing_all_categories():
    assert route_category_to_department_code("IT / Network") == "DEPT-IT"
    assert route_category_to_department_code("Electrical") == "DEPT-ELEC"
    assert route_category_to_department_code("Plumbing") == "DEPT-PLUMB"
    assert route_category_to_department_code("Cleaning / Housekeeping") == "DEPT-HOUSEKEEPING"
    assert route_category_to_department_code("Laboratory") == "DEPT-LAB"
    assert route_category_to_department_code("Infrastructure / Maintenance") == "DEPT-INFRA"
    assert route_category_to_department_code("Academic") == "DEPT-ACADEMIC"
    assert route_category_to_department_code("Hostel / Canteen") == "DEPT-HOSTEL"
    assert route_category_to_department_code("Other / Manual Review") == "DEPT-ADMIN"
    assert route_category_to_department_code("Unknown Category") == "DEPT-ADMIN"
