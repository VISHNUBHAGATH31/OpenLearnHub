// schoollevel.js

document.getElementById('ncertTile').addEventListener('click', function () {
    // Assuming you want to pass 'NCERT' as the board parameter
    redirectToBoard('NCERT');
});
document.getElementById('bseapTile').addEventListener('click', function () {
    // Assuming you want to pass 'NCERT' as the board parameter
    redirectToBoard('BSEAP');
});

function redirectToBoard(board) {
    // Redirect to board.html with the board parameter
    window.location.href = 'class.html?board=' + encodeURIComponent(board);
}
// schoollevel.js
