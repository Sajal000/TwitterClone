function loadDoc(url, func) {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            func(xhttp.response);
        }
    }
    xhttp.open("GET", url);
    xhttp.send();
}

function login() {
    let txtEmail = document.getElementById("txtEmail").value.toLowerCase()
    let txtPassword = document.getElementById("txtPassword")

    if (txtEmail.value == '' || txtPassword.value == '') {
        alert("Email and password can not be blank.");
        return;
    }

    let URL = "/login?email=" + txtEmail.value + "&password=" + txtPassword.value;

    let chkRemember = document.getElementById('chkRemember')
    if (chkRemember.checked) {
        URL += "&remember=yes"
    } else {
        URL += "&remember=no"
    }

    loadDoc(URL, login_response);
}

function login_response(response) {
    let data = JSON.parse(response);
    let result = data["result"];
    if (result != "OK") {
        alert(result);
    }
    else {
        window.location.replace("/account.html");
    }
}

const post = () => {
    let titlePost = document.getElementById('titlePost').value
    let postBody = document.getElementById('postBody').value

    if (!titlePost && !postBody) {
        alert('Please put a title and body to post! You can\'t just post blank thoughts......')
        return
    }

    let xhttp = new XMLHttpRequest()
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            const response = JSON.parse(xhttp.responseText)

            const titleElement = document.createElement('p')
            titleElement.textContent = response.titlePost

            const postElement = document.createElement('p')
            postElement.textContent = response.postBody

            const dashboard = document.getElementById('dashboard')
            dashboard.appendChild(titleElement)
            dashboard.appendChild(postElement)

            alert('Post uploaded successfully!');
            renderPost();
        } else {
            console.log('Error uploading post!');
            alert('Error uploading post!');
        }
    };

    xhttp.open('POST', '/upload', true)
    const formData = new FormData()
    formData.append('titlePost', titlePost)
    formData.append('postBody', postBody)

    xhttp.send(formData)
}

const deletePost = (postId) => {
    let xhttp = new XMLHttpRequest()
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            alert('Post deleted successfully!')
            const deletedPost = document.getElementById(postId)
            if (deletedPost) {
                deletedPost.remove()
            }
            renderPost();
        } else {
            console.error('Failed to delete post!')
            alert('Failed to delete post!')
        }
    }
    xhttp.open("DELETE", `/delete/${postId}`, true);
    xhttp.send();
}

const displayPost = (data) => {
    const items = data.result;
    console.log(loggedInUsername)

    let content = '';
    for (let i = 0; i < items.length; i++) {
        if (items[i].username === loggedInUsername) { 
            content +=
                `<div>
                    <h4>${items[i].username}</h4>
                    <h3>${items[i].title}</h3>
                    <p>${items[i].body}</p>
                    <p>${items[i].date}</p>
                    <a href="#" class="delete-link" onclick="deletePost('${items[i].post}')">Delete</a>
                </div>`;
        }
    }
    document.getElementById('dashboard').innerHTML = content;
};

const uploadFile = () => {
    let fileInput = document.getElementById('fileInput')
    let file = fileInput.files[0]

    let xhttp = new XMLHttpRequest()
    xhttp.onload = function() {
        if (xhttp.status === 200) {
            const response = JSON.parse(xhttp.responseText);

            const imgElement = document.createElement('img');
            imgElement.src = response.url;

            divResults.appendChild(imgElement);

            alert('File uploaded successfully!');
        } else {
            console.log('Error uploading file!');
            alert('Error uploading file!');
        }
    }

    xhttp.open('POST', '/profilepic', true);
    let formData = new FormData();
    formData.append('file', file);

    xhttp.send(formData);
}


function renderPost() {
    fetch('/dashboard')
        .then(response => response.json())
        .then(data => displayPost(data));
}

window.onload = function () {
    renderPost();
};


