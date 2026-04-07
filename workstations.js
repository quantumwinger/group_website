// --- CONFIGURATION ---
const GROUP_PASSCODE = "dasgupta";

// To use Google Sheets for device synchronization, set this to true and follow instructions in google_apps_script_setup.md
const USE_GOOGLE_SHEETS = true;
const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyHe_g6QmJh7q5yzliptlZX9kdeSn2G0voeN4nxhirRZbY9sXWWvpG70nV5-wBFusgE/exec";

// --- STATE & UTILS ---
let bookingsCache = [];
let currentUser = "";
let pendingDeleteId = null;

// Simple ID generator
const generateId = () => Math.random().toString(36).substr(2, 9);

// Format date for display
const formatDateTime = (isoString) => {
    const d = new Date(isoString);
    return d.toLocaleString('en-US', {
        month: 'short', day: 'numeric',
        hour: 'numeric', minute: '2-digit', hour12: true
    });
};

// Check if a time is between start and end
const isCurrentlyActive = (start, end) => {
    const now = new Date().getTime();
    return now >= new Date(start).getTime() && now <= new Date(end).getTime();
};

// Check for overlaps
const checkOverlap = (ws, start, end, excludeId = null) => {
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();

    return bookingsCache.some(b => {
        if (b.workstation != ws || b.id === excludeId) return false;
        const bStart = new Date(b.startTime).getTime();
        const bEnd = new Date(b.endTime).getTime();

        // Overlap condition:
        // Max(Start A, Start B) < Min(End A, End B)
        return Math.max(startTime, bStart) < Math.min(endTime, bEnd);
    });
};

// --- BACKEND MANAGER ---
class BookingManager {
    static async fetchBookings() {
        if (USE_GOOGLE_SHEETS && GOOGLE_SCRIPT_URL) {
            try {
                const response = await fetch(GOOGLE_SCRIPT_URL);
                if (!response.ok) throw new Error('Failed to fetch from Google Sheets');
                const data = await response.json();
                if (data && data.error) throw new Error(data.error);
                bookingsCache = Array.isArray(data) ? data : [];
                updateSyncStatus(true);
            } catch (e) {

                console.error(e);
                updateSyncStatus(false, "Cannot connect to Google Sheets");
                // fallback to local if failed
                this.loadFromLocal();
            }
        } else {
            this.loadFromLocal();
            updateSyncStatus(false);
        }
        return bookingsCache;
    }

    static loadFromLocal() {
        const data = localStorage.getItem('workstation-bookings');
        if (data) {
            bookingsCache = JSON.parse(data);
        } else {
            bookingsCache = [];
        }
    }

    static async addBooking(booking) {
        if (checkOverlap(booking.workstation, booking.startTime, booking.endTime)) {
            throw new Error("Time slot overlaps with an existing booking.");
        }

        bookingsCache.push(booking);

        if (USE_GOOGLE_SHEETS && GOOGLE_SCRIPT_URL) {
            try {
                // To avoid CORS preflight, we send as text/plain. The script handles postData.contents.
                await fetch(GOOGLE_SCRIPT_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: JSON.stringify({ action: 'add', ...booking })
                });
            } catch (e) {
                console.error("Failed to sync to Google Sheets", e);
            }
        } else {
            localStorage.setItem('workstation-bookings', JSON.stringify(bookingsCache));
        }

        renderDashboard();
    }

    static async deleteBooking(id) {
        bookingsCache = bookingsCache.filter(b => b.id !== id);

        if (USE_GOOGLE_SHEETS && GOOGLE_SCRIPT_URL) {
            try {
                await fetch(GOOGLE_SCRIPT_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: JSON.stringify({ action: 'delete', id: id })
                });
            } catch (e) {
                console.error("Failed to delete on Google Sheets", e);
            }
        } else {
            localStorage.setItem('workstation-bookings', JSON.stringify(bookingsCache));
        }

        renderDashboard();
    }
}

// --- UI LOGIC ---

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();

    // Login Form
    document.getElementById('login-btn').addEventListener('click', handleLogin);

    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        sessionStorage.removeItem('ws-auth');
        sessionStorage.removeItem('ws-user');
        window.location.reload();
    });

    // Modals
    document.getElementById('new-booking-btn').addEventListener('click', () => {
        document.getElementById('booking-error').style.display = 'none';

        // Auto-fill time to next half hour
        const now = new Date();
        now.setMinutes(Math.ceil(now.getMinutes() / 30) * 30);
        now.setSeconds(0, 0);

        // Adjust for timezone offset for proper datetime-local input string
        const offset = now.getTimezoneOffset() * 60000;
        const localISOTime = (new Date(now - offset)).toISOString().slice(0, 16);

        document.getElementById('start-time').value = localISOTime;
        document.getElementById('booking-modal').classList.add('active');
    });

    document.getElementById('close-booking').addEventListener('click', () => {
        document.getElementById('booking-modal').classList.remove('active');
    });

    // Cancel Modal Logic
    document.getElementById('cancel-no-btn').addEventListener('click', () => {
        document.getElementById('cancel-modal').classList.remove('active');
        pendingDeleteId = null;
    });

    document.getElementById('cancel-yes-btn').addEventListener('click', () => {
        if (pendingDeleteId) {
            const btn = document.getElementById('cancel-yes-btn');
            btn.textContent = 'Canceling...';
            btn.disabled = true;

            BookingManager.deleteBooking(pendingDeleteId).then(() => {
                document.getElementById('cancel-modal').classList.remove('active');
                pendingDeleteId = null;
                btn.textContent = 'Yes, Cancel';
                btn.disabled = false;
            });
        }
    });

    // Booking Submission
    document.getElementById('booking-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const btn = document.getElementById('submit-booking-btn');
        btn.textContent = "Booking...";
        btn.disabled = true;

        const workstation = document.getElementById('workstation-select').value;
        const startTime = document.getElementById('start-time').value;
        const durationHours = parseFloat(document.getElementById('duration').value);

        const startObj = new Date(startTime);
        const endObj = new Date(startObj.getTime() + durationHours * 60 * 60 * 1000);

        try {
            await BookingManager.addBooking({
                id: generateId(),
                workstation,
                user: currentUser,
                startTime: startObj.toISOString(),
                endTime: endObj.toISOString()
            });
            document.getElementById('booking-modal').classList.remove('active');
        } catch (err) {
            const errorEl = document.getElementById('booking-error');
            errorEl.textContent = err.message;
            errorEl.style.display = 'block';
        } finally {
            btn.textContent = "Confirm Booking";
            btn.disabled = false;
        }
    });

    // Periodic Sync (every 30 seconds if Google Sheets is enabled)
    setInterval(() => {
        if (USE_GOOGLE_SHEETS && GOOGLE_SCRIPT_URL && currentUser) {
            BookingManager.fetchBookings().then(renderDashboard);
        }
    }, 30000);

    // Cross-tab sync for localStorage (if no Google sheets)
    window.addEventListener('storage', (e) => {
        if (e.key === 'workstation-bookings' && !USE_GOOGLE_SHEETS) {
            BookingManager.loadFromLocal();
            renderDashboard();
        }
    });
});

function checkAuth() {
    if (sessionStorage.getItem('ws-auth') === 'true') {
        currentUser = sessionStorage.getItem('ws-user') || "User";
        document.getElementById('login-modal').classList.remove('active');
        initDashboard();
    }
}

function handleLogin() {
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('passcode').value;

    if (user && pass === GROUP_PASSCODE) {
        sessionStorage.setItem('ws-auth', 'true');
        sessionStorage.setItem('ws-user', user);
        currentUser = user;
        document.getElementById('login-modal').classList.remove('active');
        initDashboard();
    } else {
        document.getElementById('login-error').style.display = 'block';
    }
}

async function initDashboard() {
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('display-name').textContent = currentUser;

    // Initial fetch and render
    await BookingManager.fetchBookings();
    renderDashboard();
}

function updateSyncStatus(isGoogleSheets, errorMsg = null) {
    const el = document.getElementById('sync-status');
    const textEl = el.querySelector('.status-text');

    if (isGoogleSheets) {
        el.classList.add('online');
        textEl.textContent = 'Synced with Server';
    } else {
        el.classList.remove('online');
        textEl.textContent = errorMsg ? `Error: ${errorMsg}` : 'Local Storage Only';
    }
}

function renderDashboard() {
    // Clean old bookings (older than 24 hours ago)
    const now = new Date().getTime();
    bookingsCache = bookingsCache.filter(b => {
        const endTime = new Date(b.endTime).getTime();
        return endTime > (now - 24 * 60 * 60 * 1000); // keep recent past and future
    });

    // Sort ascending by time
    bookingsCache.sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime());

    [1, 2, 3].forEach(wsId => {
        const wsBookings = bookingsCache.filter(b => parseInt(b.workstation) === wsId);
        const container = document.getElementById(`ws${wsId}-bookings`);
        const statusBadge = document.getElementById(`ws${wsId}-status`);

        container.innerHTML = ''; // clear

        let isCurrentlyInUse = false;

        if (wsBookings.length === 0) {
            container.innerHTML = `<p style="color: var(--text-muted); text-align: center; padding: 2rem 0;">No upcoming bookings.</p>`;
        } else {
            wsBookings.forEach(b => {
                const isActive = isCurrentlyActive(b.startTime, b.endTime);
                if (isActive) isCurrentlyInUse = true;

                // Past bookings (ended) are grayed out. They are kept if within 24hr.
                const isPast = new Date(b.endTime).getTime() < now;

                const div = document.createElement('div');
                div.className = `booking-item ${isActive ? 'active-now' : ''}`;
                if (isPast) div.style.opacity = '0.5';

                div.innerHTML = `
                    <div class="booking-user">${b.user} ${isActive ? '(In Use Now)' : ''}</div>
                    <div class="booking-time">${formatDateTime(b.startTime)} - ${formatDateTime(b.endTime)}</div>
                    ${(b.user === currentUser && !isPast) ?
                        `<button class="delete-booking-btn" onclick="deleteBooking('${b.id}')" title="Cancel Booking">&times;</button>` : ''}
                `;
                container.appendChild(div);
            });
        }

        // Update status badge
        if (isCurrentlyInUse) {
            statusBadge.textContent = 'In Use';
            statusBadge.className = 'status-badge badge-in-use';
        } else {
            statusBadge.textContent = 'Available';
            statusBadge.className = 'status-badge badge-available';
        }
    });

    // Refresh every minute to update "Active" states automatically
    scheduleNextMinuteRender();
}

let timeoutId;
function scheduleNextMinuteRender() {
    if (timeoutId) clearTimeout(timeoutId);
    // Render precisely at the top of the next minute
    const now = new Date();
    const delay = 60000 - (now.getSeconds() * 1000 + now.getMilliseconds());
    timeoutId = setTimeout(() => {
        renderDashboard();
    }, delay);
}

window.deleteBooking = (id) => {
    pendingDeleteId = id;
    document.getElementById('cancel-modal').classList.add('active');
};
