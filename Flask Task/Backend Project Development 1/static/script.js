document.addEventListener('DOMContentLoaded', () => {
    const regexInput = document.getElementById('regexInput');
    const testInput = document.getElementById('testInput');

    regexInput.focus();

    const form = document.getElementById('regexForm');
    form.addEventListener('submit', () => {
        console.log('Searching for pattern: ' + regexInput.value);
    });
});