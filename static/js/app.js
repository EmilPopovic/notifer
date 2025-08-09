class NotiFERApp {
    constructor() {
        this.api = new ApiClient()
        this.ui = new UIManager()
        this.i18n = new I18n()
        this.init()
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeApp())
        } else {
            this.initializeApp()
        }
    }

    initializeApp() {
        this.initializeLocalization()
        this.bindEvents()
        this.ui.initializeModals()
    }

    initializeLocalization() {
        this.updateUILanguage()
        this.addLanguageSwitcher()
        this.watchLanguageChanges()
    }

    updateUILanguage() {
        const locale = this.i18n.locale
        document.documentElement.lang = locale

        // Update all translatable elements
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n')
            const translation = this.i18n.t(key)

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.type === 'text' || element.type === 'email') {
                    element.placeholder = translation
                }
            } else {
                element.textContent = translation
            }
        })

        this.updateModalContent()
    }

    updateModalContent() {
        // Update modal content based on current language
        const modalContents = {
            howto: this.i18n.t('modals.howto'),
            contact: this.i18n.t('modals.contact'),
            disclaimer: this.i18n.t('modals.disclaimer'),
            github: this.i18n.t('modals.github')
        }

        // Store for modal usage
        window.modalContents = modalContents
    }

    watchLanguageChanges() {
        document.addEventListener('languageChanged', () => this.updateUILanguage())
    }

    addLanguageSwitcher() {
        const existingSwitcher = document.querySelector('.language-switcher')
        if (existingSwitcher) {
            existingSwitcher.remove()
        }

        const langSwitcher = document.createElement('div')
        langSwitcher.className = 'language-switcher'
        langSwitcher.innerHTML = `
            <button onclick="app.switchLanguage('hr')" class="${this.i18n.locale === 'hr' ? 'active' : ''}">HR</button>
            <button onclick="app.switchLanguage('en')" class="${this.i18n.locale === 'en' ? 'active' : ''}">EN</button>
        `

        const hero = document.querySelector('.hero')
        if (hero) {
            hero.appendChild(langSwitcher)
        }
    }

    switchLanguage(locale) {
        this.i18n.setLocale(locale)
        this.updateUILanguage()
        
        // Update active language button
        document.querySelectorAll('.language-switcher button').forEach(btn => btn.classList.remove('active'))
        const activeBtn = document.querySelector(`.language-switcher button[onclick*="${locale}"]`)
        if (activeBtn) {
            activeBtn.classList.add('active')
        }

        document.dispatchEvent(new CustomEvent('languageChanged', { detail: { locale } }))
    }

    bindEvents() {
        // Subscribe form
        const subscribeForm = document.getElementById('subscribeForm')
        if (subscribeForm) {
            subscribeForm.addEventListener('submit', (e) => this.handleSubscribe(e))
        }

        // Email validation
        const emailInput = document.getElementById('userEmail')
        if (emailInput) {
            emailInput.addEventListener('input', (e) => this.validateEmail(e))
        }

        // Management actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                const action = e.target.getAttribute('data-action')
                this.handleManagementAction(action)
            }
        })

        // Modal events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.ui.closeAllModals()
            }
        })

        // Close modal on overlay click
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-overlay')) {
                this.ui.closeModal(e.target.id)
            }
        })
    }

    async handleSubscribe(event) {
        event.preventDefault()

        this.ui.clearErrors()
        const urlInput = document.getElementById('calendarUrl')
        const url = urlInput.value.trim()

        if (url.startsWith('https://www.fer.unizg.hr/kalendar')) {
            this.ui.showStatus('subscribeStatus', this.i18n.t('errors.notThatLink'), 'error', true)
            return
        }

        const successMessage = this.i18n.t('message.subscriptionEmailSent')

        try {
            this.ui.setButtonLoading('subscribe', true)

            const result = await this.api.subscribe(url)

            this.ui.showStatus('subscribeStatus', successMessage, 'success')
            urlInput.value = ''

        } catch (error) {
            const message = this.getErrorMessage(error)
            this.ui.showStatus('subscribeStatus', message, 'error', true)
        } finally {
            this.ui.setButtonLoading('subscribe', false)
        }
    }

    async handleManagementAction(action) {
        this.ui.clearErrors()
        const emailInput = document.getElementById('userEmail')
        const email = emailInput.value.trim()

        if (!this.isValidEmail(email)) {
            this.ui.showError('userEmail', 'emailError', this.i18n.t('errors.invalidEmail'))
            return
        }

        try {
            this.ui.setButtonLoading(action, true)
            await this.api.managementAction(action, email)

            const successKey = `message.${action}Sent`

            console.log('Action:', action)
            console.log('Success key:', successKey)
            console.log('Current locale:', this.i18n.locale)
            console.log('Translation result:', this.i18n.t(successKey))
            console.log('Translation object:', translations[this.i18n.locale].message)

            this.ui.showStatus('manageStatus', this.i18n.t(successKey), 'success')
        } catch (error) {
            const message = this.getErrorMessage(error)
            this.ui.showStatus('manageStatus', message, 'error', true)
        } finally {
            this.ui.setButtonLoading(action, false)
        }
    }

    validateEmail(event) {
        const email = event.target.value.trim()
        if (email && !this.isValidEmail(email)) {
            this.ui.showError('userEmail', 'emailError', this.i18n.t('errors.invalidEmail'))
        } else {
            this.ui.clearErrors()
        }
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    }

    getErrorMessage(error) {
        if (error.error_code) {
            const key = `errors.${error.error_code}`
            return this.i18n.t(key, error.details || {})
        }
        return this.i18n.t('errors.serverError')
    }
}

document.addEventListener('DOMContentLoaded', () => window.app = new NotiFERApp())
