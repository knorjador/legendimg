
window.addEventListener('load', () => {

    // const models = {
    //     svc: { name: 'SVC', hyparams: { 'C': [1, 2, 3, 5, 10, 15, 20, 30, 50, 70, 100], 'tol': [0.1, 0.01, 0.001, 0.0001, 0.00001] } },
    //     lsvc: { name: 'LinearSVC', hyparams: { 'C': [1, 2, 3, 5, 10, 15, 20, 30, 50, 70, 100], 'tol': [0.1, 0.01, 0.001, 0.0001, 0.00001] } },
    //     dt: { name: 'DecisionTreeClassifier', hyparams: { 'max_depth': ['None', 10, 20, 30, 40, 50], 'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4] } },
    //     rf: { name: 'RandomForestClassifier', hyparams: { 'n_estimators': [50, 100, 200], 'max_depth': ['None', 10, 20, 30, 40, 50], 'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4] } }
    // }

    const models = {
        svc: { name: 'SVC', hyparams: { 'C': [1], 'tol': [0.1] } },
        lsvc: { name: 'LinearSVC', hyparams: { 'C': [1, 2], 'tol': [0.1, 0.01] } },
        dt: { name: 'DecisionTreeClassifier', hyparams: { 'max_depth': [10, 20], 'min_samples_split': [2, 5], 'min_samples_leaf': [1, 2] } },
        rf: { name: 'RandomForestClassifier', hyparams: { 'n_estimators': [50, 100], 'max_depth': [10, 20], 'min_samples_split': [2, 5], 'min_samples_leaf': [1, 2] } }
    }

    const 
        select_estimator = document.getElementById('select_estimator'),
        div_hyparams = document.getElementById('hyparams')

    let html_hyparams = '<div class="info_hyparams"><p>&#8505;</p> séparé par <p>,</p> pour plusieurs valeurs</div>'

    for (const hyparam in models.svc.hyparams) {
        const default_values = models.svc.hyparams[hyparam]
        html_hyparams += `
            <div class="div_hyparams">
                <label for="${hyparam}">
                    ${hyparam}
                </label>
                <input type="text" data-hyparams name="${hyparam}" value="${default_values.join(',')}"/>
            </div>
        `
    }

    div_hyparams.insertAdjacentHTML('afterbegin', html_hyparams)

    if (select_estimator) {
        select_estimator.addEventListener('change', event => {
            const 
                estimator = select_estimator.value,
                hyparams = models[estimator].hyparams

            div_hyparams.innerHTML = ''

            if (Object.keys(hyparams).length > 0) {
                let html_hyparams = '<div class="info_hyparams"><p>&#8505;</p> séparé par <p>,</p> pour plusieurs valeurs</div>'

                for (const hyparam in hyparams) {
                    const default_values = hyparams[hyparam]
                    html_hyparams += `
                        <div class="div_hyparams">
                            <label for="${hyparam}">
                                ${hyparam}
                            </label>
                            <input type="text" data-hyparams name="${hyparam}" value="${default_values.join(',')}"/>
                        </div>
                    `
                }

                div_hyparams.insertAdjacentHTML('afterbegin', html_hyparams)
            }
        })
    }

    const button_training = document.getElementById('button_training')

    if (button_training)
        button_training.addEventListener('click', async(event) => {
    
            event.preventDefault()

            const 
                form = document.getElementById('form_train'),
                loading = document.getElementById('loading'),
                loading_message = document.getElementById('loading_message'),
                form_message = document.getElementById('form_message'),
                model = document.querySelector('select[name="Model"]').value,
                input_hyparams = document.querySelectorAll("input[data-hyparams]")
                hyparams = {}

        
            form.style.display = 'none'
            loading.style.display = 'flex'
            form_message.textContent = ''

            for (const hyparam of input_hyparams)
                hyparams[hyparam.name] = hyparam.value.split(',').map(x => parseFloat(x))
                
            loading_message.innerHTML = `
                Entraînement avec l'estimateur <span style="font-weight: bold;">${models[model].name}</span> en cours...
                <br />
                <br />
                ${Object.keys(hyparams).length > 0 ? `<p>Hyper paramatètres</p><pre>${JSON.stringify(hyparams)}</pre>` : ''} 
            `

            const 
                access_token = localStorage.getItem('access_token'),
                data = {
                    access_token,
                    model,
                    hyparams
                }
        
            const request = await fetch("/train_sentiment", {

                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
                
            })
        
            const response = await request.json()
            console.log(response)

            form.style.display = 'flex'
            loading.style.display = 'none'
            loading_message.innerHTML = ''

            if (request.ok) {

                form_message.insertAdjacentHTML('afterbegin', `
                    <span>Score train accuracy: ${response.train_acc}</span>
                    <br>
                    <span>Score test accuracy: ${response.test_acc}</span>
                `)

                // setTimeout(() => form_message.textContent = "", 2222)
    
            } else {
                
                form_message.insertAdjacentHTML('afterbegin', `${response.message}`)

                if (response.detail) {

                    form_message.insertAdjacentHTML('afterbegin', `Jeton expiré : <a href="/">Authentification</a>`)

                } else {

                    form_message.textContent = `Désolé, une erreur lors la requête est survenue`

                    setTimeout(() => form_message.textContent = "", 2222)

                }
        
            }
        })

})


