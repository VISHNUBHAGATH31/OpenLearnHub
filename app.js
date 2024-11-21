// app.js

function openClass(className) {
    var i;
    var classes = document.getElementsByClassName("class-content");
    for (i = 0; i < classes.length; i++) {
        classes[i].style.display = "none";
    }
    var selectedClass = document.getElementById(className);
    selectedClass.style.display = "block";
    selectedClass.classList.add("fade-in");
}

function openSubject(subject) {
    // Modify this function to handle the click on subjects
    // For now, it will log the selected subject to the console
    console.log('Selected Subject:', subject);
}
