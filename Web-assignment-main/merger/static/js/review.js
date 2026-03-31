// Review page JS: star rating, autosize textarea, and AJAX-safe form submit
document.addEventListener('DOMContentLoaded', function () {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('ratingInput');
    let selectedRating = parseInt(ratingInput?.value || 0);

    function updateStars(rating) {
        stars.forEach((star) => {
            const r = parseInt(star.dataset.rating);
            const img = star.querySelector('.star-img');
            if (img) {
                if (r <= rating) {
                    img.src = img.src.replace('star-empty.png', 'star-filled.png');
                    star.classList.add('filled');
                } else {
                    img.src = img.src.replace('star-filled.png', 'star-empty.png');
                    star.classList.remove('filled');
                }
            }
        });
    }

    if (stars.length) {
        updateStars(selectedRating);

        stars.forEach((star) => {
            star.addEventListener('click', function () {
                selectedRating = parseInt(this.dataset.rating);
                ratingInput.value = selectedRating;
                updateStars(selectedRating);
            });
            star.addEventListener('mouseenter', function () {
                const hoverRating = parseInt(this.dataset.rating);
                updateStars(hoverRating);
            });
            star.addEventListener('mouseleave', function () {
                updateStars(selectedRating);
            });
        });
    }

    // autosize textarea
    const textarea = document.getElementById('reviewText');
    if (textarea) {
        textarea.style.overflow = 'hidden';
        const resize = () => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        };
        textarea.addEventListener('input', resize);
        resize();
    }

    // graceful AJAX submit: if JS enabled, send fetch and redirect on success
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const action = reviewForm.action;
            const formData = new FormData(reviewForm);

            fetch(action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
                .then(resp => {
                    if (resp.redirected) {
                        window.location = resp.url; // follow redirect (profile_booking)
                        return null;
                    }
                    return resp.text();
                })
                .catch(err => {
                    console.error('Review save failed', err);
                    alert('Failed to save review.');
                });
        });
    }

});


