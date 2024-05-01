function displayPost(data) {
    const items = data.result;
    let content = '';
    for (let i = 0; i < items.length; i++) {
        content += 
        `<div>
            <h4>${items[i].username}</h4>
            <img src="${items[i].profilePicURL}" width="50" height="50">
            <h3>${items[i].title}</h3>
            <p>${items[i].body}</p>
            <p>${items[i].date}</p>
            <a href="#" class="Reply-link" onclick="replyPost('${items[i].post}', '${items[i].username}')">Reply</a>
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

