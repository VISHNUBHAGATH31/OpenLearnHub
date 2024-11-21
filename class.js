document.querySelectorAll('.class-content').forEach(classContent => {
    classContent.addEventListener('click', function(event) {
        var classNumber = this.getAttribute('data-class');

        // Hide all class content elements
        hideAllClasses();

        // Show the selected class content
        this.style.display = "block";
    });
});

// Event listener for subject links
document.querySelectorAll('.subject-link').forEach(subjectLink => {
    subjectLink.addEventListener('click', function(event) {
        event.preventDefault();
        var classNumber = this.closest('.class-content').getAttribute('data-class');
        var subject = this.getAttribute('data-subject');

        // Assuming you want to redirect to resource.html with parameters
        window.location.href = `resource.html?class=${classNumber}&subject=${subject}`;
    });
});