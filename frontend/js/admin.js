/**
 * Admin Panel Manager & Interactive CRUD Operations
 * Connects all Admin views to the REST API with dynamic Modals, Toast alerts, and Search Filters.
 */

let departmentsList = [];
let sectionsList = [];
let subjectsList = [];
let facultyList = [];

let allRoomsList = [];
let allLabsList = [];

function formatYear(yr) {
  const map = { 1: "FY", 2: "SY", 3: "TY", 4: "BTech" };
  return map[yr] || `Yr ${yr}`;
}

document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireRole("ADMIN");

  // Pre-load common metadata
  await loadMetadata();

  const path = window.location.pathname;
  if (path.includes("dashboard.html")) {
    loadDashboardStats();
  } else if (path.includes("students.html") || path.includes("student.html")) {
    loadStudents();
  } else if (path.includes("faculty.html")) {
    loadFaculty();
  } else if (path.includes("subjects.html")) {
    loadSubjects();
  } else if (path.includes("resources.html")) {
    loadResources();
  } else if (path.includes("assignments.html")) {
    loadAssignments();
  }
});

async function loadMetadata() {
  try {
    const deptRes = await api.get("/api/departments");
    if (deptRes.success) departmentsList = deptRes.departments || [];
    const secRes = await api.get("/api/sections");
    if (secRes.success) sectionsList = secRes.sections || [];
    const subRes = await api.get("/api/subjects");
    if (subRes.success) subjectsList = subRes.subjects || [];
    const facRes = await api.get("/api/faculty");
    if (facRes.success) facultyList = facRes.faculty || [];
  } catch (err) {
    console.error("Failed to load metadata", err);
  }
}

// -----------------------------------------------------------------------------
// Modal Control Utilities
// -----------------------------------------------------------------------------
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("open");
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove("open");
}

// -----------------------------------------------------------------------------
// Dashboard Statistics & Overview
// -----------------------------------------------------------------------------
async function loadDashboardStats() {
  const res = await api.get("/api/admin/stats");
  if (res.success) {
    if (document.getElementById("stat-students")) document.getElementById("stat-students").textContent = res.stats.students;
    if (document.getElementById("stat-faculty")) document.getElementById("stat-faculty").textContent = res.stats.faculty;
    if (document.getElementById("stat-subjects")) document.getElementById("stat-subjects").textContent = res.stats.subjects;
    if (document.getElementById("stat-rooms")) document.getElementById("stat-rooms").textContent = res.stats.rooms;
    if (document.getElementById("stat-rooms-count")) document.getElementById("stat-rooms-count").textContent = res.stats.rooms;
    if (document.getElementById("stat-labs")) document.getElementById("stat-labs").textContent = res.stats.labs;
    if (document.getElementById("stat-labs-count")) document.getElementById("stat-labs-count").textContent = res.stats.labs;
  }
}

// -----------------------------------------------------------------------------
// 1. Students CRUD
// -----------------------------------------------------------------------------
let allStudents = [];

async function loadStudents() {
  const res = await api.get("/api/students");
  const tbody = document.getElementById("student-table-body");
  if (!tbody) return;

  if (res.success) {
    allStudents = res.students || [];
    populateStudentFilters();
    renderStudentsTable(allStudents);
  }
}

function renderStudentsTable(students) {
  const tbody = document.getElementById("student-table-body");
  const countEl = document.getElementById("studentTableCount");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (countEl) countEl.textContent = `${students.length} Students`;

  if (students.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding: 28px;">No students found matching your criteria.</td></tr>`;
    return;
  }

  students.forEach((s, index) => {
    tbody.innerHTML += `
      <tr>
        <td class="rollcall-no">${index + 1}</td>
        <td><strong>${s.student_code}</strong></td>
        <td>${s.name}</td>
        <td><span style="color:#64748b;">${s.email}</span></td>
        <td>${s.dept_name}</td>
        <td><span class="badge badge-neutral" style="white-space: nowrap;">${formatYear(s.academic_year)}</span></td>
        <td><span class="badge badge-ok" style="white-space: nowrap;">${s.section_name || 'Unassigned'}</span></td>
        <td class="rollcall-signature"></td>
        <td>
          <div class="action-buttons">
            <button class="btn-sm btn-edit" onclick="openEditStudentModal(${s.student_id})">Edit</button>
            <button class="btn-sm btn-danger-sm" onclick="deleteStudent(${s.student_id}, '${s.name}')">Delete</button>
          </div>
        </td>
      </tr>
    `;
  });
}

function filterStudents() {
  const query = (document.getElementById("studentSearch").value || "").toLowerCase();
  const dept = document.getElementById("studentDeptFilter") ? document.getElementById("studentDeptFilter").value : "";
  const year = document.getElementById("studentYearFilter") ? document.getElementById("studentYearFilter").value : "";
  const section = document.getElementById("studentSectionFilter") ? document.getElementById("studentSectionFilter").value : "";

  const filtered = allStudents.filter(s => {
    const matchesQuery = s.name.toLowerCase().includes(query) || 
                         s.student_code.toLowerCase().includes(query) || 
                         s.email.toLowerCase().includes(query);
    const matchesDept = !dept || s.dept_id == dept;
    const matchesYear = !year || s.academic_year == year;
    const matchesSection = !section || s.section_id == section;
    return matchesQuery && matchesDept && matchesYear && matchesSection;
  }).sort((a, b) => a.student_code.localeCompare(b.student_code));
  renderStudentsTable(filtered);
}

function populateStudentFilters() {
  const deptSelect = document.getElementById("studentDeptFilter");
  if (deptSelect) {
    const selected = deptSelect.value;
    deptSelect.innerHTML = `<option value="">All Branches</option>` +
      departmentsList.map(d => `<option value="${d.dept_id}">${d.dept_code} — ${d.dept_name}</option>`).join("");
    deptSelect.value = selected;
  }
  updateStudentDivisionFilter();
}

function updateStudentDivisionFilter() {
  const divisionSelect = document.getElementById("studentSectionFilter");
  if (!divisionSelect) return;
  const dept = document.getElementById("studentDeptFilter")?.value;
  const year = document.getElementById("studentYearFilter")?.value;
  const selected = divisionSelect.value;
  const divisions = sectionsList.filter(section =>
    (!dept || section.dept_id == dept) && (!year || section.academic_year == year)
  );
  divisionSelect.innerHTML = `<option value="">All Divisions</option>` +
    divisions.map(section => `<option value="${section.section_id}">${section.section_name}</option>`).join("");
  if (divisions.some(section => String(section.section_id) === selected)) divisionSelect.value = selected;
}

function printStudentRollCall() {
  filterStudents();
  const branch = document.getElementById("studentDeptFilter")?.selectedOptions[0]?.text || "All Branches";
  const year = document.getElementById("studentYearFilter")?.selectedOptions[0]?.text || "All Classes";
  const division = document.getElementById("studentSectionFilter")?.selectedOptions[0]?.text || "All Divisions";
  const title = document.getElementById("studentPrintTitle");
  if (title) title.textContent = `Roll Call List — ${branch} | ${year} | ${division}`;
  window.print();
}

function populateStudentDropdowns() {
  const deptSelect = document.getElementById("studentDept");
  if (deptSelect) {
    deptSelect.innerHTML = departmentsList.map(d => `<option value="${d.dept_id}">${d.dept_name} (${d.dept_code})</option>`).join('');
  }
  const secSelect = document.getElementById("studentSection");
  if (secSelect) {
    secSelect.innerHTML = `<option value="">-- Select Division (Optional) --</option>` + 
      sectionsList.map(s => `<option value="${s.section_id}">${s.section_name} (${s.dept_name})</option>`).join('');
  }
}

function openAddStudentModal() {
  populateStudentDropdowns();
  document.getElementById("studentModalTitle").textContent = "Add Student Record";
  document.getElementById("studentId").value = "";
  document.getElementById("studentName").value = "";
  document.getElementById("studentEmail").value = "";
  document.getElementById("studentCode").value = "";
  document.getElementById("studentPassword").value = "";
  document.getElementById("studentPassword").placeholder = "Default: Password123";
  document.getElementById("studentYear").value = "3";
  openModal("studentModal");
}

async function openEditStudentModal(id) {
  populateStudentDropdowns();
  const res = await api.get(`/api/students/${id}`);
  if (res.success && res.student) {
    const s = res.student;
    document.getElementById("studentModalTitle").textContent = "Edit Student Details";
    document.getElementById("studentId").value = s.student_id;
    document.getElementById("studentName").value = s.name;
    document.getElementById("studentEmail").value = s.email;
    document.getElementById("studentCode").value = s.student_code;
    document.getElementById("studentPassword").value = "";
    document.getElementById("studentPassword").placeholder = "Leave blank to keep current";
    document.getElementById("studentDept").value = s.dept_id;
    document.getElementById("studentYear").value = s.academic_year;
    document.getElementById("studentSection").value = s.section_id || "";
    openModal("studentModal");
  }
}

async function saveStudent(event) {
  event.preventDefault();
  const id = document.getElementById("studentId").value;
  const payload = {
    name: document.getElementById("studentName").value.trim(),
    email: document.getElementById("studentEmail").value.trim(),
    student_code: document.getElementById("studentCode").value.trim(),
    dept_id: parseInt(document.getElementById("studentDept").value),
    academic_year: parseInt(document.getElementById("studentYear").value),
    section_id: document.getElementById("studentSection").value ? parseInt(document.getElementById("studentSection").value) : null,
    password: document.getElementById("studentPassword").value.trim() || undefined
  };

  let res;
  if (id) {
    res = await api.put(`/api/students/${id}`, payload);
  } else {
    res = await api.post("/api/students", payload);
  }

  if (res.success) {
    Toast.show(`Student ${payload.name} saved successfully.`, "success");
    closeModal("studentModal");
    loadStudents();
  } else {
    Toast.show("Error: " + (res.message || "Failed to save student record."), "error");
  }
}

async function deleteStudent(id, name) {
  if (confirm(`Are you sure you want to delete student "${name}"?`)) {
    const res = await api.del(`/api/students/${id}`);
    if (res.success) {
      Toast.show(`Student ${name} removed.`, "success");
      loadStudents();
    } else {
      Toast.show("Error: " + (res.message || "Failed to delete student."), "error");
    }
  }
}

// -----------------------------------------------------------------------------
// 2. Faculty CRUD
// -----------------------------------------------------------------------------
let allFaculty = [];

async function loadFaculty() {
  const res = await api.get("/api/faculty");
  const tbody = document.getElementById("faculty-table-body");
  if (!tbody) return;

  if (res.success) {
    allFaculty = res.faculty || [];
    renderFacultyTable(allFaculty);
  }
}

function renderFacultyTable(faculty) {
  const tbody = document.getElementById("faculty-table-body");
  const countEl = document.getElementById("facultyTableCount");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (countEl) countEl.textContent = `${faculty.length} Faculty Members`;

  if (faculty.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding: 28px;">No faculty members found.</td></tr>`;
    return;
  }

  faculty.forEach(f => {
    tbody.innerHTML += `
      <tr>
        <td><strong>${f.faculty_code}</strong></td>
        <td><strong>${f.name}</strong></td>
        <td><span style="color:#64748b;">${f.email}</span></td>
        <td>${f.dept_name}</td>
        <td><span class="badge badge-info">${f.designation}</span></td>
        <td>
          <div class="action-buttons">
            <button class="btn-sm btn-edit" onclick="openEditFacultyModal(${f.faculty_id})">Edit</button>
            <button class="btn-sm btn-danger-sm" onclick="deleteFaculty(${f.faculty_id}, '${f.name}')">Delete</button>
          </div>
        </td>
      </tr>
    `;
  });
}

function filterFaculty() {
  const query = (document.getElementById("facultySearch").value || "").toLowerCase();
  const dept = document.getElementById("facultyDeptFilter") ? document.getElementById("facultyDeptFilter").value : "";

  const filtered = allFaculty.filter(f => {
    const matchesQuery = f.name.toLowerCase().includes(query) || 
                         f.faculty_code.toLowerCase().includes(query) || 
                         f.email.toLowerCase().includes(query);
    const matchesDept = !dept || f.dept_id == dept;
    return matchesQuery && matchesDept;
  });
  renderFacultyTable(filtered);
}

function printFacultyDirectory() {
  filterFaculty();
  window.print();
}

function populateFacultyDropdowns() {
  const deptSelect = document.getElementById("facultyDept");
  if (deptSelect) {
    deptSelect.innerHTML = departmentsList.map(d => `<option value="${d.dept_id}">${d.dept_name} (${d.dept_code})</option>`).join('');
  }
}

function openAddFacultyModal() {
  populateFacultyDropdowns();
  document.getElementById("facultyModalTitle").textContent = "Add Faculty Member";
  document.getElementById("facultyId").value = "";
  document.getElementById("facultyName").value = "";
  document.getElementById("facultyEmail").value = "";
  document.getElementById("facultyCode").value = "";
  document.getElementById("facultyPassword").value = "";
  document.getElementById("facultyPassword").placeholder = "Default: Password123";
  document.getElementById("facultyDesignation").value = "Assistant Professor";
  openModal("facultyModal");
}

async function openEditFacultyModal(id) {
  populateFacultyDropdowns();
  const res = await api.get(`/api/faculty/${id}`);
  if (res.success && res.faculty) {
    const f = res.faculty;
    document.getElementById("facultyModalTitle").textContent = "Edit Faculty Details";
    document.getElementById("facultyId").value = f.faculty_id;
    document.getElementById("facultyName").value = f.name;
    document.getElementById("facultyEmail").value = f.email;
    document.getElementById("facultyCode").value = f.faculty_code;
    document.getElementById("facultyPassword").value = "";
    document.getElementById("facultyPassword").placeholder = "Leave blank to keep current";
    document.getElementById("facultyDept").value = f.dept_id;
    document.getElementById("facultyDesignation").value = f.designation;
    openModal("facultyModal");
  }
}

async function saveFaculty(event) {
  event.preventDefault();
  const id = document.getElementById("facultyId").value;
  const payload = {
    name: document.getElementById("facultyName").value.trim(),
    email: document.getElementById("facultyEmail").value.trim(),
    faculty_code: document.getElementById("facultyCode").value.trim(),
    dept_id: parseInt(document.getElementById("facultyDept").value),
    designation: document.getElementById("facultyDesignation").value,
    password: document.getElementById("facultyPassword").value.trim() || undefined
  };

  let res;
  if (id) {
    res = await api.put(`/api/faculty/${id}`, payload);
  } else {
    res = await api.post("/api/faculty", payload);
  }

  if (res.success) {
    Toast.show(`Faculty member ${payload.name} saved.`, "success");
    closeModal("facultyModal");
    loadFaculty();
  } else {
    Toast.show("Error: " + (res.message || "Failed to save faculty record."), "error");
  }
}

async function deleteFaculty(id, name) {
  if (confirm(`Remove faculty member "${name}"?`)) {
    const res = await api.del(`/api/faculty/${id}`);
    if (res.success) {
      Toast.show(`Faculty ${name} removed.`, "success");
      loadFaculty();
    } else {
      Toast.show("Error: " + (res.message || "Failed to delete faculty."), "error");
    }
  }
}

// -----------------------------------------------------------------------------
// 3. Subjects CRUD
// -----------------------------------------------------------------------------
let allSubjects = [];

async function loadSubjects() {
  const res = await api.get("/api/subjects");
  const tbody = document.getElementById("subject-table-body");
  if (!tbody) return;

  if (res.success) {
    allSubjects = res.subjects || [];
    renderSubjectsTable(allSubjects);
  }
}

function renderSubjectsTable(subjects) {
  const tbody = document.getElementById("subject-table-body");
  const countEl = document.getElementById("subjectTableCount");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (countEl) countEl.textContent = `${subjects.length} Courses`;

  if (subjects.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding: 28px;">No courses found.</td></tr>`;
    return;
  }

  subjects.forEach(sub => {
    const isLab = sub.type === "Lab";
    tbody.innerHTML += `
      <tr>
        <td><strong>${sub.subject_code}</strong></td>
        <td><strong>${sub.subject_name}</strong></td>
        <td>${sub.dept_name}</td>
        <td><span class="badge ${isLab ? 'badge-lab' : 'badge-ok'}">${sub.type}</span></td>
        <td>${sub.lectures_per_week} / wk (${sub.duration_hours}h)</td>
        <td>${sub.required_room_type} (${sub.min_capacity} seats)</td>
        <td>
          <div class="action-buttons">
            <button class="btn-sm btn-edit" onclick="openEditSubjectModal(${sub.subject_id})">Edit</button>
            <button class="btn-sm btn-danger-sm" onclick="deleteSubject(${sub.subject_id}, '${sub.subject_name}')">Delete</button>
          </div>
        </td>
      </tr>
    `;
  });
}

function filterSubjects() {
  const query = (document.getElementById("subjectSearch").value || "").toLowerCase();
  const dept = document.getElementById("subjectDeptFilter") ? document.getElementById("subjectDeptFilter").value : "";
  const type = document.getElementById("subjectTypeFilter") ? document.getElementById("subjectTypeFilter").value : "";

  const filtered = allSubjects.filter(sub => {
    const matchesQuery = sub.subject_name.toLowerCase().includes(query) || 
                         sub.subject_code.toLowerCase().includes(query);
    const matchesDept = !dept || sub.dept_id == dept;
    const matchesType = !type || sub.type == type;
    return matchesQuery && matchesDept && matchesType;
  });
  renderSubjectsTable(filtered);
}

function populateSubjectDropdowns() {
  const deptSelect = document.getElementById("subjectDept");
  if (deptSelect) {
    deptSelect.innerHTML = departmentsList.map(d => `<option value="${d.dept_id}">${d.dept_name} (${d.dept_code})</option>`).join('');
  }
}

function openAddSubjectModal() {
  populateSubjectDropdowns();
  document.getElementById("subjectModalTitle").textContent = "Add Course Record";
  document.getElementById("subjectId").value = "";
  document.getElementById("subjectCode").value = "";
  document.getElementById("subjectName").value = "";
  document.getElementById("subjectType").value = "Lecture";
  document.getElementById("subjectLectures").value = "3";
  document.getElementById("subjectDuration").value = "1";
  document.getElementById("subjectRoomType").value = "Classroom";
  document.getElementById("subjectMinCapacity").value = "45";
  document.getElementById("subjectProjector").checked = true;
  document.getElementById("subjectSmartBoard").checked = false;
  openModal("subjectModal");
}

async function openEditSubjectModal(id) {
  populateSubjectDropdowns();
  const res = await api.get(`/api/subjects/${id}`);
  if (res.success && res.subject) {
    const s = res.subject;
    document.getElementById("subjectModalTitle").textContent = "Edit Course Details";
    document.getElementById("subjectId").value = s.subject_id;
    document.getElementById("subjectCode").value = s.subject_code;
    document.getElementById("subjectName").value = s.subject_name;
    document.getElementById("subjectDept").value = s.dept_id;
    document.getElementById("subjectType").value = s.type;
    document.getElementById("subjectLectures").value = s.lectures_per_week;
    document.getElementById("subjectDuration").value = s.duration_hours;
    document.getElementById("subjectRoomType").value = s.required_room_type;
    document.getElementById("subjectMinCapacity").value = s.min_capacity || 40;
    document.getElementById("subjectProjector").checked = !!s.requires_projector;
    document.getElementById("subjectSmartBoard").checked = !!s.requires_smart_board;
    openModal("subjectModal");
  }
}

async function saveSubject(event) {
  event.preventDefault();
  const id = document.getElementById("subjectId").value;
  const payload = {
    subject_code: document.getElementById("subjectCode").value.trim(),
    subject_name: document.getElementById("subjectName").value.trim(),
    dept_id: parseInt(document.getElementById("subjectDept").value),
    type: document.getElementById("subjectType").value,
    lectures_per_week: parseInt(document.getElementById("subjectLectures").value),
    duration_hours: parseInt(document.getElementById("subjectDuration").value),
    required_room_type: document.getElementById("subjectRoomType").value,
    min_capacity: parseInt(document.getElementById("subjectMinCapacity").value),
    requires_projector: document.getElementById("subjectProjector").checked,
    requires_smart_board: document.getElementById("subjectSmartBoard").checked,
    min_computers: document.getElementById("subjectType").value === "Lab" ? 30 : 0
  };

  let res;
  if (id) {
    res = await api.put(`/api/subjects/${id}`, payload);
  } else {
    res = await api.post("/api/subjects", payload);
  }

  if (res.success) {
    Toast.show(`Course ${payload.subject_code} saved.`, "success");
    closeModal("subjectModal");
    loadSubjects();
  } else {
    Toast.show("Error: " + (res.message || "Failed to save subject."), "error");
  }
}

async function deleteSubject(id, name) {
  if (confirm(`Delete subject "${name}"?`)) {
    const res = await api.del(`/api/subjects/${id}`);
    if (res.success) {
      Toast.show(`Course ${name} deleted.`, "success");
      loadSubjects();
    } else {
      Toast.show("Error: " + (res.message || "Failed to delete subject."), "error");
    }
  }
}

// -----------------------------------------------------------------------------
// 4. Resources (Classrooms & Labs) CRUD
// -----------------------------------------------------------------------------
async function loadResources() {
  const roomsRes = await api.get("/api/rooms");
  const labsRes = await api.get("/api/labs");
  
  if (roomsRes.success) {
    allRoomsList = roomsRes.rooms || [];
    const countEl = document.getElementById("roomsCount");
    if (countEl) countEl.textContent = allRoomsList.length;
    renderRoomsTable(allRoomsList);
  }
  
  if (labsRes.success) {
    allLabsList = labsRes.labs || [];
    const countEl = document.getElementById("labsCount");
    if (countEl) countEl.textContent = allLabsList.length;
    renderLabsTable(allLabsList);
  }
}

function renderRoomsTable(rooms) {
  const roomBody = document.getElementById("room-table-body");
  if (!roomBody) return;

  if (rooms.length === 0) {
    roomBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding: 24px;">No classrooms found.</td></tr>`;
  } else {
    roomBody.innerHTML = rooms.map(r => `
      <tr>
        <td><strong>${r.room_number}</strong></td>
        <td>${r.building}</td>
        <td><strong>${r.capacity}</strong> Seats</td>
        <td>${r.projector_available ? '<span class="badge badge-ok">Projector Ready</span>' : '<span class="badge badge-neutral">Standard</span>'}</td>
        <td>
          <div class="action-buttons">
            <button class="btn-sm btn-edit" onclick="openEditRoomModal(${r.room_id})">Edit</button>
            <button class="btn-sm btn-danger-sm" onclick="deleteRoom(${r.room_id}, '${r.room_number}')">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');
  }
}

function renderLabsTable(labs) {
  const labBody = document.getElementById("lab-table-body");
  if (!labBody) return;

  if (labs.length === 0) {
    labBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding: 24px;">No laboratories found.</td></tr>`;
  } else {
    labBody.innerHTML = labs.map(l => `
      <tr>
        <td><strong>${l.lab_name}</strong></td>
        <td>${l.building}</td>
        <td><strong>${l.capacity}</strong> Seats</td>
        <td><span class="badge badge-info">${l.computer_count} Workstations</span></td>
        <td><span style="font-size:12px; color:#475569;">${l.specialized_equipment || 'General Purpose'}</span></td>
        <td>
          <div class="action-buttons">
            <button class="btn-sm btn-edit" onclick="openEditLabModal(${l.lab_id})">Edit</button>
            <button class="btn-sm btn-danger-sm" onclick="deleteLab(${l.lab_id}, '${l.lab_name}')">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');
  }
}

function filterRooms() {
  const query = (document.getElementById("roomSearch").value || "").toLowerCase();
  const filtered = allRoomsList.filter(r => 
    r.room_number.toLowerCase().includes(query) || 
    r.building.toLowerCase().includes(query)
  );
  renderRoomsTable(filtered);
}

function filterLabs() {
  const query = (document.getElementById("labSearch").value || "").toLowerCase();
  const filtered = allLabsList.filter(l => 
    l.lab_name.toLowerCase().includes(query) || 
    l.building.toLowerCase().includes(query) ||
    (l.specialized_equipment && l.specialized_equipment.toLowerCase().includes(query))
  );
  renderLabsTable(filtered);
}

// Room Modals
function openAddRoomModal() {
  document.getElementById("roomModalTitle").textContent = "Add Classroom";
  document.getElementById("roomId").value = "";
  document.getElementById("roomNumber").value = "";
  document.getElementById("roomBuilding").value = "Main Academic Block";
  document.getElementById("roomCapacity").value = "60";
  document.getElementById("roomProjector").checked = true;
  document.getElementById("roomSmartBoard").checked = false;
  openModal("roomModal");
}

async function openEditRoomModal(id) {
  const res = await api.get(`/api/rooms/${id}`);
  if (res.success && res.room) {
    const r = res.room;
    document.getElementById("roomModalTitle").textContent = "Edit Classroom";
    document.getElementById("roomId").value = r.room_id;
    document.getElementById("roomNumber").value = r.room_number;
    document.getElementById("roomBuilding").value = r.building;
    document.getElementById("roomCapacity").value = r.capacity;
    document.getElementById("roomProjector").checked = !!r.projector_available;
    document.getElementById("roomSmartBoard").checked = !!r.smart_board_available;
    openModal("roomModal");
  }
}

async function saveRoom(event) {
  event.preventDefault();
  const id = document.getElementById("roomId").value;
  const payload = {
    room_number: document.getElementById("roomNumber").value.trim(),
    building: document.getElementById("roomBuilding").value.trim(),
    capacity: parseInt(document.getElementById("roomCapacity").value),
    projector_available: document.getElementById("roomProjector").checked,
    smart_board_available: document.getElementById("roomSmartBoard").checked
  };

  let res;
  if (id) {
    res = await api.put(`/api/rooms/${id}`, payload);
  } else {
    res = await api.post("/api/rooms", payload);
  }

  if (res.success) {
    Toast.show(`Classroom ${payload.room_number} saved.`, "success");
    closeModal("roomModal");
    loadResources();
  } else {
    Toast.show("Error: " + (res.message || "Failed to save classroom."), "error");
  }
}

async function deleteRoom(id, roomNo) {
  if (confirm(`Delete classroom "${roomNo}"?`)) {
    const res = await api.del(`/api/rooms/${id}`);
    if (res.success) {
      Toast.show(`Classroom ${roomNo} deleted.`, "success");
      loadResources();
    } else {
      Toast.show("Error: " + (res.message || "Failed to delete room."), "error");
    }
  }
}

// Lab Modals
function openAddLabModal() {
  document.getElementById("labModalTitle").textContent = "Add Laboratory";
  document.getElementById("labId").value = "";
  document.getElementById("labName").value = "";
  document.getElementById("labBuilding").value = "Tech Tower A";
  document.getElementById("labCapacity").value = "35";
  document.getElementById("labComputers").value = "35";
  document.getElementById("labProjector").checked = true;
  document.getElementById("labSpecs").value = "";
  openModal("labModal");
}

async function openEditLabModal(id) {
  const res = await api.get(`/api/labs/${id}`);
  if (res.success && res.lab) {
    const l = res.lab;
    document.getElementById("labModalTitle").textContent = "Edit Laboratory";
    document.getElementById("labId").value = l.lab_id;
    document.getElementById("labName").value = l.lab_name;
    document.getElementById("labBuilding").value = l.building;
    document.getElementById("labCapacity").value = l.capacity;
    document.getElementById("labComputers").value = l.computer_count;
    document.getElementById("labProjector").checked = !!l.projector_available;
    document.getElementById("labSpecs").value = l.specialized_equipment || "";
    openModal("labModal");
  }
}

async function saveLab(event) {
  event.preventDefault();
  const id = document.getElementById("labId").value;
  const payload = {
    lab_name: document.getElementById("labName").value.trim(),
    building: document.getElementById("labBuilding").value.trim(),
    capacity: parseInt(document.getElementById("labCapacity").value),
    computer_count: parseInt(document.getElementById("labComputers").value),
    projector_available: document.getElementById("labProjector").checked,
    specialized_equipment: document.getElementById("labSpecs").value.trim()
  };

  let res;
  if (id) {
    res = await api.put(`/api/labs/${id}`, payload);
  } else {
    res = await api.post("/api/labs", payload);
  }

  if (res.success) {
    Toast.show(`Laboratory ${payload.lab_name} saved.`, "success");
    closeModal("labModal");
    loadResources();
  } else {
    Toast.show("Error: " + (res.message || "Failed to save laboratory."), "error");
  }
}

async function deleteLab(id, labName) {
  if (confirm(`Delete laboratory "${labName}"?`)) {
    const res = await api.del(`/api/labs/${id}`);
    if (res.success) {
      Toast.show(`Laboratory ${labName} deleted.`, "success");
      loadResources();
    } else {
      Toast.show("Error: " + (res.message || "Failed to delete lab."), "error");
    }
  }
}

// -----------------------------------------------------------------------------
// 5. Course Assignments CRUD
// -----------------------------------------------------------------------------
let allAssignments = [];

async function loadAssignments() {
  const res = await api.get("/api/assignments");
  const tbody = document.getElementById("assignment-table-body");
  if (!tbody) return;

  if (res.success) {
    allAssignments = res.assignments || [];
    renderAssignmentsTable(allAssignments);
  }
}

function renderAssignmentsTable(assignments) {
  const tbody = document.getElementById("assignment-table-body");
  const countEl = document.getElementById("assignmentTableCount");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (countEl) countEl.textContent = `${assignments.length} Mappings`;

  if (assignments.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding: 28px;">No course assignments mapped. Click "Assign Course" above.</td></tr>`;
    return;
  }

  assignments.forEach(a => {
    const isLab = a.subject_type === 'Lab';
    tbody.innerHTML += `
      <tr>
        <td><strong>${a.subject_code}</strong></td>
        <td><strong>${a.subject_name}</strong> <span class="badge ${isLab ? 'badge-lab' : 'badge-ok'}" style="font-size:10px;">${a.subject_type}</span></td>
        <td>${a.faculty_name} (${a.faculty_code})</td>
        <td><span class="badge badge-ok" style="white-space: nowrap;">${a.section_name}</span> (${a.dept_name})</td>
        <td>${a.lectures_per_week} classes / wk</td>
        <td>
          <button class="btn-sm btn-danger-sm" onclick="deleteAssignment(${a.assignment_id}, '${a.subject_code}', '${a.section_name}')">Remove</button>
        </td>
      </tr>
    `;
  });
}

function filterAssignments() {
  const query = (document.getElementById("assignmentSearch").value || "").toLowerCase();
  const filtered = allAssignments.filter(a => 
    a.subject_code.toLowerCase().includes(query) || 
    a.subject_name.toLowerCase().includes(query) ||
    a.faculty_name.toLowerCase().includes(query) ||
    a.section_name.toLowerCase().includes(query)
  );
  renderAssignmentsTable(filtered);
}

function populateAssignmentDropdowns() {
  const subSelect = document.getElementById("assignSubject");
  const facSelect = document.getElementById("assignFaculty");
  const secSelect = document.getElementById("assignSection");

  if (subSelect) {
    subSelect.innerHTML = subjectsList.map(s => `<option value="${s.subject_id}">${s.subject_code} - ${s.subject_name} (${s.type})</option>`).join('');
  }
  if (facSelect) {
    facSelect.innerHTML = facultyList.map(f => `<option value="${f.faculty_id}">${f.name} (${f.dept_name})</option>`).join('');
  }
  if (secSelect) {
    secSelect.innerHTML = sectionsList.map(s => `<option value="${s.section_id}">${s.section_name} (${s.dept_name})</option>`).join('');
  }
}

function openAddAssignmentModal() {
  populateAssignmentDropdowns();
  openModal("assignmentModal");
}

async function saveAssignment(event) {
  event.preventDefault();
  const payload = {
    subject_id: parseInt(document.getElementById("assignSubject").value),
    faculty_id: parseInt(document.getElementById("assignFaculty").value),
    section_id: parseInt(document.getElementById("assignSection").value)
  };

  const res = await api.post("/api/assignments", payload);
  if (res.success) {
    Toast.show("Course allocation created successfully.", "success");
    closeModal("assignmentModal");
    loadAssignments();
  } else {
    Toast.show("Error: " + (res.message || "Failed to create course assignment."), "error");
  }
}

async function deleteAssignment(id, subCode, section) {
  if (confirm(`Remove course mapping for ${subCode} (${section})?`)) {
    const res = await api.del(`/api/assignments/${id}`);
    if (res.success) {
      Toast.show(`Mapping for ${subCode} removed.`, "success");
      loadAssignments();
    } else {
      Toast.show("Error: " + (res.message || "Failed to remove mapping."), "error");
    }
  }
}
