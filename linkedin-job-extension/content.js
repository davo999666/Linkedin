let lastJobIdentifier = "";

async function sendSimple(title, description) {
    const jobData = {
        url: window.location.href,
        title,
        description
    };

    if (typeof showLoadingModal === "function") {
        showLoadingModal();
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/job", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(jobData)
        });

        const data = await res.json();
        
        if (data.status === "error") {
            document.getElementById("ai-loading-toast")?.remove();
            alert("Server Error: " + (data.message || "Unknown error"));
            return;
        }
        
        const analysis = data.analysis;
        const time = data.processing_time_sec;
        
        if (!analysis) {
            document.getElementById("ai-loading-toast")?.remove();
            alert("No analysis data returned");
            return;
        }
        
        showAnalysisModal(analysis, time);
    } catch (err) {
        document.getElementById("ai-loading-toast")?.remove();
        alert("Error: " + err.message);
    }
}

function getVisibleElement(selector) {
    const elements = document.querySelectorAll(selector);
    for (let el of elements) {
        // An element is visible if its bounding box has non-zero height
        if (el.getBoundingClientRect().height > 0) {
            return el;
        }
    }
    return null;
}

function checkJobChange() {
    let title = "";
    let description = "";

    // 1. Try LinkedIn
    if (window.location.hostname.includes("linkedin.com")) {
        title = document.querySelector("h1")?.innerText?.trim() || "";
        // LinkedIn uses multiple possible selectors for job details
        description = document.querySelector(".jobs-box__html-content")?.innerText?.trim()
                   || document.querySelector("#job-details")?.innerText?.trim()
                   || document.querySelector("[data-job-details]")?.innerText?.trim()
                   || "";
    }
    // 2. Try Yad2 / Drushim
    else {
        // Yad2 renders many jobs on the page but hides the descriptions of unclicked jobs.
        // We must find the description box that is actually visible on screen right now.
        const visibleDescEl = getVisibleElement(".vacancyFullDetails") || getVisibleElement(".job-details-wrap");
        if (visibleDescEl) {
            description = visibleDescEl.innerText.trim();
            
            // Go up to the job card to grab the correponding title
            const parentTask = visibleDescEl.closest(".job-item-main, .job-item, .bg-open") || document;
            title = parentTask.querySelector(".job-url")?.innerText?.trim() 
                 || parentTask.querySelector("h3")?.innerText?.trim() 
                 || document.querySelector("h1")?.innerText?.trim() 
                 || "";
        }
    }

    // Wait until the job details are fully loaded in the DOM
    if (!description || !title) {
        return;
    }

    // Unique descriptor to avoid duplicate requests for the same job
    const currentJobIdentifier = title + " | " + description.substring(0, 100);

    if (currentJobIdentifier !== lastJobIdentifier) {
        console.log("🔄 New job fully loaded:", title);
        lastJobIdentifier = currentJobIdentifier;

        sendSimple(title, description);
    }
}

// 👇 check every 1.0 seconds
setInterval(checkJobChange, 1000);