document.addEventListener("DOMContentLoaded", () => {
  Auth.requireRole("FACULTY");
  const user = Auth.getUser();
  if (user) {
    const nameEl = document.getElementById("userName");
    const emailEl = document.getElementById("userEmail");
    if (nameEl) nameEl.textContent = (user.profile && user.profile.name) ? user.profile.name : "Faculty Member";
    if (emailEl) emailEl.textContent = user.email || "";
  }
  renderTimetableGrid("faculty-timetable-container");
});