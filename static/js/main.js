// DOM Elements
const videoForm = document.getElementById('videoForm');
const videoContainer = document.getElementById('videoContainer');
const editModal = document.getElementById('editModal');
const editForm = document.getElementById('editForm');
const searchInput = document.getElementById('searchInput');
const closeModal = document.querySelector('.close');

// State
let videos = [];

// Toast Notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// API Functions
async function fetchVideos() {
    try {
        const response = await fetch('/video/1'); // Fetch initial video to test
        if (response.ok) {
            const video = await response.json();
            videos = [video];
            renderVideos();
        }
    } catch (error) {
        showToast('Error fetching videos', 'error');
    }
}

async function addVideo(videoData) {
    try {
        const response = await fetch(`/video/${videoData.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...videoData,
                youtube_url: document.getElementById('youtubeUrl').value
            })
        });

        if (response.ok) {
            const newVideo = await response.json();
            videos.push(newVideo);
            renderVideos();
            showToast('Video added successfully');
        } else {
            const error = await response.json();
            showToast(error.message, 'error');
        }
    } catch (error) {
        showToast('Error adding video', 'error');
    }
}

async function updateVideo(videoData) {
    try {
        const response = await fetch(`/video/${videoData.id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(videoData)
        });

        if (response.ok) {
            const updatedVideo = await response.json();
            videos = videos.map(v => v.id === updatedVideo.id ? updatedVideo : v);
            renderVideos();
            closeEditModal();
            showToast('Video updated successfully');
        } else {
            const error = await response.json();
            showToast(error.message, 'error');
        }
    } catch (error) {
        showToast('Error updating video', 'error');
    }
}

async function deleteVideo(videoId) {
    try {
        const response = await fetch(`/video/${videoId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            videos = videos.filter(v => v.id !== videoId);
            renderVideos();
            showToast('Video deleted successfully');
        } else {
            const error = await response.json();
            showToast(error.message, 'error');
        }
    } catch (error) {
        showToast('Error deleting video', 'error');
    }
}

// UI Functions
function renderVideos(searchTerm = '') {
    const filteredVideos = videos.filter(video => 
        video.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    videoContainer.innerHTML = filteredVideos.map(video => `
        <div class="video-card" data-id="${video.id}">
            <h3>${video.name}</h3>
            <div class="stats">
                <span><i class="fas fa-eye"></i> ${video.views}</span>
                <span><i class="fas fa-heart"></i> ${video.likes}</span>
            </div>
            <div class="actions">
                <button class="btn-edit" onclick="openEditModal(${video.id})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn-delete" onclick="deleteVideo(${video.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}

function openEditModal(videoId) {
    const video = videos.find(v => v.id === videoId);
    if (!video) return;

    document.getElementById('editVideoId').value = video.id;
    document.getElementById('editVideoName').value = video.name;
    document.getElementById('editVideoViews').value = video.views;
    document.getElementById('editVideoLikes').value = video.likes;

    editModal.style.display = 'block';
}

function closeEditModal() {
    editModal.style.display = 'none';
    editForm.reset();
}

// Event Listeners
videoForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const videoData = {
        id: parseInt(document.getElementById('videoId').value),
        name: document.getElementById('videoName').value,
        views: parseInt(document.getElementById('videoViews').value),
        likes: parseInt(document.getElementById('videoLikes').value)
    };
    addVideo(videoData);
    videoForm.reset();
});

editForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const videoData = {
        id: parseInt(document.getElementById('editVideoId').value),
        name: document.getElementById('editVideoName').value,
        views: parseInt(document.getElementById('editVideoViews').value),
        likes: parseInt(document.getElementById('editVideoLikes').value)
    };
    updateVideo(videoData);
});

searchInput.addEventListener('input', (e) => {
    renderVideos(e.target.value);
});

closeModal.addEventListener('click', closeEditModal);

window.addEventListener('click', (e) => {
    if (e.target === editModal) {
        closeEditModal();
    }
});

document.getElementById('fetchYouTube').addEventListener('click', async () => {
    const button = document.getElementById('fetchYouTube');
    const youtubeUrl = document.getElementById('youtubeUrl').value;
    
    if (!youtubeUrl) {
        showToast('Please enter a YouTube URL', 'error');
        return;
    }

    button.classList.add('loading');
    
    try {
        const response = await fetch(`/video/1`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: 1,
                name: '',
                views: 0,
                likes: 0,
                youtube_url: youtubeUrl
            })
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('videoName').value = data.name;
            document.getElementById('videoViews').value = data.views;
            document.getElementById('videoLikes').value = data.likes;
            showToast('YouTube data fetched successfully');
        } else {
            const error = await response.json();
            showToast(error.message || 'Error fetching YouTube data', 'error');
        }
    } catch (error) {
        showToast('Error fetching YouTube data', 'error');
    } finally {
        button.classList.remove('loading');
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', fetchVideos);
