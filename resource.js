async function openSubject(subject, classNumber) {
    try {
        const response = await fetch(`http://localhost:5000/getResources?class=${classNumber}&subject=${subject}`);
        const results = await response.json();

        // Check if the response has the 'results' property and is a JSON-formatted string
        if (results && results.results) {
            // Parse the 'results' property if it's a string
            const resultsArray = typeof results.results === 'string' ? JSON.parse(results.results) : results.results;
            // Call the displayResults function with the correct array
            displayResults(resultsArray);
        } else {
            console.error('Invalid or missing results in the response:', results);
        }
    } catch (error) {
        console.error('Error fetching or parsing results:', error);
    }
}

// Your displayResults function remains unchanged
async function displayResults(results) {
    const searchResultsContainer = document.getElementById('searchResultsContainer');
    const searchResults = document.getElementById('searchResults');

    // Clear previous results
    searchResults.innerHTML = '';

    try {
        // Check if results is an array
        if (Array.isArray(results)) {
            // Display the results
            results.forEach(result => {
                // Check if the result has necessary properties
                if (result && result.filepath && result.name) {
                    const resultElement = document.createElement('div');
                    resultElement.classList.add('result-item');

                    // Create an iframe for the PDF thumbnail
                    const pdfThumbnail = document.createElement('iframe');
                    pdfThumbnail.src = result.filepath;
                    pdfThumbnail.width = '100%';
                    pdfThumbnail.height = '200px'; // You can adjust the height as needed

                    // Create a paragraph for the name
                    const resultName = document.createElement('p');
                    resultName.textContent = result.name;

                    // Append the thumbnail and name to the result element
                    resultElement.appendChild(pdfThumbnail);
                    resultElement.appendChild(resultName);

                    // Attach a click event to open the full path in a new page
                    resultElement.addEventListener('click', () => {
                        window.open(result.filepath, '_blank');
                    });

                    // Append the result element to the search results
                    searchResults.appendChild(resultElement);
                } else {
                    // If there is no path or name, display a message or handle it accordingly
                    console.error('Result is missing necessary properties:', result);
                }
            });
        } else {
            console.error('Results is not an array:', results);
        }
    } catch (error) {
        console.error('Error displaying results:', error);
    }

    // Show the container
    searchResultsContainer.style.display = results.length > 0 ? 'flex' : 'none';
}
