// DOM Elements
const navBtns = document.querySelectorAll('.nav-btn');
const appSections = document.querySelectorAll('.app-section');
const cardStack = document.querySelector('.card-stack');
const actionBtns = document.querySelectorAll('.action-btn');
const logoutBtn = document.getElementById('logout-btn');

// State Management
let currentCard = null;
let isDragging = false;
let startX = 0;
let currentX = 0;

// Navigation
navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const section = btn.dataset.section;
        
        // Update active nav button
        navBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Show corresponding section
        appSections.forEach(s => {
            s.classList.remove('active');
            if (s.id === `${section}-section`) {
                s.classList.add('active');
            }
        });
    });
});

// Card Stack Functionality
function initCardStack() {
    // TODO: Fetch potential matches from API
    const mockProfiles = [
        {
            name: 'Sarah',
            age: 25,
            bio: 'Adventure seeker & coffee lover',
            interests: ['Travel', 'Photography', 'Music'],
            image: 'https://via.placeholder.com/400x600'
        },
        // Add more mock profiles here
    ];
    
    // Create and add cards to stack
    mockProfiles.forEach(profile => {
        const card = createProfileCard(profile);
        cardStack.appendChild(card);
    });
    
    // Set up first card
    currentCard = cardStack.querySelector('.profile-card');
    if (currentCard) {
        setupCardDrag(currentCard);
    }
}

function createProfileCard(profile) {
    const card = document.createElement('div');
    card.className = 'profile-card';
    card.innerHTML = `
        <div class="card-image">
            <img src="${profile.image}" alt="${profile.name}">
        </div>
        <div class="card-info">
            <h2 class="name">${profile.name}, ${profile.age}</h2>
            <p class="bio">${profile.bio}</p>
            <div class="interests">
                ${profile.interests.map(interest => 
                    `<span class="interest-tag">${interest}</span>`
                ).join('')}
            </div>
        </div>
    `;
    return card;
}

function setupCardDrag(card) {
    card.addEventListener('mousedown', startDrag);
    card.addEventListener('touchstart', startDrag);
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag);
    
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
}

function startDrag(e) {
    isDragging = true;
    startX = e.type === 'mousedown' ? e.clientX : e.touches[0].clientX;
    currentCard.style.transition = 'none';
}

function drag(e) {
    if (!isDragging) return;
    
    e.preventDefault();
    currentX = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX;
    const diff = currentX - startX;
    
    currentCard.style.transform = `translateX(${diff}px) rotate(${diff * 0.1}deg)`;
    
    // Add like/dislike indication
    if (diff > 50) {
        currentCard.style.border = '2px solid #4CAF50';
    } else if (diff < -50) {
        currentCard.style.border = '2px solid #ff6b6b';
    } else {
        currentCard.style.border = 'none';
    }
}

function endDrag(e) {
    if (!isDragging) return;
    
    isDragging = false;
    const diff = currentX - startX;
    
    if (Math.abs(diff) > 100) {
        // Swipe threshold reached
        const direction = diff > 0 ? 'right' : 'left';
        handleSwipe(direction);
    } else {
        // Return card to center
        currentCard.style.transition = 'transform 0.3s ease';
        currentCard.style.transform = 'translateX(0) rotate(0)';
        currentCard.style.border = 'none';
    }
}

function handleSwipe(direction) {
    const action = direction === 'right' ? 'like' : 'dislike';
    
    // Animate card off screen
    currentCard.style.transition = 'transform 0.5s ease';
    currentCard.style.transform = `translateX(${direction === 'right' ? '100%' : '-100%'}) rotate(${direction === 'right' ? '30' : '-30'}deg)`;
    
    // Remove card after animation
    setTimeout(() => {
        currentCard.remove();
        
        // Set up next card
        currentCard = cardStack.querySelector('.profile-card');
        if (currentCard) {
            setupCardDrag(currentCard);
        } else {
            // No more cards
            cardStack.innerHTML = '<div class="no-more-profiles">No more profiles to show</div>';
        }
    }, 500);
    
    // TODO: Send like/dislike to API
    console.log(`User ${action}ed profile`);
}

// Action Buttons
actionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        if (!currentCard) return;
        
        const action = btn.classList.contains('like') ? 'right' : 'left';
        handleSwipe(action);
    });
});

// Logout functionality
logoutBtn.addEventListener('click', () => {
    // TODO: Implement actual logout API call
    window.location.href = 'index.html';
});

// Initialize app
initCardStack(); 