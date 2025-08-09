const translations = {
    en: {
        // Page content
        title: 'NotiFER',
        heroText: 'Never miss a schedule change!',
        subscribeText: 'Subscribe to notifications',
        subscribeButton: 'Subscribe',
        manageButton: 'Want to manage your subscription?',
        manageModalTitle: 'Manage subscription',
        pauseButton: 'Pause notifications',
        resumeButton: 'Resume notifications',
        deleteButton: 'Delete account',
        manageNotice: 'Changes take effect only after email confirmation.',
        contact: 'Contact',
        info: 'Info',
        github: 'GitHub',
        
        // Placeholders
        placeholders: {
            calendarUrl: 'Paste your FER calendar link',
            userEmail: 'Enter your registered email'
        },

        // Error messages
        errors: {
            SUBSCRIPTION_NOT_FOUND: 'Subscription not found.',
            SUBSCRIPTION_ALREADY_ACTIVE: 'Subscription already activated.',
            INVALID_CALENDAR_URL: 'Invalid calendar URL.',
            INVALID_ICAL_DOCUMENT: 'Invalid iCal document at the URL.',
            NOTIFICATIONS_ALREADY_PAUSED: 'Notifications are already paused.',
            NOTIFICATIONS_ALREADY_ACTIVE: 'Notifications are already active.',
            RATE_LIMIT_EXCEEDED: 'Too many requests. Try again in {retry_after_minutes} minutes.',
            INVALID_TOKEN: 'This link is invalid or expired.',
            invalidEmail: 'Please enter a valid email.',
            invalidUrl: 'Please enter a valid calendar URL.',
            serverError: 'Server error. Please try again later.',
            notThatLink: 'That\'s not the link we\'re looking for. Check (?) for more info.'
        },

        // Success messages
        message: {
            subscriptionEmailSent: 'Confirmation email sent! Check your inbox (and spam) to activate notifications.',
            pauseSent: 'Pause confirmation email sent. Check your inbox (and spam).',
            resumeSent: 'Resume confirmation email sent. Check your inbox (and spam).',
            deleteSent: 'Delete confirmation email sent. Check your inbox (and spam).'
        },

        // Modal content
        modals: {
            howto: `
                <h2>How to get the link?</h2>
                <p>Your FER calendar link is <b>not</b> <a href="https://www.fer.unizg.hr/kalendar">
                https://www.fer.unizg.hr/kalendar</a>, but you still need to go to that page! Below the 
                bottom right corner of the calendar, there's a "Download my activities in iCal format" button. 
                Don't click it! Right-click (or long press on mobile) to copy the link. The format 
                is https://www.fer.unizg.hr/_downloads/calevent/mycal.ics?user=[your_username]&auth=[your_token]. 
                That's the link you need to enter in NotiFER.</p>
            `,
            contact: `
                <h2>Contact</h2>
                <p>For support and questions, send an email to <a href="mailto:admin@emilpopovic.me">admin@emilpopovic.me</a>.</p>
            `,
            disclaimer: `
                <h2 id="-info">Info</h2>
                <p>This service is available as-is and exclusively for the convenience of fellow students. <strong>I am 
                a student who independently develops this tool</strong> and am not in any way connected to FER, approved by 
                it, or officially associated with it. <strong>Use at your own risk</strong>. I cannot 
                be held responsible for missed classes, laboratory exercises, and other consequences that may 
                arise from errors, delays, or deviations in schedule notifications. <strong>Always check 
                your schedule on the official FER website.</strong></p>
                <h3 id="-service-scope-and-responsibility">Service Scope and Responsibility</h3>
                <ul>
                    <li><strong>Experimental nature:</strong> This tool is experimental and may contain bugs.
                    Always check the official schedule.</li>
                    <li><strong>User responsibility:</strong> The user is responsible for checking the schedule. I am not
                    responsible for users missing classes.</li>
                </ul>
                <h3 id="-data-collection-and-security">Data Collection and Security</h3>
                <ul>
                    <li><strong>What is collected:</strong> The only thing this application collects is your FER email address 
                    (e.g., pi31415@fer.hr), calendar authentication token, and the previous version of your calendar.</li>
                    <li><strong>Data handling:</strong> All data is securely stored and the application is hosted locally in Zagreb, 
                    and emails are sent using Resend.com.</li>
                    <li><strong>Your consent:</strong> By using this service, you consent to this data handling.
                    Although every effort is made to protect your data, no system can be 100% secure.</li>
                    <li><strong>Data deletion:</strong> All data can be deleted using the &quot;Delete 
                    account&quot; function. The only thing needed for data deletion is access to the fer.hr email. If this
                    doesn't suit you, send me a message.</li>
                </ul>
                <h3 id="-service-availability-and-changes">Service Availability and Changes</h3>
                <ul>
                    <li><strong>No service guarantee:</strong> I may modify, temporarily suspend,
                    or shut down this service at any time. In that case, I will try to ensure that users receive notification of 
                    service termination.</li>
                    <li><strong>Reliability:</strong> I aim for the highest possible reliability, but cannot guarantee uninterrupted 
                    access and perfect functionality.</li>
                    <li><strong>External changes:</strong> This application depends on services I do not control - 
                    FER's calendar and email systems - which can change at any time. I am not responsible for such 
                    interruptions.</li>
                </ul>
                <h2 id="-message-to-user">Message to User</h2>
                <p>The points above sound scary, but I also depend on and trust this application myself. What I want to say is... 
                    <strong>Don't blame me if you're late to lab!!!</strong> :3</p>
            `,
            github: `
                <h2>GitHub Repository</h2>
                <p>NotiFER is open source! Available on GitHub:<br>
                <a href="https://github.com/myolnyr/NotiFER" target="_blank">github.com/myolnyr/NotiFER</a>
                </p>
            `
        }
    },
    hr: {
        // Page content
        title: 'NotiFER',
        heroText: 'Nikad ne propusti promjenu u rasporedu!',
        subscribeText: 'Pretplati se na obavijesti',
        subscribeButton: 'Pretplati se',
        manageButton: 'Želiš urediti svoju pretplatu?',
        manageModalTitle: 'Uredi pretplatu',
        pauseButton: 'Pauziraj obavijesti',
        resumeButton: 'Uključi obavijesti',
        deleteButton: 'Izbriši račun',
        manageNotice: 'Promjena se provodi tek nakon potvrde mailom.',
        contact: 'Kontakt',
        info: 'Info',
        github: 'GitHub',
        
        // Placeholders
        placeholders: {
            calendarUrl: 'Zalijepi link na svoj FER kalendar',
            userEmail: 'Upiši svoj registrirani email'
        },

        // Error messages
        errors: {
            SUBSCRIPTION_NOT_FOUND: 'Pretplata nije pronađena.',
            SUBSCRIPTION_ALREADY_ACTIVE: 'Pretplata već aktivirana.',
            INVALID_CALENDAR_URL: 'Nevažeći URL kalendara.',
            INVALID_ICAL_DOCUMENT: 'Na URL-u nije valjan iCal dokument.',
            NOTIFICATIONS_ALREADY_PAUSED: 'Obavijesti su već pauzirane.',
            NOTIFICATIONS_ALREADY_ACTIVE: 'Obavijesti su već aktivne.',
            RATE_LIMIT_EXCEEDED: 'Previše zahtjeva. Pokušaj ponovno za {retry_after_minutes} minuta.',
            INVALID_TOKEN: 'Ovaj link nije valjan ili je zastario.',
            invalidEmail: 'Molim upiši valjan email.',
            invalidUrl: 'Molim upiši ispravan URL kalendara.',
            serverError: 'Greška poslužitelja. Pokušaj ponovno kasnije.',
            notThatLink: 'To nije link koji tražimo. Pogledaj (?) za više informacija.'
        },

        // Success messages  
        message: {
            subscriptionEmailSent: 'Email za potvrdu poslan! Provjeri svoj inbox (i spam) da aktiviraš obavijesti.',
            pauseSent: 'Email za potvrdu pauziranja obavijesti je poslan. Provjeri svoj inbox (i spam).',
            resumeSent: 'Email za potvrdu uključivanja obavijesti je poslan. Provjeri svoj inbox (i spam).',
            deleteSent: 'Email za potvrdu brisanja obavijesti je poslan. Provjeri svoj inbox (i spam).'
        },

        // Modal content
        modals: {
            howto: `
                <h2>Kako do linka?</h2>
                <p>Link na tvoj FER kalendar <b>nije</b> <a href="https://www.fer.unizg.hr/kalendar">
                https://www.fer.unizg.hr/kalendar</a>, ali ipak trebaš otići na tu stranicu! Ispod donjeg desnog kuta kalendara, 
                nalazi se "Preuzmi moje aktivnosti u iCal formatu" gumb. Nemoj ga stiskati! Desnim klikom (ili ako si na 
                mobitelu, dugim pritiskom) na njega možeš kopirati link na koji vodi. Format tog linka je 
                https://www.fer.unizg.hr/_downloads/calevent/mycal.ics?user=[tvoj_username]&auth=[tvoj_token]. 
                To je link koji trebaš upisati u NotiFER.</p>
            `,
            contact: `
                <h2>Kontakt</h2>
                <p>Za podršku i pitanja, pošalji mail na <a href="mailto:admin@emilpopovic.me">admin@emilpopovic.me</a>.</p>
            `,
            disclaimer: `
                <h2 id="-info">Info</h2>
                <p>Ova usluga dostupna je takva kakva jest i isključivo za udobnost kolegama studentima. <strong>Ja sam 
                student koji samostalno razvija ovaj alat</strong> i nisam ni na koji način povezan s FER-om, odobren od 
                strane njega niti službeno povezan s njim. <strong>Koristite na vlastitu odgovornost</strong>. Ne mogu 
                se smatrati odgovornim za propuštenu nastavu, laboratorijske vježbe i druge posljedice koje mogu 
                proizaći iz pogrešaka, kašnjenja ili odstupanja u obavijestima o rasporedu. <strong>Uvijek provjerite 
                svoj raspored na službenoj stranici FER-a.</strong></p>
                <h3 id="-service-scope-and-responsibility">Opseg usluge i odgovornost</h3>
                <ul>
                    <li><strong>Eksperimentalna priroda:</strong> Ovaj je alat eksperimentalan i može sadržavati bugove.
                    Uvijek provjeri službeni raspored.</li>
                    <li><strong>Odgovornost korisnika:</strong> Korisnik je odgovoran za provjeru rasporeda. Nisam
                    odgovoran za izostanke korisnika s nastave.</li>
                </ul>
                <h3 id="-data-collection-and-security">Prikupljanje i sigurnost podataka</h3>
                <ul>
                    <li><strong>Što se prikuplja:</strong> Jedino što ova aplikacija prikuplja je tvoja FER email adresa 
                    (npr. pi31415@fer.hr), token za autentikaciju kalendara te prošla verzija tvog kalendara.</li>
                    <li><strong>Rukovanje podacima:</strong> Svi su podaci sigurno smješteni i aplikacija je hostana lokalno 
                    u Zagrebu, a mailovi se šalju koristeći Resend.com.</li>
                    <li><strong>Tvoj pristanak:</strong> Korištenjem ove usluge pristaješ na ovakvo rukovanje podacima.
                    Iako se ulažu svi napori da se tvoji podaci zaštite, nijedan sustav ne može biti 100% siguran.</li>
                    <li><strong>Brisanje podataka:</strong> Sve je podatke moguće izbrisati koristeći &quot;Izbriši 
                    račun&quot; funkciju. Jedino što je potrebno za brisanje podataka je pristup fer.hr mailu. Ako ti to
                    nije po volji, pošalji mi poruku.</li>
                </ul>
                <h3 id="-service-availability-and-changes">Dostupnost usluge i promjene</h3>
                <ul>
                    <li><strong>Bez garancije usluge:</strong> Mogu bilo kada modificirati, privremeno suspendirati
                    ili ugasiti ovu uslugu. U tom ću se slučaju potruditi da korisnici dobiju obavijest o prekidu 
                    usluge.</li>
                    <li><strong>Pouzdanost:</strong> Ciljam na što veću pouzdanost, ali ne mogu garantirati neprekinut 
                    pristup i savršenu funkcionalnost.</li>
                    <li><strong>Vanjske promjene:</strong> Ova aplikacija ovisi o servisima koje ne kontroliram - 
                    FER-ovom sustavu kalendara i mailova - koji se bilo kada mogu promijeniti. Nisam odgovoran za takve 
                    prekide.</li>
                </ul>
                <h2 id="-message-to-user">Poruka korisniku</h2>
                <p>Točke gore zvuče opasno, ali i sam ovisim o i vjerujem ovoj aplikaciji. Ono što hoću reći je... 
                    <strong>Nemoj kriviti mene ako zakasniš na labos!!!</strong> :3</p>
            `,
            github: `
                <h2>GitHub repozitorij</h2>
                <p>NotiFER je softver otvorenog koda! Dostupan je na GitHubu:<br>
                <a href="https://github.com/myolnyr/NotiFER" target="_blank">github.com/myolnyr/NotiFER</a>
                </p>
            `
        }
    }
};

class I18n {
    constructor() {
        this.locale = this.detectLocale()
    }

    detectLocale() {
        return localStorage.getItem('locale') || 'hr'
    }

    setLocale(locale) {
        this.locale = locale
        localStorage.setItem('locale', locale)
    }

    t(key, params = {}) {
        const keys = key.split('.')
        let value = translations[this.locale]

        for (const k of keys) {
            value = value?.[k]
        }

        if (!value) {
            // Fallback to English
            value = translations.en
            for (const k of keys) {
                value = value?.[k]
            }
        }

        if (!value) return key

        // Replace parameters
        return value.replace(/\{(\w+)\}/g, (match, param) => params[param] || match)
    }
}

const i18n = new I18n()
