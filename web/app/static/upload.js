

const submitAnnotate = async() => {

    if (FILE && FILE.name && FILE.url) {

        const 
            form = document.getElementById('dd_container'),
            loading = document.getElementById('loading'),
            loading_annotate = document.getElementById('loading_annotate'),
            data = { filename: FILE.name, url: FILE.url }

        form.style.display = 'none'
        loading.style.display = 'flex'
        
        setTimeout(() => {
            loading_annotate.innerHTML = `Annotation en cours`
        }, 1300)
    
        const request = await fetch('http://localhost:5000/upload', {
    
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
    
        })
    
        const response = await request.json()
    
        console.log(response)
    
        if (request.ok) {
            
            setTimeout(() => {
    
                loading.style.display = 'none'

                const 
                    caption = response.caption,
                    trad = response.trad,
                    sentiment = response.sentiment,
                    caption_container = document.getElementById('caption_container')

                caption_container.style.display = 'inline-block'
                caption_container.insertAdjacentHTML('afterbegin', `
                    <p style="font-size: 16px;font-style: italic;" class="caption">${caption}</p>
                    <p class="caption">Sentiment : ${sentiment.trad} <span style="font-size: 40px;">${sentiment.smiley}</span></p>
                    <p class="caption">${trad}</p>
                    <img style="margin: auto" src='${FILE.url}' alt=${caption}>
                `)

                document.getElementById('button_redo').addEventListener('click', () => location.reload())
    
            }, 1111)
    
        } else {
            
            form.style.display = 'inline-block'
            loading.style.display = 'none'
            loading_annotate.textContent = `Désolé, une erreur avec la requête est survenue, code http : ${response.status}`
    
            setTimeout(() => loading_annotate.textContent = "", 1111)
    
        }

    }

}

let FILE

window.addEventListener('load', () => {

    const 
        dropArea = document.querySelector('.drag_area'),
        dragText = document.querySelector('.header')

    let 
        button = dropArea.querySelector('.button'),
        input = dropArea.querySelector('input')

    button.onclick = () => input.click()

    // when browse
    input.addEventListener('change', function() {
        console.log(this.files)
        FILE = this.files[0]
        console.log('browse')
        // console.log(FILE)
        dropArea.classList.add('active')
        displayFile()
    })
    
    // when file is inside drag area
    dropArea.addEventListener('dragover', event => {
        event.preventDefault()
        dropArea.classList.add('active')
        dragText.textContent = 'Relâcher pour charger'
    })
  
    // when file leave the drag area
    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('active')
        dragText.textContent = 'Glisser && déposer'
    })
  
    // when file is dropped
    dropArea.addEventListener('drop', event => {
        event.preventDefault()
        console.log(event.dataTransfer.files)
        FILE = event.dataTransfer.files[0]
        // file = event.dataTransfer.files
        console.log('drag')
        // console.log(FILE)
        displayFile()
    })
  
    const displayFile = () => {
        let 
            fileType = FILE.type,
            validExtensions = ['image/jpeg', 'image/jpg', 'image/png']

        console.log(fileType)
    
        if (validExtensions.includes(fileType)) {
            let fileReader = new FileReader()
    
            fileReader.onload = () => {
                let fileURL = fileReader.result

                // console.log(fileURL)
        
                FILE.url = fileURL

                let imgTag = `<img src="${fileURL}" alt="">`

                dropArea.innerHTML = imgTag
            }

            fileReader.readAsDataURL(FILE)

            const can_cancel = document.getElementById('button_cancel')

            can_cancel.style.display = 'inline-block'
            can_cancel.addEventListener('click', () => location.reload())
        } else {
            alert('Ce fichier n\'est pas une image')

            dropArea.classList.remove('active')
        }
    }

    document.getElementById('button_annotate').addEventListener('click', submitAnnotate)

})







