function escapeHtml(text) {
    return String(text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function renderList(items) {
    if (!items || !items.length) return "<p class='muted'>No items found.</p>";
    return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderSkillChips(skills, type) {
    if (!skills || !skills.length) return "<p class='muted'>None</p>";
    return `<div class="chip-wrap">${skills
        .map((skill) => `<span class="chip ${type}">${escapeHtml(skill)}</span>`)
        .join("")}</div>`;
}

function renderRoadmap(roadmap) {
    if (!roadmap) return "<p class='muted'>Roadmap not available.</p>";
    return `
        <div class="timeline">
            <div class="timeline-card">
                <h4>Week 1-2</h4>
                ${renderList(roadmap.week_1_2 || [])}
            </div>
            <div class="timeline-card">
                <h4>Week 3-4</h4>
                ${renderList(roadmap.week_3_4 || [])}
            </div>
            <div class="timeline-card">
                <h4>Month 2-3</h4>
                ${renderList(roadmap.month_2_3 || [])}
            </div>
        </div>
    `;
}

async function analyze() {

    let loader = document.getElementById("loader");
    let resultDiv = document.getElementById("result");

    loader.classList.remove("hidden");
    resultDiv.innerHTML = "";

    try {
        let file = document.getElementById("resume").files[0];
        let job = document.getElementById("job").value.trim();

        if (!file) {
            throw new Error("Please upload a resume");
        }
        if (!job) {
            throw new Error("Please enter a job description");
        }

        let formData = new FormData();
        formData.append("file", file);
        formData.append("job_description", job);

        let response = await fetch(`/analyze`, {
            method: "POST",
            body: formData
        });

        // 🔥 VERY IMPORTANT DEBUG
        if (!response.ok) {
            let text = await response.text();
            throw new Error("Server Error: " + text);
        }

        const data = await response.json();
        const report = data.ai_report || {};

        loader.classList.add("hidden");

        resultDiv.innerHTML = `
            <h3>Analysis Dashboard</h3>

            <div class="result-grid">
                <div class="result-card">
                    <h4>Resume Skills</h4>
                    ${renderSkillChips(data.resume_skills || [], "good")}
                </div>
                <div class="result-card">
                    <h4>Required Job Skills</h4>
                    ${renderSkillChips(data.job_skills || [], "neutral")}
                </div>
                <div class="result-card">
                    <h4>Missing Skills</h4>
                    ${renderSkillChips(data.missing_skills || [], "gap")}
                </div>
                <div class="result-card">
                    <h4>Profile Summary</h4>
                    ${renderList(report.profile_summary || [])}
                </div>
                <div class="result-card">
                    <h4>Strengths</h4>
                    ${renderList(report.strengths || [])}
                </div>
                <div class="result-card">
                    <h4>Gap Areas</h4>
                    ${renderList(report.gap_areas || [])}
                </div>
                <div class="result-card full-width">
                    <h4>90-Day Learning Roadmap</h4>
                    ${renderRoadmap(report.roadmap)}
                </div>
                <div class="result-card">
                    <h4>Resources</h4>
                    ${renderList(report.resources || [])}
                </div>
                <div class="result-card">
                    <h4>Project Ideas</h4>
                    ${renderList(report.projects || [])}
                </div>
                <div class="result-card">
                    <h4>Interview Tips</h4>
                    ${renderList(report.interview_tips || [])}
                </div>
                <div class="result-card full-width highlight">
                    <h4>Top 5 Next Actions</h4>
                    ${renderList(report.top_next_actions || [])}
                </div>
            </div>
        `;

    } catch (error) {
        loader.classList.add("hidden");  // ✅ ALWAYS stop loader
        resultDiv.innerHTML = `<p class="error">Error: ${escapeHtml(error.message)}</p>`;
        console.error(error);
    }
}