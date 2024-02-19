document.addEventListener('DOMContentLoaded', function() {
    generateImageButton = document.getElementById("generate-img-btn");
    generateImageButton.addEventListener('click', generateImage);
});

// Generate and displays an image for the item preview
function generateImage() {
    const formData = new FormData(document.getElementById("item-register-form"));
    const itemErrorDisplay = document.getElementById("item-error-display");
    const itemImage = document.getElementById("item-image");
    const itemInputImage = document.getElementById("image-link").value;

    itemImage.style.display = 'block';
    fetch('/get_item_data', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        itemErrorDisplay.innerHTML = '';
        itemErrorDisplay.style.display = 'none';

        if (data.image_url) {
            const particleImage = document.querySelector(".particle-image");
            const itemBox = document.getElementById("item-preview-box");
            const selectedQuality = document.querySelector('.radio-option-quality input[type="radio"]:checked').value;
            const titleBox = document.getElementById("title-box");

            itemBox.className = (`item-box border-${selectedQuality}`);
            itemImage.src = itemInputImage ? itemInputImage : data.image_url;
            particleImage.style.display = data.particle_id ? 'block' : 'none';
            particleImage.src = data.particle_id ? `static/tf2folio/particles/${data.particle_id}_188x188.png` : '';
            titleBox.innerHTML = data.item_title ? data.item_title : '';
            titleBox.className = selectedQuality;

        } else if (itemInputImage) {
            itemImage.src = itemInputImage;
        } else {
            itemErrorDisplay.innerHTML = 'Failed to generate image. Please enter your own image link.';
            itemErrorDisplay.style.display = 'block';
            itemImage.src = defaultImage;
        }
    });
}