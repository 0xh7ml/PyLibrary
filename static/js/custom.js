function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function handleAction(url) {
    const csrfToken = getCsrfToken();

    axios.post(url,{
        csrfmiddlewaretoken: csrfToken
    },
    {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },

    })
    .then(response => {
        // Handle successful response
        console.log(response.data);
        location.reload(); // Reload the page to reflect changes
    })
    .catch(error => {
        // Handle error
        console.error(error);
    });
}