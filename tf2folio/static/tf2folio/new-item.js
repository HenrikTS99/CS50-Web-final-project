document.addEventListener('DOMContentLoaded', function() {
    generateImageButton = document.getElementById("generate-img-btn");
    generateImageButton.addEventListener('click', generateImage);
});

// Generate an image for the item preview
function generateImage() {
    var formData = new FormData(document.getElementById("item-register-form"));
    const itemErrorDisplay = document.getElementById("item-error-display");
    const itemImage = document.getElementById("item-image");
    console.log(formData);

    itemImage.style.display = 'block';
    fetch('/get_item_data', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.image_url) {
            console.log(data);
            
            const particleImage = document.querySelector(".particle-image");
            const itemBox = document.getElementById("item-preview-box");
            const selectedQuality = document.querySelector('.radio-option-quality input[type="radio"]:checked').value;
            const titleBox = document.getElementById("title-box");
            const itemInputImage = document.getElementById("image-link").value;

            itemErrorDisplay.innerHTML = '';
            itemErrorDisplay.style.display = 'none';
            itemBox.className = (`item-box border-${selectedQuality}`);
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
                titleBox.className = selectedQuality;
            } else {
                titleBox.innerHTML = '';
            }
        } else {
            itemErrorDisplay.innerHTML = 'Failed to generate image. Please enter your own image link.';
            itemErrorDisplay.style.display = 'block';
            itemImage.src = defaultImage;
        }
    });
}