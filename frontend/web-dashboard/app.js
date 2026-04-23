// Dynamically choose API URL based on whether we are running locally or on Vercel
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = isLocalhost 
    ? "http://localhost:8000/api/v1" 
    : "https://vericlip-ai.onrender.com/api/v1";

// --- State ---
let loadedThreats = [];
let loadedEvents = [];

// --- Helpers ---
function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
        if (k === "className") node.className = v;
        else if (k.startsWith("on")) node.addEventListener(k.slice(2).toLowerCase(), v);
        else node.setAttribute(k, v);
    }
    for (const child of children) {
        if (typeof child === "string") node.appendChild(document.createTextNode(child));
        else if (child) node.appendChild(child);
    }
    return node;
}

function updateStatus(text, statusClass = "standby") {
    const indicator = document.getElementById("api-status");
    indicator.textContent = `SYSTEM: ${text.toUpperCase()}`;
    // You could add classes for different colors if needed
}

// --- API Calls ---

async function loadHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error();
        const data = await res.json();
        updateStatus(`ONLINE v${data.version}`);
    } catch {
        updateStatus("OFFLINE", "offline");
    }
}

async function loadStats() {
    const endpoints = ["cases", "media", "threats", "events", "notices"];
    try {
        // Use Promise.allSettled to prevent cascade failures
        const results = await Promise.allSettled(
            endpoints.map(e => fetch(`${API_BASE}/${e}`).then(r => r.json()))
        );

        // Extract data safely, defaulting to empty arrays/objects
        const getData = (idx, fallback = { total: 0, items: [], length: 0 }) => {
            if (results[idx].status === "fulfilled") return results[idx].value;
            console.warn(`Endpoint ${endpoints[idx]} failed, using fallback`);
            return fallback;
        };

        const threatsData = getData(2);
        const mediaData = getData(1);
        const noticesData = getData(4);

        document.getElementById("val-threats").textContent = (threatsData.total || 0).toString().padStart(3, '0');
        document.getElementById("val-media").textContent = (mediaData.total || 0).toString().padStart(3, '0');
        document.getElementById("val-notices").textContent = (noticesData.length || noticesData.total || 0).toString().padStart(3, '0');

        // Mock revenue logic: $1.2k per notice
        const revenue = ((noticesData.length || noticesData.total || 0) * 1.2).toFixed(1);
        document.getElementById("val-revenue").textContent = `$${revenue}k`;
    } catch (err) {
        console.error("Stats fetch failed", err);
    }
}

async function loadThreatFeed() {
    const minConf = document.getElementById("threat-min-conf").value || 0.5;
    const feed = document.getElementById("threat-feed");
    
    try {
        const res = await fetch(`${API_BASE}/threats?min_confidence=${minConf}`);
        const data = await res.json();
        loadedThreats = data.items;
        
        feed.innerHTML = "";
        if (loadedThreats.length === 0) {
            feed.innerHTML = '<div class="empty-state">NO THREATS DETECTED IN SWARM</div>';
            return;
        }

        loadedThreats.forEach((item, idx) => {
            const card = el("div", { className: "threat-card", onclick: () => verifyThreat(idx) },
                el("div", { className: "card-title" }, item.title || "Unknown Stream"),
                el("div", { className: "card-meta" }, 
                    `SOURCE: ${item.source.toUpperCase()} | CONF: ${(item.confidence * 100).toFixed(0)}%`
                )
            );
            feed.appendChild(card);
        });
    } catch (err) {
        feed.innerHTML = '<div class="empty-state">FEED SYNCHRONIZATION ERROR</div>';
    }
}

async function verifyThreat(idx) {
    updateStatus("VERIFYING...");
    try {
        const res = await fetch(`${API_BASE}/verify/${idx}`, { method: "POST" });
        const data = await res.json();
        updateStatus("VERIFIED");
        setTimeout(refreshAll, 1000);
    } catch (err) {
        alert("Verification failed: " + err.message);
        updateStatus("ONLINE");
    }
}

async function loadEvents() {
    const body = document.getElementById("event-table-body");
    try {
        const res = await fetch(`${API_BASE}/events`);
        const data = await res.json();
        loadedEvents = data.items;
        body.innerHTML = "";

        loadedEvents.forEach(item => {
            const tr = el("tr", {},
                el("td", {}, item.threat_id.split('_')[1]),
                el("td", {}, el("a", { href: item.infringement_url, target: "_blank", style: "color:var(--accent-primary)" }, "VIEW LINK")),
                el("td", {}, el("span", { className: `level-badge level-${item.threat_level}` }, item.threat_level)),
                el("td", {}, item.jurisdiction),
                el("td", {}, 
                    el("button", { className: "hud-btn", onclick: () => generateTakedown(item.threat_id) }, "TAKEDOWN")
                )
            );
            body.appendChild(tr);
        });
    } catch (err) {
        body.innerHTML = '<tr><td colspan="5">FAILED TO LOAD EVENTS</td></tr>';
    }
}

async function generateTakedown(threatId) {
    updateStatus("GENERATING NOTICE...");
    try {
        const res = await fetch(`${API_BASE}/takedown/${threatId}?dry_run=true`, { method: "POST" });
        const data = await res.json();
        showModal("LEGAL TAKEDOWN NOTICE", data.notice_content, data.jurisdiction);
        updateStatus("ONLINE");
    } catch (err) {
        alert("Takedown generation failed");
        updateStatus("ONLINE");
    }
}

// --- UI Actions ---

function showModal(title, content, jurisdiction = "US") {
    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-subtitle").textContent = `JURISDICTION: ${jurisdiction}`;
    document.getElementById("modal-content").textContent = content;
    document.getElementById("modal-overlay").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modal-overlay").classList.add("hidden");
}

// Ensure close events are bound
document.getElementById("modal-close").onclick = closeModal;
document.getElementById("modal-overlay").onclick = (e) => {
    if (e.target.id === "modal-overlay") closeModal();
};

function copyNotice() {
    const content = document.getElementById("modal-content").textContent;
    navigator.clipboard.writeText(content);
    const btn = document.querySelector(".nebula-btn-outline");
    const oldText = btn.textContent;
    btn.textContent = "COPIED!";
    setTimeout(() => btn.textContent = oldText, 2000);
}

function confirmTakedown() {
    alert("AUTHORIZATION GRANTED. NOTICE DISPATCHED TO PLATFORM API.");
    closeModal();
}

// --- Initialization ---

document.getElementById("form-scan").onsubmit = async (e) => {
    e.preventDefault();
    const query = document.getElementById("scan-query").value;
    updateStatus("SCANNING...");
    
    try {
        await fetch(`${API_BASE}/scan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        refreshAll();
    } catch (err) {
        updateStatus("SCAN ERROR");
    }
};

async function refreshAll() {
    await loadHealth();
    await loadStats();
    await loadThreatFeed();
    await loadEvents();
}

// Pause polling when tab is not visible
document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        clearInterval(refreshInterval);
    } else {
        refreshAll();
        refreshInterval = setInterval(refreshAll, 30000);
    }
});

let refreshInterval = setInterval(refreshAll, 30000);

// Button event bindings
document.getElementById("btn-refresh").onclick = refreshAll;
document.getElementById("btn-load-threats").onclick = loadThreatFeed;
document.getElementById("btn-load-events").onclick = loadEvents;
