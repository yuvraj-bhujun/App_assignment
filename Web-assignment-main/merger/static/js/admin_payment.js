function generateReport() {
    const btn = document.querySelector('.generate-btn');
    btn.classList.add('downloading');
    btn.innerHTML = '<span>Generating...</span>';

    setTimeout(() => {
        btn.innerHTML = '<span>✓ Report Generated</span>';
        
        setTimeout(() => {
            btn.classList.remove('downloading');
            btn.innerHTML = '<span>Generate report</span>';
        }, 1500);
    }, 1500);

    // In a real application, this would trigger a PDF download or similar
    console.log('Generating payment report...');
    window.location.href = "/grandblue/admin/payments/report/pdf/";
}