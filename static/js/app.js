const API_BASE = window.location.origin;
let isProcessing = false;


const statusMessages = {
    pauseSent: "📩 Email za potvrdu pauziranja obavijesti je poslan. Provjeri svoj inbox (i spam).",
    resumeSent: "📩 Email za potvrdu uključivanja obavijesti je poslan. Provjeri svoj inbox (i spam).",
    deleteSent: "📩 Email za potvrdu brisanja obavijesti je poslan. Provjeri svoj inbox (i spam).",
    subSuccess: "🎉 Email za potvrdu poslan! Provjeri svoj inbox (i spam) da aktiviraš obavijesti.",
    subError: "⚠️ Greška tijekom obrade zahtjeva. Pokušaj ponovno kasnije.",
    invalidEmail: "❌ Molim upiši valjan email.",
    invalidUrl: "❌ Molim upiši ispravan URL kalendara.",
    serverError: "🔧 Greška poslužitelja. Pokušaj ponovno kasnije.",
    rateLimit: "⏳ Previše zahtjeva. Pokušaj ponovno kasnije.",
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
        }, 10000);
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

    twemoji.parse(document.content, {
        base: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/"
    });
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
    const modal = document.getElementById('manageModal');
    modal.classList.add('active');
    
    twemoji.parse(modal, {
        folder: 'svg',
        ext: '.svg'
    });
}


function closeManageModal() {
    document.getElementById('manageModal').classList.remove('active');
}


document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeManageModal();
        closeInfoModal();
    } 
});


document.addEventListener('click', function (event) {
    const manageModal = document.getElementById('manageModal');
    const infoModal = document.getElementById('infoModal');
    
    if (event.target === manageModal) {
        closeManageModal();
    }
    
    if (event.target === infoModal) {
        closeInfoModal();
    }
});


function openModal(type) {
    const modal = document.getElementById('infoModal');
    const content = document.getElementById('infoModalContent');
    let html = '';

    switch(type) {
        case 'howto':
            html = `<h2 id="-kako-do-linka-">🤔 Kako do linka?</h2>
<p>Link na tvoj FER kalendar <em>nije</em> <a href="https://www.fer.unizg.hr/kalendar">https://www.fer.unizg.hr/kalendar</a>, ali ipak trebaš otići na tu stranicu! Ispod donjeg desnog kuta kalendara, nalazi se &quot;Preuzmi moje aktivnosti u iCal formatu&quot; gumb. Nemoj ga stiskati! 🛑 Desnim klikom (ili ako si na mobitelu, dugim pritiskom 📱) na njega možeš kopirati link na koji vodi. 🔗 Format tog linka je https://www.fer.unizg.hr/_downloads/calevent/mycal.ics?user=[tvoj_username]&amp;auth=[tvoj_token]. To je link koji trebaš upisati u NotiFER.</p>`
            break;
        case 'contact':
            html = `<h2>📞 Kontakt</h2>
                            <p>Za podršku i pitanja, pošalji mail na admin@emilpopovic.me.</p>`;
            break;
        case 'disclaimer':
            html = `<h2 id="-info">ℹ️ Info</h2>
<p>Ova usluga dostupna je takva kakva jest i isključivo za udobnost kolegama studentima. <strong>Ja sam student koji samostalno razvija ovaj alat</strong> i nisam ni na koji način povezan s FER-om, odobren od strane njega niti službeno povezan s njim. <strong>Koristite na vlastitu odgovornost</strong>. Ne mogu se smatrati odgovornim za propuštenu nastavu, laboratorijske vježbe i druge posljedice koje mogu proizaći iz pogrešaka, kašnjenja ili odstupanja u obavijestima o rasporedu. <strong>Uvijek provjerite svoj raspored na službenoj stranici FER-a.</strong></p>
<h3 id="-opseg-usluge-i-odgovornost">🔬 Opseg usluge i odgovornost</h3>
<ul>
<li><strong>Eksperimentalna priroda:</strong> Ovaj je alat eksperimentalan i može sadržavati bugove. Uvijek provjeri službeni raspored.</li>
<li><strong>Odgovornost korisnika:</strong> Korisnik je odgovoran za provjeru rasporeda. Nisam odgovoran za izostanke korisnika s nastave.</li>
</ul>
<h3 id="-prikupljanje-i-sigurnost-podataka">🔒 Prikupljanje i sigurnost podataka</h3>
<ul>
<li><strong>Što se prikuplja:</strong> Jedino što ova aplikacija prikuplja je tvoja FER email adresa (npr. pi31415@fer.hr), token za autentikaciju kalendara te prošla verzija tvog kalendara.</li>
<li><strong>Rukovanje podacima:</strong> Svi su podaci sigurno smješteni i aplikacija hostana u Njemačkoj na usluzi Hetzner, a mailovi se šalju koristeći Resend.com.</li>
<li><strong>Tvoj pristanak:</strong> Korištenjem ove usluge pristaješ na ovakvo rukovanje podacima. Iako se ulažu svi napori da se tvoji podaci zaštite, nijedan sustav ne može biti 100% siguran.</li>
<li><strong>Brisanje podataka:</strong> Sve je podatke moguće izbrisati koristeći &quot;Izbriši račun&quot; funkciju. Jedino što je potrebno za brisanje podataka je pristup fer.hr mailu. Ako ti to nije po volji, pošalji mi poruku.</li>
</ul>
<h3 id="-dostupnost-usluge-i-promjene">🚧 Dostupnost usluge i promjene</h3>
<ul>
<li><strong>Bez garancije usluge:</strong> Mogu bilo kada modificirati, privremeno suspendirati ili ugasiti ovu uslugu. U tom ću se slučaju potruditi da korisnici dobiju obavijest o prekidu usluge.</li>
<li><strong>Pouzdanost:</strong> Ciljam na što veću pouzdanost, ali ne mogu garantirati neprekinut pristup i savršenu funkcionalnost.</li>
<li><strong>Vanjske promjene:</strong> Ova aplikacija ovisi o servisima koje ne kontroliram - FER-ovom sustavu kalendara i mailova - koji se bilo kada mogu promijeniti. Nisam odgovoran za takve prekide.</li>
</ul>
<h2 id="-poruka-korisniku">✨ Poruka korisniku</h2>
<p>Točke gore zvuče opasno, ali i sam ovisim o i vjerujem ovoj aplikaciji. Ono što hoću reći je... <strong>Nemoj kriviti mene ako zakasniš na labos!!!</strong> :3</p>
`;
            break;
        case 'github':
            html = `<h2>🧑‍💻 GitHub repozitorij</h2>
                            <p>Cijeli NotiFER je open source na GitHubu:<br>
                            <a href="https://github.com/EmilPopovic/NotiFER" target="_blank">
                                github.com/EmilPopovic/NotiFER
                            </a></p>`;
            break;
    }
    content.innerHTML = html;
    modal.classList.add('active');

    twemoji.parse(content, {
        base: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/"
    });
}

function closeInfoModal() {
    document.getElementById('infoModal').classList.remove('active');
}
