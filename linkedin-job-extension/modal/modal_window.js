function showLoadingModal() {
    document.getElementById("ai-loading-toast")?.remove();
    const toast = document.createElement("div");
    toast.id = "ai-loading-toast";
    toast.innerHTML = `
        <div style="
            position: fixed;
            bottom: 20px; left: 20px;
            background: #fff;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            font-family: Arial;
            display: flex;
            align-items: center;
            gap: 10px;
            border-left: 4px solid #0073b1;
        ">
            <span style="font-size: 18px;">🤖</span>
            <span style="color: #333; font-weight: bold; font-size: 14px;">Analyzing Job Match...</span>
        </div>
    `;
    document.body.appendChild(toast);
}

function showAnalysisModal(analysisRaw, time) {
    let analysis;

    // handle string or object
    try {
        analysis = typeof analysisRaw === "string"
            ? JSON.parse(analysisRaw)
            : analysisRaw;
    } catch (e) {
        document.getElementById("ai-loading-toast")?.remove();
        alert("❌ Invalid JSON:\n" + analysisRaw);
        return;
    }

    // remove old modal or toast if exists
    document.getElementById("ai-loading-toast")?.remove();
    document.getElementById("ai-modal")?.remove();

    const known = analysis.matching_job_skills || [];
    const missing = analysis.missing_skills || [];

    const modal = document.createElement("div");
    modal.id = "ai-modal";

    modal.innerHTML = `
        <div style="
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <div style="
                background: #fff;
                padding: 20px;
                width: 600px;
                max-height: 80%;
                overflow-y: auto;
                border-radius: 12px;
                font-family: Arial;
            ">
                <h2>🎯 Match: ${analysis.match_percent}% ⏱ ${time}</h2>

                <h3>✅ Known Skills</h3>
                <div style="display:flex; flex-wrap:wrap; gap:8px;">
                       ${known.map(s => `
                       <span style="
                            background:#e6f0ff;
                            color:#0073b1;
                            padding:4px 8px;
                            border-radius:6px;
                            font-size:12px;
                            ">
                        ${s}
                       </span>
                    `).join("")}
                </div>

                <h3>❌ Missing Skills</h3>
                <ul>
                    ${missing.map(m => `
                        <li>
                            <b>${m.skill}</b><br/>
                            <small>${m.what_is_it}</small>
                        </li>
                    `).join("")}
                </ul>

                <h3>🧠 Why this score</h3>
                <p>${analysis.score_reason || "No explanation"}</p>

                <button id="close-ai-modal" style="
                    margin-top: 15px;
                    padding: 8px 12px;
                    border: none;
                    background: #0073b1;
                    color: white;
                    border-radius: 6px;
                    cursor: pointer;
                ">Close</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("close-ai-modal").onclick = () => {
        modal.remove();
    };
}