
window.addEventListener('load', () => {

    if (document.getElementById("name"))
        document.getElementById("name").value = ""
    if (document.getElementById("password"))
        document.getElementById("password").value = ""

    const button_credentials = document.getElementById('button_credentials')

    if (button_credentials)
        button_credentials.addEventListener('click', async(event) => {
    
            event.preventDefault()
    
            const 
                form = document.getElementById('wrapper_form'),
                loading = document.getElementById('loading'),
                form_message = document.getElementById('form_message'),
                name = document.getElementById("name").value,
                password = document.getElementById("password").value

            if (name.length != 0 && password.length != 0) {
                 
                form.style.display = 'none'
                loading.style.display = 'flex'

                const request = await fetch('/auth', {

                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, password })
                    
                })

                const response = await request.json()
                console.log(response)

                if (request.ok) {

                    setTimeout(() => {
    
                        form.style.display = 'block'
                        loading.style.display = 'none'
        
                        if (response.success) {
        
                            const access_token = response.access_token
        
                            localStorage.setItem('access_token', access_token);
        
                            // window.location.assign(`/protected?token=${access_token}`)
                            window.location.assign(`/protected/${access_token}`)
        
                        } else {
                
                            form_message.textContent = response.message

                            setTimeout(() => form_message.textContent = "", 1000)

                        }
        
                    }, 1111)

                } else {

                    form.style.display = 'block'
                    loading.style.display = 'none'
        
                    form_message.textContent = `Désolé, une erreur avec la requête est survenue, code http : ${response.status}`

                    setTimeout(() => form_message.textContent = "", 1000)
                    
                }

            }
        })

})


