// Reviews data will be populated from backend template
const reviews = window.reviewsData || [];

let currentIndex = 0;
let updatingReview = false;

function getStars(rating) {
    const fullStars = "★".repeat(rating);
    const emptyStars = "☆".repeat(5 - rating);
    return fullStars + emptyStars;
}

function showReview(index, direction = "right") {
    if (reviews.length === 0) return;
    
    updatingReview = true;
    const reviewContent = document.getElementById("review-content");
    const review = reviews[index];
    const newReview = document.createElement("div");
    newReview.classList.add("review-slide");
    newReview.innerHTML = `
    <div class="review-stars">${getStars(review.rating)}</div>
    <div class="review-text">"${review.text}"</div>
    <div class="review-author">
        <div class="author-info" style="text-align: center;">
        <strong>${review.author}</strong><br>
        <span class="activity">${review.activity}</span>
        </div>
    </div>
    `;
    const inAnim = direction === "right" ? "slideInFromRight" : "slideInFromLeft";
    const outAnim = direction === "right" ? "slideOutToLeft" : "slideOutToRight";

    if (reviewContent.firstChild) {
        const oldReview = reviewContent.firstChild;
        oldReview.style.animationName = outAnim;
        oldReview.addEventListener("animationend", () => {
            reviewContent.removeChild(oldReview);
            updatingReview = false;
        }, { once: true });
    } else {
        newReview.addEventListener("animationend", () => { updatingReview = false; }, { once: true });
    }

    newReview.style.animationName = inAnim;
    reviewContent.appendChild(newReview);
    updateDots(index);
}

function prevReview() {
    if (updatingReview || reviews.length === 0) return;
    currentIndex = (currentIndex - 1 + reviews.length) % reviews.length;
    showReview(currentIndex, "left");
}

function nextReview() {
    if (updatingReview || reviews.length === 0) return;
    currentIndex = (currentIndex + 1) % reviews.length;
    showReview(currentIndex, "right");
}

function createDots() {
    const dotsContainer = document.getElementById("dots");
    dotsContainer.innerHTML = "";
    reviews.forEach((_, i) => {
        const dot = document.createElement("span");
        dot.classList.add("dot");
        dot.addEventListener("click", () => {
            if (updatingReview) return;
            const direction = i > currentIndex ? "right" : "left";
            currentIndex = i;
            showReview(currentIndex, direction);
        });
        dotsContainer.appendChild(dot);
    });
    updateDots(currentIndex);
}

function updateDots(activeIndex) {
    const dots = document.querySelectorAll(".dot");
    dots.forEach((dot, i) => dot.classList.toggle("active", i === activeIndex));
}

if (reviews.length > 0) {
    createDots();
    showReview(currentIndex);
}

/* Scroll Animations */
document.addEventListener("DOMContentLoaded", () => {
    const animatedElements = [
        document.querySelector(".hero .overlay"),
        document.querySelector(".activities h2"),
        document.querySelector(".activities .subtitle"),
        document.querySelector(".why-choose h2"),
        document.querySelector(".reviews .header"),
        document.querySelector(".reviews .review-container"),
        ...document.querySelectorAll(".card"),
        ...document.querySelectorAll(".feature")
    ].filter(el => el !== null);

    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show-el");
                obs.unobserve(entry.target);

                // Clean up after animation to restore hover effects
                entry.target.addEventListener("transitionend", (e) => {
                    if (e.propertyName !== "opacity") return;
                    entry.target.classList.remove("hidden-el", "show-el");
                    entry.target.classList.remove("delay-100", "delay-200", "delay-300");
                }, { once: true });
            }
        });
    }, observerOptions);

    // Add stagger delays
    const cards = document.querySelectorAll(".card");
    cards.forEach((card, index) => {
        const delay = (index % 3) * 100 + 100;
        if (delay === 100) card.classList.add("delay-100");
        if (delay === 200) card.classList.add("delay-200");
        if (delay === 300) card.classList.add("delay-300");
    });

    const features = document.querySelectorAll(".feature");
    features.forEach((feature, index) => {
        const delay = (index % 3) * 100 + 100;
        if (delay === 100) feature.classList.add("delay-100");
        if (delay === 200) feature.classList.add("delay-200");
        if (delay === 300) feature.classList.add("delay-300");
    });

    // Initialize elements
    animatedElements.forEach(el => {
        el.classList.add("hidden-el");
        observer.observe(el);
    });
});

/* Scroll To Top Button Logic */
const scrollTopBtn = document.getElementById("scrollTopBtn");

window.onscroll = function () {
    scrollFunction();
};

function scrollFunction() {
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        scrollTopBtn.style.display = "block";
    } else {
        scrollTopBtn.style.display = "none";
    }
}

scrollTopBtn.addEventListener("click", () => {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});