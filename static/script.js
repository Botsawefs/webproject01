// assets/script.js

// FIX: All pages use [data-theme="dark"] on <html>, NOT a class toggle.
// The old script toggled document.documentElement.classList ('dark')
// but style.css targeted body.dark-mode — they never matched.
// Now everything is unified: data-theme="dark" on <html>.

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? '' : 'dark');
    localStorage.setItem('theme', isDark ? 'light' : 'dark');

    const btn = document.getElementById('themeBtn');
    if (btn) btn.innerHTML = isDark ? '🌙' : '☀️';
}

// Apply saved theme immediately on every page load
window.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        const btn = document.getElementById('themeBtn');
        if (btn) btn.innerHTML = '☀️';
    }

    // Navbar scroll effect (used on pages with a transparent hero nav)
    const navbar = document.getElementById('navbar');
    if (navbar) {
        const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 60);
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // Scroll reveal
    const revealAll = () => {
        document.querySelectorAll('.reveal').forEach(el => {
            if (el.getBoundingClientRect().top < window.innerHeight - 80) {
                el.classList.add('active');
            }
        });
    };
    window.addEventListener('scroll', revealAll, { passive: true });
    revealAll(); // run once on load so above-fold elements show immediately

    // Live greeting on index page
    const greetEl = document.getElementById('greeting');
    if (greetEl) {
        const h = new Date().getHours();
        if      (h < 12) greetEl.textContent = 'Good Morning from Mahiyanganaya';
        else if (h < 18) greetEl.textContent = 'Good Afternoon from Mahiyanganaya';
        else             greetEl.textContent = 'Good Evening from Mahiyanganaya';
    }
});

// Global booking helper (used by Book Now buttons across the site)
function openBooking() {
    window.location.href = '/booking';
}

// --- MIYUGUNA AI INTERACTION ---

function toggleMiyuguna() {
    const chatWin = document.getElementById('chat-window');
    if (chatWin) {
        // Toggle a class instead of changing inline styles
        chatWin.classList.toggle('flex-active');
    } else {
        console.error("Miyuguna Error: Could not find #chat-window element");
    }
}

function sendMiyugunaMsg() {
    const input = document.getElementById('chat-input');
    const body = document.getElementById('chat-body');
    
    if (!input || !input.value.trim()) return;

    // 1. Add User Message
    const userMsg = document.createElement('div');
    userMsg.className = 'user-msg';
    userMsg.textContent = input.value;
    body.appendChild(userMsg);
    
    const text = input.value.toLowerCase();
    input.value = '';
    body.scrollTop = body.scrollHeight;

    // 2. Simple AI Logic (Replace with API call later)
    setTimeout(() => {
        let reply = "I'm not sure about that, but Sorabora Lake is beautiful this time of year!";
        if(text.includes('room')) reply = "We have 12 luxury rooms with lake views.";
        if(text.includes('hello') || text.includes('hi')) reply = "Ayubowan! Welcome to G.M.T. Sorabora.";

        const botMsg = document.createElement('div');
        botMsg.className = 'bot-msg';
        botMsg.textContent = reply;
        body.appendChild(botMsg);
        body.scrollTop = body.scrollHeight;
    }, 600);
}

// Global listener for the Enter key in chat
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'chat-input') {
        sendMiyugunaMsg();
    }
});