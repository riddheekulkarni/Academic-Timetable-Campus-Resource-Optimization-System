/**
 * Dynamic Interactive Timetable Grid & Filtering Library
 * 12-Hour AM/PM Format with Dedicated Lunch Break & Minimal Cell Layout
 */

let timetableCache = [];

async function initMasterTimetable() {
  const res = await api.get("/api/timetable");
  if (!res.success || !res.timetable) {
    document.getElementById("master-timetable-container").innerHTML = `
      <div class="status-card" style="text-align: center; padding: 40px;">
        <h3 style="font-size:16px; margin-bottom:8px;">No timetable generated yet</h3>
        <p style="color: var(--text-muted); font-size:13.5px; margin-bottom:16px;">Run the optimization engine to allocate classrooms and time slots.</p>
        <button class="btn" onclick="triggerOptimization()">Optimize Timetable Now</button>
      </div>
    `;
    return;
  }

  timetableCache = res.timetable || [];
  populateTimetableFilters(timetableCache);
  renderFilteredTimetableGrid("master-timetable-container", timetableCache);
}

function populateTimetableFilters(schedule) {
  const sectionFilter = document.getElementById("filterSection");
  const facultyFilter = document.getElementById("filterFaculty");
  const roomFilter = document.getElementById("filterRoom");

  if (sectionFilter) {
    const currentVal = sectionFilter.value;
    const sections = Array.from(new Set(schedule.map(e => e.section_name).filter(Boolean))).sort();
    sectionFilter.innerHTML = `<option value="">All Divisions</option>` + 
      sections.map(s => `<option value="${s}">${s}</option>`).join('');
    if (currentVal) sectionFilter.value = currentVal;
  }

  if (facultyFilter) {
    const currentVal = facultyFilter.value;
    const faculties = Array.from(new Set(schedule.map(e => e.faculty_name).filter(Boolean))).sort();
    facultyFilter.innerHTML = `<option value="">All Faculty</option>` + 
      faculties.map(f => `<option value="${f}">${f}</option>`).join('');
    if (currentVal) facultyFilter.value = currentVal;
  }

  if (roomFilter) {
    const currentVal = roomFilter.value;
    const rooms = Array.from(new Set(schedule.map(e => e.room_number || e.lab_name).filter(Boolean))).sort();
    roomFilter.innerHTML = `<option value="">All Classrooms &amp; Labs</option>` + 
      rooms.map(r => `<option value="${r}">${r}</option>`).join('');
    if (currentVal) roomFilter.value = currentVal;
  }
}

function onFilterChange() {
  const query = document.getElementById("timetableSearch") ? document.getElementById("timetableSearch").value.toLowerCase().trim() : "";
  const sec = document.getElementById("filterSection") ? document.getElementById("filterSection").value : "";
  const fac = document.getElementById("filterFaculty") ? document.getElementById("filterFaculty").value : "";
  const room = document.getElementById("filterRoom") ? document.getElementById("filterRoom").value : "";
  const type = document.getElementById("filterType") ? document.getElementById("filterType").value : "";

  const filtered = timetableCache.filter(e => {
    const matchQuery = !query || 
      e.subject_code.toLowerCase().includes(query) || 
      e.subject_name.toLowerCase().includes(query) ||
      (e.faculty_name && e.faculty_name.toLowerCase().includes(query)) ||
      (e.room_number && e.room_number.toLowerCase().includes(query)) ||
      (e.lab_name && e.lab_name.toLowerCase().includes(query));

    const matchSec = !sec || e.section_name === sec;
    const matchFac = !fac || e.faculty_name === fac;
    const matchRoom = !room || (e.room_number === room || e.lab_name === room);
    const matchType = !type || e.subject_type === type;

    return matchQuery && matchSec && matchFac && matchRoom && matchType;
  });

  renderFilteredTimetableGrid("master-timetable-container", filtered);
}

function renderFilteredTimetableGrid(containerId, schedule) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (schedule.length === 0) {
    container.innerHTML = `
      <div class="status-card" style="text-align: center; padding: 36px; color: var(--text-muted);">
        <p style="font-size: 14px; margin: 0;">No scheduled classes match the selected filter criteria.</p>
      </div>
    `;
    return;
  }

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  
  // 12-Hour AM/PM schedule slots with Lunch Break
  const times = [
    { label: "8:30 AM – 9:30 AM", match: ["08:30", "8:30", "08:30:00", "8:30:00"], isLunch: false },
    { label: "9:30 AM – 10:30 AM", match: ["09:30", "9:30", "09:30:00", "9:30:00"], isLunch: false },
    { label: "10:30 AM – 11:30 AM", match: ["10:30", "10:30:00"], isLunch: false },
    { label: "11:30 AM – 12:30 PM", match: ["11:30", "11:30:00"], isLunch: false },
    { label: "12:30 PM – 1:30 PM", match: ["12:30", "12:30:00"], isLunch: true },
    { label: "1:30 PM – 2:30 PM", match: ["13:30", "13:30:00", "1:30", "01:30"], isLunch: false },
    { label: "2:30 PM – 3:30 PM", match: ["14:30", "14:30:00", "2:30", "02:30"], isLunch: false },
    { label: "3:30 PM – 4:30 PM", match: ["15:30", "15:30:00", "3:30", "03:30"], isLunch: false },
    { label: "4:30 PM – 5:30 PM", match: ["16:30", "16:30:00", "4:30", "04:30"], isLunch: false }
  ];

  let html = `
    <div class="timetable-grid-wrapper">
      <table class="timetable-grid">
        <thead>
          <tr>
            <th style="width: 135px;">Time Slot</th>
            ${days.map(d => `<th>${d}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
  `;

  times.forEach(t => {
    if (t.isLunch) {
      // Dedicated Full-Width Lunch Break Row
      html += `
        <tr class="lunch-break-row">
          <td class="time-col" style="background:#f1f5f9; color:#475569; font-weight:700;">${t.label}</td>
          <td colspan="5" class="lunch-break-cell">
            <div class="lunch-ribbon">
              <svg viewBox="0 0 24 24" style="width:13px; height:13px; stroke:currentColor; stroke-width:2; fill:none;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              Lunch Break
            </div>
          </td>
        </tr>
      `;
      return;
    }

    html += `<tr><td class="time-col">${t.label}</td>`;
    
    days.forEach(day => {
      const entries = schedule.filter(e => {
        if (e.day_of_week !== day) return false;
        const st = (e.start_time || "").trim();
        return t.match.some(m => st === m || st.startsWith(m));
      });

      if (entries.length > 0) {
        html += `<td>`;
        entries.forEach(entry => {
          const isLab = entry.subject_type === 'Lab';
          const loc = entry.room_number || entry.lab_name || 'TBD';
          html += `
            <div class="cell-card ${isLab ? 'lab' : ''}">
              <div class="cell-top">
                <span class="cell-code">${entry.subject_code}</span>
                <span class="cell-loc">${loc}</span>
              </div>
              <div class="cell-sub" title="${entry.subject_name}">${entry.subject_name}</div>
              <div class="cell-prof">${entry.faculty_name} &bull; ${entry.section_name || ''}</div>
            </div>
          `;
        });
        html += `</td>`;
      } else {
        html += `<td class="empty-cell">-</td>`;
      }
    });

    html += `</tr>`;
  });

  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

/**
 * Role Specific Timetable (Student / Faculty)
 */
async function renderTimetableGrid(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const res = await api.get("/api/timetable");
  if (!res.success || !res.timetable || res.timetable.length === 0) {
    container.innerHTML = `
      <div class="status-card" style="text-align: center; padding: 36px;">
        <h3 style="font-size: 16px; margin-bottom: 6px;">No schedule records available</h3>
        <p style="color: var(--text-muted); font-size: 13.5px;">Your personalized timetable has not been allocated yet. Please check back later.</p>
      </div>
    `;
    return;
  }

  renderFilteredTimetableGrid(containerId, res.timetable);
}