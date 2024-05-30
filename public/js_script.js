document.addEventListener('DOMContentLoaded', function() {
    // Get the button element
    const button = document.querySelector('.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-edgeEnd.MuiIconButton-sizeSmall.css-2n4y0m');

    // Get the div element to hide
    const divToHide = document.querySelector('.MuiBox-root.css-144sd5e');

    // Add click event listener to the button
    button.addEventListener('click', function() {
        // Hide the div by setting its display to 'none'
        divToHide.style.display = 'none';
    });
});