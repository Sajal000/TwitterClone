function displayPost(data) {
    const items = data.result
    let content = ''
    for (let i = 0; i < items.length; i++) {
        content += 
        `<div>
            <a href="/user/${items[i].username}"><h4>${items[i].username}</h4></a>
            <img src="${items[i].url}" alt="Profile Pic" width="50" height="50">
            <h3>${items[i].title}</h3>
            <p>${items[i].body}</p>
            <p>${items[i].date}</p>
            <a href="#" class="Reply-link" onclick="replyPost('${items[i].post}', '${items[i].username}')">Reply</a>
        </div>`
    }
    document.getElementById('dashboard').innerHTML = content
}


const replyPost = (postId, username) => {
    let replyForm = document.getElementById('replyForm')
    let replyTitleInput = document.getElementById('replyTitle')

    replyTitleInput.value = `Reply to: ${username}`
    replyTitleInput.readOnly = true

    replyForm.style.display = 'block'
    document.getElementById('postId').value = postId
}

const submitReply = () => {
    let replyForm = document.getElementById('replyForm')
    replyForm.style.display = 'block'

    let replyTitle = document.getElementById('replyTitle').value
    let replyBody = document.getElementById('replyBody').value 

    if (!replyTitle && !replyBody) {
        alert('Please put a title and body to post! You can\'t just reply blank thoughts......')
        return
    }

    let xhttp = new XMLHttpRequest()
    xhttp.onload = function () {
    if (xhttp.status === 200) {
        const response = JSON.parse(xhttp.responseText)

        const titleElement = document.createElement('p')
        titleElement.textContent = response.replyTitle

        const postElement = document.createElement('p')
        postElement.textContent = response.replyBody

        const dashboard = document.getElementById('dashboard')
        dashboard.appendChild(titleElement)
        dashboard.appendChild(postElement)

        alert('Reply uploaded successfully!')
        renderPost();
    } else {
        console.log('Error uploading post!')
        alert('Error uploading post!')
    }
   }

    xhttp.open('POST', '/reply', true)
    const formData = new FormData()
    formData.append('replyTitle', replyTitle)
    formData.append('replyBody', replyBody)

    xhttp.send(formData)
}

function renderPost() {
    fetch('/dashboard') 
        .then(response => response.json())
        .then(data => displayPost(data));
}

window.onload = function() {
    renderPost();
};
