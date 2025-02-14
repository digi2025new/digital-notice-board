const socket = io(); // Automatically connects to the same host

socket.on('connect', function() {
    console.log('Connected to WebSocket server');
});

socket.on('update_notices', function(msg) {
    console.log('Received update:', msg);
    loadNotices(); // Reload notices when an update is received
});

let currentNoticeIndex = 0;
let noticesData = []; // Store the notice data

function loadNotices() {
    fetch('/notices') // Calls the Flask backend to get notices
        .then(response => response.json())
        .then(notices => {
            noticesData = notices;
            currentNoticeIndex = 0; // Reset index
            if (noticesData.length > 0) {
                displayNotice(currentNoticeIndex);
            } else {
                document.getElementById('notices').innerHTML = '<p>No notices to display.</p>';
            }
        })
        .catch(error => console.error('Error fetching notices:', error));
}

function displayNotice(index) {
    const noticesDiv = document.getElementById('notices');
    if (!noticesDiv) return; // Exit if the element doesn't exist

    if (noticesData.length === 0) {
        noticesDiv.innerHTML = '<p>No notices to display.</p>';
        return;
    }

    const notice = noticesData[index];
    let noticeHTML = '';

    if (notice.file_type === 'png' || notice.file_type === 'jpg' || notice.file_type === 'jpeg' || notice.file_type === 'gif') {
        noticeHTML = `<img src="${notice.file_path}" alt="${notice.title}" style="max-width:100%; max-height:500px;">`;
    } else if (notice.file_type === 'mp4') {
        noticeHTML = `<video src="${notice.file_path}" controls style="max-width:100%; max-height:500px;"></video>`;
    } else if (notice.file_type === 'mp3') {
        noticeHTML = `<audio src="${notice.file_path}" controls></audio>`;
    } else if (notice.file_type === 'txt') {
        noticeHTML = `<p>${notice.content}</p>`;
    } else {
        noticeHTML = `<p>Unsupported file type.</p>`;
    }
    noticesDiv.innerHTML = `<div class="notice">${noticeHTML}<h3>${notice.title}</h3></div>`;
}

function nextNotice() {
    if (noticesData.length === 0) return;
    currentNoticeIndex = (currentNoticeIndex + 1) % noticesData.length;
    displayNotice(currentNoticeIndex);
}

// Initial load and auto-refresh notices every 5 seconds
loadNotices();
setInterval(nextNotice, 5000);
