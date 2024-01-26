function generateImage() {
    var formData = new FormData(document.getElementById("item-register-form"));

    console.log(formData);

    fetch('/generate_image_url', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.image_url) {
            console.log(data);
            var itemImage = document.getElementById("item-image");
            var particleImage = document.querySelector(".particle-image");
            var itemBox = document.querySelector(".item-box");
            var selectedQuality = document.querySelector('.radio-option-quality input[type="radio"]:checked').value;
            var titleBox = document.getElementById("title-box");
            var itemInputImage = document.getElementById("image-link").value;

            itemBox.classList.add(`border-${selectedQuality}`);
            itemImage.style.display = 'block';
            if (itemInputImage) {
                itemImage.src = itemInputImage;
            } else {
                itemImage.src = data.image_url;
            }
            if (data.particle_id) {
                particleImage.src = `static/tf2folio/particles/${data.particle_id}_188x188.png`;
                particleImage.style.display = 'block';
            } else {
                particleImage.src = '';
                particleImage.style.display = 'none';
            }
            if (data.item_title) {
                titleBox.innerHTML = data.item_title;
                titleBox.classList.add(selectedQuality);
            } else {
                titleBox.innerHTML = '';
            }
        } else {
            alert('Failed to generate image. Please enter your own image link.');
        }
    });
}