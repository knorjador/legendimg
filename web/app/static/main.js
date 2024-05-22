

const submitCredentials = () => {
    const 
        form = document.getElementById('wrapper_form'),
        loading = document.getElementById('loading')
    
    form.style.display = 'none'
    loading.style.display = 'flex'
}

window.addEventListener('load', () => {

    const 
        queryString = window.location.search,
        params = new URLSearchParams(queryString),
        parameters = {}

    params.forEach((value, key) => { parameters[key] = value })

    console.log(parameters)

    if (parameters.e) {
        const form_message = document.getElementById('form_message')

        let message = ''

        form_message.style.display = 'block'

        if (parameters.e === '0') {
            message = 'Une erreur est survenue'    
        } else if (parameters.e === '1') {
            message = 'Identifiants incorrects'    
        } else if (parameters.e === '2') {
            message = 'Les mots de passe sont différents'    
        } else if (parameters.e === '3') {
            message = 'Les champs ne sont pas bien remplis'    
        }

        form_message.innerText = message

        setTimeout(() => form_message.style.display = 'none', 1500)
    }

})