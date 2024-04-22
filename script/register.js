const createAccount = () => {
    let txtEmail = document.getElementById("txtEmail").value
    let txtPassword = document.getElementById("txtPassword").value

    if (txtEmail.value == '' || txtPassword.value == '') {
        alert("Email and password can not be blank.");
        return;
    }

    let xhttp = new XMLHttpRequest()
    xhttp.onload = function(){
        if (xhttp.status === 200) {
            const account = JSON.parse(xhttp.responseText)

            const emailElement = document.createElement('p')
            emailElement.textContent = account.txtEmail

            const passwordElement = document.createElement('p')
            passwordElement.textContent = account.txtPassword

            alert('Account created sucessfully!')
        } else {
            alert('Failed to create account')
        }
    }

    xhttp.open('POST', '/createaccount', true)
    const formData = new FormData()
    formData.append('txtEmail', txtEmail)
    formData.append('txtPassword', txtPassword)

    xhttp.send(formData)
}

