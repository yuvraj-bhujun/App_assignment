  const logoutBtn = document.querySelector(".logout-btn");
  const logoutModal = document.getElementById("logoutModal");
  const confirmLogout = document.getElementById("confirmLogout");
  const cancelLogout = document.getElementById("cancelLogout");

  logoutBtn.addEventListener("click", () => {
    logoutModal.style.display = "flex";
  });

  cancelLogout.addEventListener("click", () => {
    logoutModal.style.display = "none";
  });

  confirmLogout.addEventListener("click", () => {
    logoutModal.style.display = "none";
    document.getElementById("logoutForm").submit();
    alert("You have been logged out!"); 
    // Replace alert with a redirect if needed:
    // window.location.href = "login.html";
  });

  // closes modal when clicking outside content
  window.addEventListener("click", (e) => {
    if (e.target === logoutModal) {
      logoutModal.style.display = "none";
    }
  });