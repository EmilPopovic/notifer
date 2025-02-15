const API_BASE = window.location.origin;
let isProcessing = false;


const statusMessages = {
    pauseSent: "📩 Pause confirmation email sent. Check your inbox (and spam folder).",
    resumeSent: "📩 Resume confirmation email sent. Check your inbox.",
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

async function handleManagementAction(endpoint) {
    clearErrors();
    const emailInput = document.getElementById('userEmail');
    const email = emailInput.value.trim();

    if (!isValidEmail(email)) {
        showError('userEmail', 'emailError', statusMessages.invalidEmail);
        emailInput.focus();
        return;
    }

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

        const successMessage = endpoint === 'request-pause'
            ? statusMessages.pauseSent
            : statusMessages.resumeSent;

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
        if (isLoading) {
            button.innerHTML = '⏳ Processing...';
            button.classList.add('loading');
        } else {
            button.innerHTML = button.dataset.originalText;
            button.classList.remove('loading');
        }
    });
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


document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.querySelector('.manage-subscription-toggle');
    const manageContent = document.querySelector('#manageSubscriptionContent');

    toggleButton.addEventListener('click', () => {
        manageContent.classList.toggle('open');
    });
});