class UIManager {
    constructor() {
        this.loadingStates = new Map()
    }

    initializeModals() {
        // Store original button text for loading states
        document.querySelectorAll('button').forEach(button => button.dataset.originalText = button.innerHTML)
        
        // Make persistent status messages clickable to dismiss
        document.addEventListener('click', (e) => {
            if (e.target.matches('.status.persistent')) {
                e.target.style.display = 'none'
            }
        })
    }

    showError(fieldId, errorId, message) {
        const field = document.getElementById(fieldId)
        const error = document.getElementById(errorId)

        if (field) {
            field.classList.add('input-error')
        }
        if (error) {
            error.textContent = message
            error.style.display = 'block'
        }
    }

    clearErrors() {
        document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'))
        document.querySelectorAll('.error-message').forEach(el => el.style.display = 'none')
    }

    showStatus(elementId, message, type, persistent = false) {
        const statusEl = document.getElementById(elementId)
        if (!statusEl) {
            return
        }

        statusEl.innerHTML = message
        statusEl.className = `status ${type}${persistent ? ' persistent' : ''}`
        statusEl.style.display = 'block'

        if (!persistent) {
            setTimeout(() => {
                statusEl.style.display = 'none'
            }, 10000)
        }
    }

    setButtonLoading(action, loading) {
        const button = document.querySelector(`[data-action="${action}"], #${action}Button, .button[onclick*="${action}"]`)
        if (!button) {
            return
        }

        if (loading) {
            this.loadingStates.set(button, button.innerHTML)
            button.innerHTML = button.dataset.originalText || button.innerHTML
            button.disabled = true
        } else {
            const originalText = this.loadingStates.get(button) || button.dataset.originalText
            if (originalText) {
                button.innerHTML = originalText
            }
            button.disabled = false
            this.loadingStates.delete(button)
        }
    }

    openModal(modalId, content = null) {
        const modal = document.getElementById(modalId)
        if (!modal) {
            return
        }

        if (content && modalId === 'infoModal') {
            const contentEl = document.getElementById('infoModalContent')
            if (contentEl) {
                contentEl.innerHTML = content
            }
        }

        modal.classList.add('active')
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId)
        if (modal) {
            modal.classList.remove('active')
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => modal.classList.remove('active'))
    }
}
