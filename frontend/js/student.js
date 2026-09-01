document.addEventListener("DOMContentLoaded", () => {
  Auth.requireRole("STUDENT");
  const user = Auth.getUser();
  if (user) {
    const nameEl = document.getElementById("userName");
    const emailEl = document.getElementById("userEmail");
    if (nameEl) nameEl.textContent = (user.profile && user.profile.name) ? user.profile.name : "Student";
    if (emailEl) emailEl.textContent = user.email || "";
  }
  renderTimetableGrid("student-timetable-container");
});