document.addEventListener('DOMContentLoaded', () => {
    const hexDisplay = document.querySelector('.hex-value');

    if (hexDisplay) {
        hexDisplay.addEventListener('click', () => {
            const text = hexDisplay.innerText;
            
            // Copy to clipboard
            navigator.clipboard.writeText(text).then(() => {
                // Visual feedback
                const originalColor = hexDisplay.style.color;
                hexDisplay.style.color = "#1a73e8";
                alert("Hex code copied to clipboard: " + text);
                
                setTimeout(() => {
                    hexDisplay.style.color = originalColor;
                }, 500);
            });
        });
    }
});