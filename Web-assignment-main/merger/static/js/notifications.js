// Notification expand/collapse logic
document.addEventListener('DOMContentLoaded', function () {
  console.log('Notification script loaded');

  const expandButtons = document.querySelectorAll('.expand-btn');
  console.log('Found expand buttons:', expandButtons.length);

  expandButtons.forEach((button, index) => {
    console.log('Adding listener to button', index);

    button.addEventListener('click', function (e) {
      console.log('Button clicked!');
      e.stopPropagation();

      const card = this.closest('.notification-card') || this.closest('.notification-card-cancelled');
      const detailsDiv = card.querySelector('.notification-details');
      const isExpanded = card.classList.contains('expanded');

      console.log('Is expanded:', isExpanded);

      if (isExpanded) {
        // Collapse
        card.classList.remove('expanded');
        detailsDiv.classList.remove('visible');
        this.classList.remove('expanded');
      } else {
        // Expand
        card.classList.add('expanded');
        detailsDiv.classList.add('visible');
        this.classList.add('expanded');
      }
    });
  });
});