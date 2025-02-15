const API_BASE = window.location.origin;
let isProcessing = false;


const statusMessages = {
    pauseSent: "📩 Pause confirmation email sent. Check your inbox (and spam folder).",
    resumeSent: "📩 Resume confirmation email sent. Check your inbox (and spam folder).",
    deleteSent: "📩 Delete confirmation email sent. Check your inbox (and spam folder).",
    subSuccess: "🎉 Confirmation email sent! Check your inbox to activate.",
    subError: "⚠️ Error processing your request. Please try again.",
    invalidEmail: "❌ Please enter a valid email address",
    invalidUrl: "❌ Please enter a valid calendar URL",
    serverError: "🔧 Server error. Please try again later.",
    rateLimit: "⏳ Too many requests. Please wait before trying again.",
};


function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}


function showError(fieldId, errorId, message) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(errorId);
    field.classList.add('input-error');
    error.textContent = message;
    error.style.display = 'block';
}


function clearErrors() {
    document.querySelectorAll('.input-error').forEach(el => {
        el.classList.remove('input-error');
    });
    document.querySelectorAll('.error-message').forEach(el => {
        el.style.display = 'none';
    });
}


function showStatus(elementId, message, type, persistent = false) {
    const statusEl = document.getElementById(elementId);
    statusEl.innerHTML = message;
    statusEl.className = `status ${type}${persistent ? ' persistent' : ''}`;
    statusEl.style.display = 'block';

    if (!persistent) {
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}


async function handleError(response, fallbackMessage) {
    try {
        const error = await response.json();
        return error.detail || fallbackMessage;
    } catch {
        return fallbackMessage;
    }
}


async function handleSubscribe(event) {
    event.preventDefault();
    if (isProcessing) return;

    clearErrors();
    const urlInput = document.getElementById('calendarUrl');
    const url = urlInput.value.trim();

    isProcessing = true;
    toggleLoading(true);

    try {
        const response = await fetch(`${API_BASE}/subscribe?q=${encodeURIComponent(url)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const result = await response.json();

        if (!response.ok) {
            const errorMessage = result.detail || statusMessages.subError;
            showStatus('subscribeStatus', errorMessage, 'error', true);
            return;
        }

        showStatus('subscribeStatus', statusMessages.subSuccess, 'success');
        urlInput.value = '';
    } catch (error) {
        showStatus('subscribeStatus', statusMessages.serverError, 'error', true);
    } finally {
        isProcessing = false;
        toggleLoading(false);
    }
}


async function handlePause() {
    if (isProcessing) return;
    await handleManagementAction('request-pause');
}

async function handleResume() {
    if (isProcessing) return;
    await handleManagementAction('request-resume');
}

async function handleDelete() {
    if (isProcessing) return;
    await handleManagementAction('request-delete');
}

async function handleManagementAction(endpoint) {
    clearErrors();
    const emailInput = document.getElementById('userEmail');
    const email = emailInput.value.trim();

    isProcessing = true;
    toggleLoading(true);

    try {
        const response = await fetch(`${API_BASE}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });

        if (!response.ok) {
            const errorMessage = await handleError(response, statusMessages.subError);
            showStatus('manageStatus', errorMessage, 'error', true);
            return;
        }
        
        let successMessage = '';
        
        switch (endpoint) {
            case 'request-pause':
                successMessage = statusMessages.pauseSent;
                break;
            case 'request-resume':
                successMessage = statusMessages.resumeSent;
                break;
            case 'request-delete':
                successMessage = statusMessages.deleteSent;
                break;
        }

        showStatus('manageStatus', successMessage, 'success');
    } catch (error) {
        showStatus('manageStatus', statusMessages.serverError, 'error', true);
    } finally {
        isProcessing = false;
        toggleLoading(false);
    }
}


function toggleLoading(isLoading) {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.disabled = isLoading;
    });
    
    const loadingEl = document.getElementById('globalLoading');
    if (isLoading) {
        loadingEl.style.display = 'flex';
    } else {
        loadingEl.style.display = 'none';
    }
}


document.querySelectorAll('button').forEach(button => {
    button.dataset.originalText = button.innerHTML;
});


document.getElementById('subscribeForm').addEventListener('submit', handleSubscribe);


document.getElementById('userEmail').addEventListener('input', function() {
    if (!isValidEmail(this.value.trim())) {
        showError('userEmail', 'emailError', statusMessages.invalidEmail);
    } else {
        clearErrors();
    }
});


document.querySelectorAll('.status.persistent').forEach(el => {
    el.addEventListener('click', () => {
        el.style.display = 'none';
    });
});


function openManageModal() {
    document.getElementById('manageModal').classList.add('active');
}


function closeManageModal() {
    document.getElementById('manageModal').classList.remove('active');
}


function openModal(type) {
    const modal = document.getElementById('infoModal');
    const content = document.getElementById('infoModalContent');
    let html = '';

    switch(type) {
        case 'contact':
            html = `<h2>Contact</h2>
                            <p>For support, please email: admin@emilpopovic.me</p>`;
            break;
        case 'disclaimer':
            html = `<h2>Disclaimer</h2>
                            <p>This service is provided "as-is" without any warranties. 
                            We are not responsible for any missed events or notifications.</p>`;
            break;
        case 'github':
            html = `<h2>GitHub Repository</h2>
                            <p>Contribute or view the source code at:<br>
                            <a href="https://github.com/emil-popovic/calendar-notifications" target="_blank">
                                github.com/emil-popovic/calendar-notifications
                            </a></p>`;
            break;
    }
    content.innerHTML = html;
    modal.classList.add('active');
}

function closeInfoModal() {
    document.getElementById('infoModal').classList.remove('active');
}