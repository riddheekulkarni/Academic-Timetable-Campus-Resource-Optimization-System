document.addEventListener("DOMContentLoaded", () => {
  Auth.requireRole("FACULTY");
  const user = Auth.getUser();
  if (user) {
    const nameEl = document.getElementById("userName");
    const emailEl = document.getElementById("userEmail");
    if (nameEl) nameEl.textContent = (user.profile && user.profile.name) ? user.profile.name : "Faculty Member";
    if (emailEl) emailEl.textContent = user.email || "";
  }
  if (window.location.pathname.includes("availability.html")) {
    loadAvailability();
  } else {
    renderTimetableGrid("faculty-timetable-container");
  }
});

const availabilityDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

function formatAvailabilityTime(value) {
  const [hours, minutes] = String(value || "").slice(0, 5).split(":").map(Number);
  if (Number.isNaN(hours) || Number.isNaN(minutes)) return "";
  const period = hours >= 12 ? "PM" : "AM";
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${String(minutes).padStart(2, "0")} ${period}`;
}

async function loadAvailability() {
  const response = await api.get("/api/faculty/availability");
  if (!response.success) {
    Toast.show(response.message || "Unable to load availability.", "error");
    return;
  }

  const grid = document.getElementById("availability-grid");
  const slotsByDay = Object.fromEntries(availabilityDays.map(day => [day, []]));
  (response.slots || []).forEach(slot => slotsByDay[slot.day_of_week].push(slot));

  grid.innerHTML = availabilityDays.map(day => `
    <section class="availability-day">
      <h3>${day}</h3>
      <div class="availability-slots">
        ${(slotsByDay[day] || []).map(slot => `
          <label class="availability-slot ${slot.is_available ? "" : "unavailable"}">
            <input type="checkbox" data-slot-id="${slot.slot_id}" ${slot.is_available ? "" : "checked"} onchange="updateAvailabilitySlot(this)">
            <span>${formatAvailabilityTime(slot.start_time)} - ${formatAvailabilityTime(slot.end_time)}</span>
          </label>
        `).join("")}
      </div>
    </section>
  `).join("");
}

function updateAvailabilitySlot(input) {
  input.closest(".availability-slot").classList.toggle("unavailable", input.checked);
}

function markAllAvailable() {
  document.querySelectorAll("#availability-grid input[type='checkbox']").forEach(input => {
    input.checked = false;
    updateAvailabilitySlot(input);
  });
}

async function saveAvailability() {
  const button = document.getElementById("saveAvailabilityBtn");
  const unavailable_slot_ids = Array.from(document.querySelectorAll("#availability-grid input:checked"))
    .map(input => Number(input.dataset.slotId));
  button.disabled = true;
  button.textContent = "Saving...";

  const response = await api.put("/api/faculty/availability", { unavailable_slot_ids });
  button.disabled = false;
  button.textContent = "Save Availability";
  Toast.show(response.message || "Availability saved.", response.success ? "success" : "error");
}