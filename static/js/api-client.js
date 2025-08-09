class ApiClient {
    constructor() {
        this.baseUrl = window.location.origin
    }

    async subscribe(url) {
        const currentLanguage = window.app?.i18n?.locale || 'hr'

        const response = await fetch(`${this.baseUrl}/subscribe?q=${encodeURIComponent(url)}&language=${currentLanguage}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        return this.handleResponse(response)
    }

    async managementAction(action, email) {
        const response = await fetch(`${this.baseUrl}/request-${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        })

        return this.handleResponse(response)
    }

    async handleResponse(response) {
        const data = await response.json()

        if (!response.ok) {
            if (data.detail && typeof data.detail === 'object' && data.detail.error_code) {
                throw {
                    error_code: data.detail.error_code,
                    details: data.detail.details || {}
                }
            } else {
                throw {
                    error_code: 'UNKNOWN_ERROR',
                    message: data.detail || 'An error occurred'
                }
            }
        }

        return data
    }
}
