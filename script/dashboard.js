function displayPost(data) {
    const items = data.result;
    let content = '';
    for (let i = 0; i < items.length; i++) {
        content += 
        `<div>
            <h4>${items[i].username}</h4>
            <img src="${items[i].url}" alt="Thumbnail" style="width: 50px; height: 50px;">
            <h3>${items[i].title}</h3>
            <p>${items[i].body}</p>
            <p>${items[i].date}</p>
        </div>`
        }
    document.getElementById('dashboard').innerHTML = content;
}

function renderPost() {
    fetch('/dashboard') 
        .then(response => response.json())
        .then(data => displayPost(data));
}

window.onload = function() {
    renderPost();
};
