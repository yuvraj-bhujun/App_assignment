document.addEventListener("DOMContentLoaded", () => {
  const deleteModal = document.getElementById('deleteModal');
  const addActivityModal = document.getElementById('addActivityModal');
  const editActivityModal = document.getElementById('editActivityModal');
  const modalMessage = document.getElementById('modalMessage');
  const deleteHighlightIdsContainer = document.getElementById('deleteHighlightIdsContainer');

  let currentRow = null;

  // ---------------- CLOSE MODAL BUTTONS ----------------
  document.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = e.target.closest('.modal');
      if (modal) {
        modal.style.display = 'none';
        if (modal.id === 'addActivityModal') {
          resetAddActivityForm();
        }
        if (modal.id === 'editActivityModal') {
          resetEditImagesState();
        }
      }
    });
  });

  // ---------------- DELETE ACTIVITY ----------------
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('tr');
      if (!row) return;

      const name = row.querySelector('.activity-name').textContent;
      modalMessage.textContent = `Are you sure you want to delete "${name}"?`;
      deleteModal.style.display = 'flex';
      currentRow = row;
    });
  });

  deleteModal?.querySelector('.cancel-btn')?.addEventListener('click', () => {
    deleteModal.style.display = 'none';
  });

  deleteModal?.querySelector('.create-btn')?.addEventListener('click', () => {
    if (currentRow) {
      const form = currentRow.querySelector('.delete-form');
      if (form) form.submit();
    }
    deleteModal.style.display = 'none';
  });

  // ---------------- ADD ACTIVITY MODAL ----------------
  const addForm = document.getElementById('addActivityForm');

  document.querySelector('.add-activity-btn')?.addEventListener('click', () => {
    addActivityModal.style.display = 'flex';
  });

  addActivityModal?.querySelector('.cancel-btn')?.addEventListener('click', () => {
    addActivityModal.style.display = 'none';
    resetAddActivityForm();
  });

  // ---------------- EDIT ACTIVITY MODAL ----------------
  const editForm = document.getElementById('editActivityForm');
  const editIdInput = document.getElementById('editActivityId');
  const editNameInput = document.getElementById('editName');
  const editTypeSelect = document.getElementById('editActivityType');
  const editLocationInput = document.getElementById('editLocation');
  const editDescriptionTextarea = document.getElementById('editDescription');
  const editPriceInput = document.getElementById('editPrice');
  const editDurationInput = document.getElementById('editDuration');
  const editMaxParticipantsInput = document.getElementById('editMaxParticipants');

  // NEW Activity field inputs (edit modal)
  const editRulesTextarea = document.getElementById('editRules');
  const editSafetyTextarea = document.getElementById('editSafety');
  const editCancelTextarea = document.getElementById('editCancel');
  const editMapUrlTextarea = document.getElementById('editMapUrl');
  const editMapDescTextarea = document.getElementById('editMapDesc');

  // Highlights containers/buttons
  const addHighlightsSection = document.getElementById('addHighlightsSection');
  const addHighlightBtn = document.getElementById('addHighlightBtn');
  const editHighlightsSection = document.getElementById('editHighlightsSection');
  const editAddHighlightBtn = document.getElementById('editAddHighlightBtn');

  // Template for highlight item with better layout
  function highlightItemTemplate({ id = "", title = "", description = "", image = "" } = {}, showRemove = false) {
    const item = document.createElement("div");
    item.className = "highlight-item";

    item.dataset.tempId = id || "TEMPLATE";

    const imagePreview = image ? `
      <div class="current-image-preview">
        <img src="${image}" alt="Current image">
        <span>Current image (upload new to replace)</span>
      </div>
    ` : '';

    item.innerHTML = `
      <input type="hidden" name="highlight_id" value="${id || 'TEMPLATE'}">

      <div class="form-group">
        <label>Title</label>
        <input type="text" name="highlight_title" value="${title}">
      </div>

      <div class="form-group">
        <label>Description</label>
        <textarea name="highlight_description">${description}</textarea>
      </div>

      <div class="form-group">
        <label>Image</label>
        <input type="file" name="highlight_image_${id || 'TEMPLATE'}" accept="image/*">
        ${imagePreview}
      </div>

      <button type="button" class="remove-highlight-btn" ${showRemove ? "" : 'style="display:none;"'}>Remove</button>
    `;

    item.querySelector(".remove-highlight-btn").addEventListener("click", () => {
      if (id && !isNaN(id) && Number(id) > 0) {
        // Existing highlight: add hidden input to form
        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'delete_highlight_ids';
        hidden.value = id;
        deleteHighlightIdsContainer.appendChild(hidden);
      }
      // Remove the item from DOM
      item.remove();
    });
    return item;
  }


  // ADD modal highlight add
  if (addHighlightBtn && addHighlightsSection) {
    // When creating a new highlight dynamically
    addHighlightBtn.addEventListener("click", () => {
      const existingItems = addHighlightsSection.querySelectorAll(".highlight-item");
      const tempId = `new_${existingItems.length}`;

      const newItem = highlightItemTemplate({ id: tempId }, true);

      // Update dataset
      newItem.dataset.tempId = tempId;

      // Update hidden ID
      newItem.querySelector('input[name="highlight_id"]').value = tempId;

      // Update file input name
      const fileInput = newItem.querySelector('input[type="file"]');
      fileInput.name = `highlight_image_${tempId}`;

      addHighlightsSection.appendChild(newItem);
    });
  }

  // EDIT modal highlight add
  if (editAddHighlightBtn && editHighlightsSection) {
    editAddHighlightBtn.addEventListener("click", () => {
      const existingItems = editHighlightsSection.querySelectorAll(".highlight-item");
      const newItem = highlightItemTemplate({}, true);
      editHighlightsSection.appendChild(newItem);

      if (existingItems.length > 0) {
        existingItems.forEach(item => {
          const removeBtn = item.querySelector(".remove-highlight-btn");
          if (removeBtn) removeBtn.style.display = "inline-block";
        });
      }
    });
  }

  // ---------------- EDIT IMAGES STATE ----------------
  const editDropzone = document.getElementById('editImageDropzone');
  const editFileInput = document.getElementById('editImagesInput');
  const editPreviewGrid = document.getElementById('editImagePreviewGrid');

  let editSelectedFiles = [];
  let existingEditImages = []; // [{id, url}]
  let deleteImageIds = new Set();

  function resetEditImagesState() {
    editSelectedFiles = [];
    existingEditImages = [];
    deleteImageIds = new Set();
    if (editPreviewGrid) editPreviewGrid.innerHTML = '';
    if (editFileInput) editFileInput.value = '';
    syncDeleteHiddenInputs();
  }

  function syncEditInputFiles() {
    const dt = new DataTransfer();
    editSelectedFiles.forEach(f => dt.items.add(f));
    editFileInput.files = dt.files;
  }

  function syncDeleteHiddenInputs() {
    if (!editForm) return;
    editForm.querySelectorAll('input[name="delete_image_ids"]').forEach(el => el.remove());
    deleteImageIds.forEach(id => {
      const hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = 'delete_image_ids';
      hidden.value = id;
      editForm.appendChild(hidden);
    });
  }

  function getRemainingSlots() {
    const maxFiles = 10;
    const existingCount = existingEditImages.filter(img => !deleteImageIds.has(String(img.id))).length;
    return Math.max(0, maxFiles - existingCount - editSelectedFiles.length);
  }

  function renderEditPreviews() {
    if (!editPreviewGrid) return;
    editPreviewGrid.innerHTML = '';

    // Existing images
    existingEditImages.forEach(img => {
      const idStr = String(img.id);
      if (deleteImageIds.has(idStr)) return;

      const card = document.createElement('div');
      card.className = 'image-thumb existing';
      card.innerHTML = `
        <img src="${img.url}" alt="Existing image">
        <button type="button" class="remove-btn" aria-label="Delete image">×</button>
      `;
      card.querySelector('.remove-btn').addEventListener('click', () => {
        deleteImageIds.add(idStr);
        syncDeleteHiddenInputs();
        renderEditPreviews();
      });
      editPreviewGrid.appendChild(card);
    });

    // New selected files
    editSelectedFiles.forEach((file, idx) => {
      const url = URL.createObjectURL(file);
      const card = document.createElement('div');
      card.className = 'image-thumb';
      card.innerHTML = `
        <img src="${url}" alt="${file.name}">
        <button type="button" class="remove-btn" aria-label="Remove image">×</button>
      `;
      card.querySelector('.remove-btn').addEventListener('click', () => {
        URL.revokeObjectURL(url);
        editSelectedFiles.splice(idx, 1);
        renderEditPreviews();
        syncEditInputFiles();
      });
      editPreviewGrid.appendChild(card);
    });
  }

  function initEditUploaderEvents() {
    if (!editDropzone || !editFileInput || !editPreviewGrid || !editForm) return;

    editDropzone.addEventListener('click', (e) => {
      if (
        e.target === editDropzone ||
        e.target.classList.contains('browse-link') ||
        e.target.closest('.image-dropzone')
      ) {
        editFileInput.click();
      }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
      editDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
      }, false);
    });

    editDropzone.addEventListener('dragover', () => editDropzone.classList.add('dragover'));
    editDropzone.addEventListener('dragleave', () => editDropzone.classList.remove('dragover'));
    editDropzone.addEventListener('drop', (e) => {
      editDropzone.classList.remove('dragover');
      handleEditFiles(e.dataTransfer.files);
    });

    editFileInput.addEventListener('change', (e) => handleEditFiles(e.target.files));

    function handleEditFiles(fileList) {
      const files = Array.from(fileList).filter(f => f.type.startsWith('image/'));
      const roomLeft = getRemainingSlots();
      const toAdd = files.slice(0, roomLeft);

      editSelectedFiles = editSelectedFiles.concat(toAdd);
      renderEditPreviews();
      syncEditInputFiles();
    }
  }

  initEditUploaderEvents();

  // Open edit modal + prefill from row data-* attributes
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('tr');
      if (!row) return;

      currentRow = row;
      const ds = row.dataset;
      
      console.log("=== CLICKED ROW DATA ===");
      console.log("Row dataset:", ds);

      try {
          console.log("Parsed highlights:", JSON.parse(ds.activityHighlights || "[]"));
      } catch (error) {
          console.error("Error parsing highlights:", error);
      }

      try {
          console.log("Parsed images:", JSON.parse(ds.activityImages || "[]"));
      } catch (error) {
          console.error("Error parsing images:", error);
      }

      console.log("=========================");

      if (editIdInput) editIdInput.value = ds.activityId || '';
      if (editNameInput) editNameInput.value = ds.activityName || '';
      if (editTypeSelect) editTypeSelect.value = ds.activityType || '';
      if (editLocationInput) editLocationInput.value = ds.activityLocation || '';
      if (editDescriptionTextarea) editDescriptionTextarea.value = ds.activityDescription || '';
      if (editPriceInput) editPriceInput.value = ds.activityPrice || '';
      if (editDurationInput) editDurationInput.value = ds.activityDuration || '';
      if (editMaxParticipantsInput) editMaxParticipantsInput.value = ds.activityMaxParticipants || '';

      if (editRulesTextarea) editRulesTextarea.value = ds.activityRules || '';
      if (editSafetyTextarea) editSafetyTextarea.value = ds.activitySafety || '';
      if (editCancelTextarea) editCancelTextarea.value = ds.activityCancel || '';
      if (editMapUrlTextarea) editMapUrlTextarea.value = ds.activityMapUrl || '';
      if (editMapDescTextarea) editMapDescTextarea.value = ds.activityMapDesc || '';

      // Load highlights data
      if (editHighlightsSection && editAddHighlightBtn) {
        editHighlightsSection.innerHTML = '';

        let highlights = [];
        try {
            highlights = JSON.parse(row.dataset.activityHighlights || "[]");
        } catch {
            highlights = [];
        }

        highlights.forEach((h, idx) => {
            const item = highlightItemTemplate({
                id: h.id || "0",  // 0 for new highlights (0 is for add activity, "" will be for edit)
                title: h.title || "",
                description: h.description || "",
                image: h.image || ""
            }, idx > 0);
            editHighlightsSection.appendChild(item);
        });
        // After rendering highlight items, rename file inputs based on highlight IDs
        const highlightItems = editHighlightsSection.querySelectorAll(".highlight-item");

        highlightItems.forEach((item, index) => {
            const idInput = item.querySelector('input[name="highlight_id"]');
            const fileInput = item.querySelector('input[type="file"][name="highlight_image"]');

            if (!fileInput) return;

            let highlightId = idInput ? idInput.value : "";

            // If it's a new highlight (id is empty), generate a temporary ID
            if (!highlightId) {
                highlightId = `new_${index}`;
            }

            // Assign dynamic name
            fileInput.name = `highlight_image_${highlightId}`;
        });
        editHighlightsSection.appendChild(editAddHighlightBtn);
      }

      resetEditImagesState();
      try {
        existingEditImages = JSON.parse(ds.activityImages || "[]");
      } catch {
        existingEditImages = [];
      }
      renderEditPreviews();
      syncEditInputFiles();
      syncDeleteHiddenInputs();

      // Show modal
      editActivityModal.style.display = 'flex';

      const modalBody = editActivityModal.querySelector('.modal-body');
      if (modalBody) modalBody.scrollTop = 0;
    });
  });

  // Cancel inside edit modal
  editActivityModal?.querySelector('.cancel-btn')?.addEventListener('click', (e) => {
    e.preventDefault();
    editActivityModal.style.display = 'none';
    resetEditImagesState();
  });

  // Let the edit form submit normally to backend
  editForm?.addEventListener('submit', () => {
    // Allow normal submission
  });

  // ---------------- CLICK OUTSIDE TO CLOSE MODALS ----------------
  window.addEventListener('click', (e) => {
    if (e.target === deleteModal) {
      deleteModal.style.display = 'none';
    }
    if (e.target === addActivityModal) {
      addActivityModal.style.display = 'none';
      resetAddActivityForm();
    }
    if (e.target === editActivityModal) {
      editActivityModal.style.display = 'none';
      resetEditImagesState();
    }
  });

  // ---------------- IMAGE UPLOAD / PREVIEW (ADD ONLY) ----------------
  const dropzone = document.getElementById('imageDropzone');
  const fileInput = document.getElementById('imagesInput');
  const previewGrid = document.getElementById('imagePreviewGrid');
  let selectedFiles = [];

  if (dropzone && fileInput && previewGrid && addForm) {
    dropzone.addEventListener('click', (e) => {
      if (e.target === dropzone || e.target.classList.contains('browse-link') || e.target.closest('.image-dropzone')) {
        fileInput.click();
      }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
      }, false);
    });

    dropzone.addEventListener('dragover', () => dropzone.classList.add('dragover'));
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
      dropzone.classList.remove('dragover');
      handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

    function handleFiles(fileList) {
      const maxFiles = 10;
      const files = Array.from(fileList);

      const valid = files.filter(f => f.type.startsWith('image/'));
      const roomLeft = Math.max(0, maxFiles - selectedFiles.length);
      const toAdd = valid.slice(0, roomLeft);

      selectedFiles = selectedFiles.concat(toAdd);
      renderPreviews();
      syncInputFiles();
    }

    function renderPreviews() {
      previewGrid.innerHTML = '';
      selectedFiles.forEach((file, idx) => {
        const url = URL.createObjectURL(file);
        const card = document.createElement('div');
        card.className = 'image-thumb';
        card.innerHTML = `
          <img src="${url}" alt="${file.name}">
          <button type="button" class="remove-btn" aria-label="Remove image">×</button>
        `;
        card.querySelector('.remove-btn').addEventListener('click', () => {
          URL.revokeObjectURL(url);
          selectedFiles.splice(idx, 1);
          renderPreviews();
          syncInputFiles();
        });
        previewGrid.appendChild(card);
      });
    }

    function syncInputFiles() {
      const dt = new DataTransfer();
      selectedFiles.forEach(f => dt.items.add(f));
      fileInput.files = dt.files;
    }
  }

  // ---------------- HELPERS ----------------
  function resetAddActivityForm() {
    selectedFiles = [];
    if (previewGrid) previewGrid.innerHTML = '';
    if (fileInput) fileInput.value = '';
    if (addForm) addForm.reset();

    if (addHighlightsSection && addHighlightBtn) {
      const items = addHighlightsSection.querySelectorAll(".highlight-item");
      items.forEach((item, idx) => {
        if (idx === 0) {
          const idInput = item.querySelector('input[name="highlight_id"]');
          const titleInput = item.querySelector('input[name="highlight_title"]');
          const descTextarea = item.querySelector('textarea[name="highlight_description"]');
          const imageInput = item.querySelector('input[name="highlight_image"]');

          if (idInput) idInput.value = '';
          if (titleInput) titleInput.value = '';
          if (descTextarea) descTextarea.value = '';
          if (imageInput) imageInput.value = '';

          const removeBtn = item.querySelector('.remove-highlight-btn');
          if (removeBtn) removeBtn.style.display = 'none';
        } else {
          item.remove();
        }
      });
    }
  }
});
