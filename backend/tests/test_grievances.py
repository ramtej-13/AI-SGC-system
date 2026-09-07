import pytest

def test_submit_grievance_success(client, student_auth_headers):
    payload = {
        "title": "Wi-Fi connection down in CS lab",
        "description": "The campus Wi-Fi network in CS Department Lab 2 has been disconnected all morning with DNS probe error."
    }
    response = client.post("/api/grievances", json=payload, headers=student_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_number"].startswith("GRV-")
    assert data["category"] == "IT / Network"
    assert data["department_code"] == "DEPT-IT"
    assert data["prediction"] is not None
    assert len(data["prediction"]["top_predictions"]) == 3
    assert data["prediction"]["confidence_score"] > 0
    assert len(data["history"]) >= 1

def test_submit_grievance_validation_error(client, student_auth_headers):
    # Too short description (< 10 chars)
    payload = {
        "title": "Short title",
        "description": "Too short"
    }
    response = client.post("/api/grievances", json=payload, headers=student_auth_headers)
    assert response.status_code == 422

def test_get_my_grievances(client, student_auth_headers):
    response = client.get("/api/grievances/my", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_rbac_student_isolation(client, student_auth_headers, student2_auth_headers):
    # Student 1 creates grievance
    payload = {
        "title": "Student 1 private grievance",
        "description": "Private issue description submitted by student 1 regarding lab equipment."
    }
    resp1 = client.post("/api/grievances", json=payload, headers=student_auth_headers)
    g_id = resp1.json()["id"]

    # Student 2 attempts to read Student 1's grievance -> 403 Forbidden
    resp2 = client.get(f"/api/grievances/{g_id}", headers=student2_auth_headers)
    assert resp2.status_code == 403

def test_admin_department_queue_filtering(client, student_auth_headers, admin_auth_headers):
    # Submit an IT grievance
    client.post("/api/grievances", json={
        "title": "Ethernet port dead in computer center",
        "description": "Ethernet LAN port number 12 in computer center has no signal or link light."
    }, headers=student_auth_headers)

    # Admin filters department queue for IT Department
    resp_it = client.get("/api/admin/grievances?category=IT%20%2F%20Network", headers=admin_auth_headers)
    assert resp_it.status_code == 200
    it_list = resp_it.json()
    assert all(g["department_code"] == "DEPT-IT" for g in it_list)

def test_admin_status_update_and_history(client, student_auth_headers, admin_auth_headers):
    # Submit IT grievance
    resp = client.post("/api/grievances", json={
        "title": "Firewall blocking research server",
        "description": "Firewall is blocking access to academic research paper repositories and IEEE Xplore."
    }, headers=student_auth_headers)
    g_id = resp.json()["id"]

    # Admin updates status to In Progress
    update_resp = client.patch(
        f"/api/grievances/{g_id}/status",
        json={"status": "In Progress", "remarks": "Technician assigned to inspect firewall whitelist"},
        headers=admin_auth_headers
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "In Progress"
    assert any(h["new_status"] == "In Progress" for h in data["history"])

    # Admin updates status to Resolved
    resolve_resp = client.patch(
        f"/api/grievances/{g_id}/status",
        json={"status": "Resolved", "remarks": "Domain whitelisted on gateway proxy"},
        headers=admin_auth_headers
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "Resolved"

def test_admin_endpoints(client, admin_auth_headers):
    # 1. Admin analytics
    analytics_resp = client.get("/api/admin/analytics", headers=admin_auth_headers)
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert "total_grievances" in analytics
    assert "status_distribution" in analytics

    # 2. Model performance metadata
    perf_resp = client.get("/api/admin/model-performance", headers=admin_auth_headers)
    assert perf_resp.status_code == 200
    perf = perf_resp.json()
    assert "evaluation_metrics" in perf
    assert "confusion_matrix" in perf

    # 3. Model live test endpoint
    test_resp = client.post(
        "/api/admin/model-test",
        json={"text": "Water is leaking from the flush valve in the 2nd floor bathroom.", "threshold": 0.70},
        headers=admin_auth_headers
    )
    assert test_resp.status_code == 200
    test_data = test_resp.json()
    assert test_data["predicted_category"] == "Plumbing"
    assert "suggested_department" in test_data
    assert "suggested_priority" in test_data

def test_admin_view_all_grievances(client, admin_auth_headers):
    resp = client.get("/api/admin/grievances", headers=admin_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

def test_duplicate_status_update_rejected(client, student_auth_headers, admin_auth_headers):
    # Submit grievance
    resp = client.post("/api/grievances", json={
        "title": "Lab equipment calibration failed",
        "description": "Digital multimeter and oscilloscope calibration failed in analog electronics lab."
    }, headers=student_auth_headers)
    g_id = resp.json()["id"]

    # First update: Submitted -> In Progress
    up_resp = client.patch(
        f"/api/grievances/{g_id}/status",
        json={"status": "In Progress", "remarks": "Assigned technician"},
        headers=admin_auth_headers
    )
    assert up_resp.status_code == 200

    # Duplicate update: In Progress -> In Progress -> 400 Bad Request
    dup_resp = client.patch(
        f"/api/grievances/{g_id}/status",
        json={"status": "In Progress", "remarks": "Trying again"},
        headers=admin_auth_headers
    )
    assert dup_resp.status_code == 400
    assert "already in 'In Progress' status" in dup_resp.json()["detail"]

def test_manual_review_history_records_correct_previous_status(client, student_auth_headers, admin_auth_headers):
    # Submit an ambiguous query to trigger low confidence / manual review
    resp = client.post("/api/grievances", json={
        "title": "Unclear lost item query",
        "description": "Lost my blue umbrella somewhere near the campus main entrance gate."
    }, headers=student_auth_headers)
    g_data = resp.json()
    g_id = g_data["id"]
    assert g_data["status"] == "Submitted"

    # Admin resolves manual review: assigns to Estate & Civil Infrastructure
    review_resp = client.post(
        f"/api/admin/manual-review/{g_id}",
        json={
            "assigned_category": "Infrastructure / Maintenance",
            "review_notes": "Reviewed and re-routed to estate security desk"
        },
        headers=admin_auth_headers
    )
    assert review_resp.status_code == 200
    updated_g = review_resp.json()
    assert updated_g["status"] == "Assigned"
    assert updated_g["category"] == "Infrastructure / Maintenance"

    # Verify history captures previous_status == 'Submitted' (NOT 'Assigned')
    history = updated_g["history"]
    review_hist = next(h for h in history if "Manual review completed" in (h["remarks"] or ""))
    assert review_hist["previous_status"] == "Submitted"
    assert review_hist["new_status"] == "Assigned"
    assert "Infrastructure / Maintenance" in review_hist["remarks"]

def test_ticket_number_uniqueness_on_deletion(client, student_auth_headers):
    # Create two grievances
    r1 = client.post("/api/grievances", json={
        "title": "First ticket for uniqueness test",
        "description": "Checking that sequential ticket generation produces unique numbers."
    }, headers=student_auth_headers)
    t1 = r1.json()["ticket_number"]

    r2 = client.post("/api/grievances", json={
        "title": "Second ticket for uniqueness test",
        "description": "Checking second ticket generation sequential uniqueness."
    }, headers=student_auth_headers)
    t2 = r2.json()["ticket_number"]

    assert t1 != t2
    num1 = int(t1.split("-")[-1])
    num2 = int(t2.split("-")[-1])
    assert num2 > num1
