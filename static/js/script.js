// Small client-side helper: prevent repeated form submissions.
document.addEventListener('submit', e => { const b=e.target.querySelector('button[type=submit],button:not([type])'); if(b){b.disabled=true;b.textContent='Please wait…';} }, true);
