const adopt_btn = document.getElementById('adopt-btn');

adopt_btn.addEventListener('click', async _ => {
    try {
        const response = await fetch(window.location.href, {
            method: 'POST',
            mode: 'cors'
        });
        window.location.href =  (window.location.origin + '/home')
        console.log(response)
    } catch(err) {
        console.log(err);
    }
});