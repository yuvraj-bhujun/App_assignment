document.addEventListener('DOMContentLoaded', () => {
    // Show all photos
    const showAllBtn = document.querySelector('.show-all-photos');
    if (showAllBtn) {
        showAllBtn.addEventListener('click', () => {
            alert('Opening photo gallery...');
        });
    }

});