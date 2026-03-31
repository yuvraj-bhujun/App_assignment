// Logout Modal functionality
const logoutBtn = document.querySelector(".logout-btn");
const logoutModal = document.getElementById("logoutModal");
const confirmLogout = document.getElementById("confirmLogout");
const cancelLogout = document.getElementById("cancelLogout");

// Show logout modal
logoutBtn.addEventListener("click", () => {
  logoutModal.style.visibility = "visible";
  logoutModal.style.opacity = "1";
});

// Cancel logout
cancelLogout.addEventListener("click", () => {
  logoutModal.style.opacity = "0";
  setTimeout(() => {
    logoutModal.style.visibility = "hidden";
  }, 200);
});

// Confirm logout
confirmLogout.addEventListener("click", () => {
  // In production, this would redirect to logout URL
  alert("Logged out!");
  logoutModal.style.opacity = "0";
  setTimeout(() => {
    logoutModal.style.visibility = "hidden";
  }, 200);
});

// Close modal on outside click
logoutModal.addEventListener("click", (e) => {
  if (e.target === logoutModal) {
    logoutModal.style.opacity = "0";
    setTimeout(() => {
      logoutModal.style.visibility = "hidden";
    }, 200);
  }
});