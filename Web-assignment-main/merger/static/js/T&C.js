const params = new URLSearchParams(window.location.search);
const from = params.get('from'); // "signup" or null
const accepbutton = document.getElementById('acceptBtn');

if (accepbutton) {
    if (from === 'signup') {
        accepbutton.style.display = 'inline-block'; // show
    } else {
        accepbutton.style.display = 'none'; // hide
    }
}
// Smooth scrolling for TOC
document.querySelectorAll('#toc a').forEach(a=>{
    a.addEventListener('click', e=>{
    e.preventDefault();
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if(el){ el.scrollIntoView({behavior:'smooth',block:'start'}); window.history.replaceState(null,'', '#'+id);}    
    })
})

// Search inside terms
const search = document.getElementById('search');
const toc = document.getElementById('toc');
const anchors = Array.from(toc.querySelectorAll('a'));
search.addEventListener('input', ()=>{
    const q = search.value.trim().toLowerCase();
    anchors.forEach(a=>{
    const target = document.querySelector(a.getAttribute('href'));
    const text = (target && target.innerText) ? target.innerText.toLowerCase() : '';
    if(!q || text.includes(q)){
        a.style.display='block';
    } else { a.style.display='none'; }
    })
})

// Accept button (visual only)
const acceptBtn = document.getElementById('acceptBtn');
acceptBtn.addEventListener('click', ()=>{
    acceptBtn.innerText='Accepted ✓';
    acceptBtn.disabled = true;
    acceptBtn.style.opacity = .9;
    // Here you could hook into your site to persist acceptance
})

function acceptTerms() {
    // Save acceptance in browser
    localStorage.setItem('accepted_terms', 'true');

    // Go back to the previous page
    window.history.back();
}


// Set effective date to today if not set
(function(){
    const el = document.getElementById('effectiveDate');
    if(el && el.innerText.trim()==='2025-11-28') return; // keep provided
    const d = new Date();
    el && (el.textContent = d.toISOString().slice(0,10));
})();