const editBtn = document.getElementById("editBtn");
const saveBtn = document.getElementById("saveBtn");
const form = document.getElementById("profileForm");
const inputs = form.querySelectorAll("input");
const togglePwd = document.getElementById("togglePwd");
const pwdField = document.getElementById("pwd");

// ✏️ Enable editing
editBtn.addEventListener("click", () => {
  inputs.forEach((i) => (i.disabled = false));
  editBtn.classList.add("hidden");
  saveBtn.classList.remove("hidden");
  togglePwd.style.pointerEvents = "auto";
});

// 💾 Save form with validation
form.addEventListener("submit", (e) => {
  e.preventDefault();
  let valid = true;
  const email = document.getElementById("email").value.trim();
  const password = pwdField.value;
  const tel = document.getElementById("tel").value.trim();

  inputs.forEach((i) => (i.style.borderColor = "#d7d7d7"));

  // Email validation
  if (!/^\S+@\S+\.\S+$/.test(email)) {
    valid = false;
    document.getElementById("email").style.borderColor = "red";
    alert("Please enter a valid email address.");
  }

  // Password validation
  if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/.test(password)) {
    valid = false;
    pwdField.style.borderColor = "red";
    alert("Password must be at least 8 characters with letters and numbers.");
  }

  // Telephone validation
  if (!/^\d{8,15}$/.test(tel)) {
    valid = false;
    document.getElementById("tel").style.borderColor = "red";
    alert("Telephone number must be 8 to 15 digits.");
  }

  if (!valid) return;

  // Update display info
  document.getElementById("displayName").textContent =
    document.getElementById("fname").value +
    " " +
    document.getElementById("lname").value;
  document.getElementById("displayEmail").textContent = email;

  // Disable inputs again
  inputs.forEach((i) => (i.disabled = true));
  saveBtn.classList.add("hidden");
  editBtn.classList.remove("hidden");
  togglePwd.style.pointerEvents = "none";
});

// 👁️ Toggle password visibility
togglePwd.addEventListener("click", () => {
  if (pwdField.disabled) return;
  const isPwd = pwdField.type === "password";
  pwdField.type = isPwd ? "text" : "password";
  togglePwd.innerHTML = isPwd
    ? `<path d="M12 4.5c-7.633 0-12 7.5-12 7.5s4.367 7.5 12 7.5 12-7.5 12-7.5-4.367-7.5-12-7.5zm0 12a4.5 4.5 0 110-9 4.5 4.5 0 010 9z"/>`
    : `<path d="M12 5c-7.633 0-12 7-12 7s4.367 7 12 7 12-7 12-7-4.367-7-12-7zm0 12a5 5 0 110-10 5 5 0 010 10z"/><circle cx="12" cy="12" r="2.5"/>`;
});
togglePwd.style.pointerEvents = "none";


