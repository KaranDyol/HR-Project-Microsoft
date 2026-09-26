"use strict";

const app = document.getElementById("app");
const shell = document.querySelector(".app-shell");
const tokenKey = "peopleos.session";
const state = {
    token: sessionStorage.getItem(tokenKey),
    user: null,
    section: "overview",
    employees: [],
    employeeFilter: "Active",
    selectedEmployee: null,
    applicants: [],
    applicantFilter: "Pipeline",
    applicantPage: 1,
    applicantPageSize: 10,
    employeePage: 1,
    employeePageSize: 10,
    recruitmentJobPage: 1,
    recruitmentCandidatePage: 1,
    recruitmentPageSize: 6,
    recruitmentJobs: [],
    recruitmentCandidates: [],
    options: null,
    notificationOpen: false,
};

const sectionInfo = {
    overview: ["Overview", "Your workforce, at a glance", "A current view of people, hiring and workforce signals."],
    employees: ["People", "Employee directory", "Review employee details and workforce signals."],
    recruitment: ["Recruitment", "Open roles", "Track hiring progress across your active roles."],
    applicants: ["Applicants", "Candidate pipeline", "Review candidates and manage their application details."],
    insights: ["Insights", "Workforce insights", "Explore retention, development and team-level signals."],
    policies: ["Policy desk", "HR policy library", "Search policy sources and add verified guidance."],
    profile: ["My profile", "Account settings", "Update your PeopleOS account details."],
    admin: ["Accounts", "Workspace accounts", "Manage user access for this workspace."],
};

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[character]);
}

function initials(value) {
    return String(value || "?").trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

function formatDate(value) {
    if (!value) return "";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? "" : date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function formatPercent(value) {
    return `${Math.round(Number(value || 0) * 100)}%`;
}

function paginationControls(page, pageSize, total, actionPrefix) {
    const pages = Math.max(1, Math.ceil(total / pageSize));
    return `<nav class="pagination-controls" aria-label="Pagination"><span class="pagination-range">${total ? ((page - 1) * pageSize) + 1 : 0}-${Math.min(page * pageSize, total)} of ${total}</span><label>Rows<select data-action="${actionPrefix}-page-size" aria-label="Rows per page"><option value="10" ${pageSize === 10 ? "selected" : ""}>10</option><option value="25" ${pageSize === 25 ? "selected" : ""}>25</option><option value="50" ${pageSize === 50 ? "selected" : ""}>50</option></select></label><button class="text-button" data-action="${actionPrefix}-previous" aria-label="Previous page" ${page <= 1 ? "disabled" : ""}>Previous</button><strong>Page ${page} / ${pages}</strong><button class="text-button" data-action="${actionPrefix}-next" aria-label="Next page" ${page >= pages ? "disabled" : ""}>Next</button></nav>`;
}

async function api(path, options = {}) {
    const url = new URL(path, window.location.origin);
    if (state.token && !path.startsWith("/api/auth/login") && !path.startsWith("/api/auth/register")) {
        url.searchParams.set("token", state.token);
    }
    const request = { method: options.method || "GET", headers: { Accept: "application/json" } };
    if (options.body !== undefined) {
        if (options.body instanceof FormData) {
            request.body = options.body;
        } else {
            request.headers["Content-Type"] = "application/json";
            request.body = JSON.stringify(options.body);
        }
    }
    const response = await fetch(url, request);
    const text = await response.text();
    let result = null;
    try { result = text ? JSON.parse(text) : null; } catch { result = text; }
    if (!response.ok) {
        const message = result && typeof result === "object" ? result.detail : null;
        throw new Error(message || `Request failed (${response.status})`);
    }
    return result;
}

function setFeedback(form, message, isError = true) {
    const feedback = form.querySelector(".form-feedback");
    if (!feedback) return;
    feedback.textContent = message;
    feedback.classList.toggle("form-error", isError);
}

function formValues(form) {
    return Object.fromEntries(new FormData(form).entries());
}

function renderLoggedOut(message = "") {
    document.body.classList.add("logged-out");
    shell.classList.remove("sidebar-open");
    app.innerHTML = `
		<section class="login-panel">
			<div class="login-brand"><span class="brand-mark">P</span><strong>people<span>os</span></strong></div>
			<h1>Welcome back</h1>
			<p class="login-copy">Sign in to your workforce workspace.</p>
			<form class="login-form" id="login-form">
				<label>Email address<input name="email" type="email" autocomplete="username" required></label>
				<label>Password<input name="password" type="password" autocomplete="current-password" required></label>
				<p class="form-feedback ${message ? "form-error" : ""}" role="status">${escapeHtml(message)}</p>
				<button class="primary-button" type="submit">Sign in</button>
			</form>
			<button class="text-button login-register-link" type="button" data-action="show-register">Create an account</button>
		</section>`;
}

function renderRegister() {
    document.body.classList.add("logged-out");
    app.innerHTML = `
		<section class="login-panel">
			<div class="login-brand"><span class="brand-mark">P</span><strong>people<span>os</span></strong></div>
			<h1>Create account</h1>
			<p class="login-copy">Register for a PeopleOS workspace account.</p>
			<form class="login-form" id="register-form">
				<label>Full name<input name="name" autocomplete="name" minlength="2" required></label>
				<label>Email address<input name="email" type="email" autocomplete="email" required></label>
				<label>Workspace role<select name="role" required><option>Recruiter</option><option>Hiring Manager</option><option>HR Manager</option><option>HR Business Partner</option></select></label>
				<label>Password<input name="password" type="password" autocomplete="new-password" minlength="8" required></label>
				<label>Confirm password<input name="confirm_password" type="password" autocomplete="new-password" minlength="8" required></label>
				<p class="form-feedback" role="status"></p>
				<button class="primary-button" type="submit">Create account</button>
			</form>
			<button class="text-button login-register-link" type="button" data-action="show-login">Back to sign in</button>
		</section>`;
}

function updateHeader() {
    const info = sectionInfo[state.section] || sectionInfo.overview;
    const breadcrumb = document.querySelector(".breadcrumb");
    const heading = document.querySelector(".page-heading h1");
    const subtitle = document.querySelector(".page-heading .subtitle");
    const eyebrow = document.querySelector(".page-heading .eyebrow");
    if (breadcrumb) breadcrumb.innerHTML = `Workspace <span>/</span> ${escapeHtml(info[0])}`;
    if (heading) heading.textContent = state.section === "overview" ? `Good morning, ${state.user?.name?.split(" ")[0] || "there"}.` : info[1];
    if (subtitle) subtitle.textContent = info[2];
    if (eyebrow) eyebrow.textContent = new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" }).toUpperCase();
    const avatar = document.getElementById("account-button");
    if (avatar) avatar.textContent = initials(state.user?.name);
    document.querySelectorAll(".nav-item").forEach((button) => {
        button.classList.toggle("active", button.dataset.section === state.section);
    });
    document.querySelectorAll(".nav-item.admin-only").forEach((button) => {
        button.classList.toggle("visible", state.user?.role === "HR Admin");
    });
}

function panelHeader(title, subtitle = "", action = "") {
    return `<div class="panel-header"><div><h2 class="panel-title">${escapeHtml(title)}</h2>${subtitle ? `<p class="panel-subtitle">${escapeHtml(subtitle)}</p>` : ""}</div>${action}</div>`;
}

function metric(label, value, note, icon, warning = false) {
    return `<article class="metric"><div class="metric-top"><span>${escapeHtml(label)}</span><span class="metric-icon">${icon}</span></div><div class="metric-value">${escapeHtml(value)}</div><div class="metric-note ${warning ? "warn" : ""}">${escapeHtml(note)}</div></article>`;
}

function renderRiskRows(risks) {
    if (!risks.length) return `<div class="empty-state">No workforce signals to display.</div>`;
    return risks.slice(0, 5).map((item) => {
        const high = item.risk_score >= 0.55;
        const factor = (item.factors || []).slice(0, 2).join(" · ") || "No notable risk factors";
        return `<div class="risk-row"><div class="person"><span class="person-avatar">${escapeHtml(initials(item.name))}</span><span>${escapeHtml(item.name)}<small class="person-role">${escapeHtml(item.role)}</small><small class="person-factor">${escapeHtml(factor)}</small></span></div><div class="risk-meter ${high ? "" : "low"}"><span style="width:${Math.round(item.risk_score * 100)}%"></span></div><div class="risk-label ${high ? "" : "low"}">${formatPercent(item.risk_score)}</div></div>`;
    }).join("");
}

function renderBars(performance) {
    return performance.map((item) => `<div class="bar-wrap"><div class="bar" title="${escapeHtml(item.value)} / 5" style="height:${Math.max(8, Math.min(100, Number(item.value) / 5 * 100))}%"></div><span class="bar-label">${escapeHtml(item.label)}</span></div>`).join("");
}

async function renderOverview() {
    const data = await api("/api/dashboard");
    const metrics = data.metrics;
    app.innerHTML = `
		<section class="metrics-grid">
			${metric("Active employees", metrics.active_employees, `${metrics.total_employees} records in workspace`, "♙")}
			${metric("Open positions", metrics.open_positions, metrics.role_note, "↗")}
			${metric("High retention risk", metrics.high_risk, metrics.risk_note, "◒", metrics.high_risk > 0)}
			${metric("Average engagement", `${metrics.average_engagement}%`, metrics.skill_gap_note, "◎")}
		</section>
		<section class="content-grid">
			<article class="panel">${panelHeader("Retention signals", "Based on stored workforce signals", `<button class="text-button" data-view="insights">All insights</button>`)}<div class="risk-list">${renderRiskRows(data.risks)}</div></article>
			<article class="panel">${panelHeader("Performance snapshot", `Average score: ${escapeHtml(metrics.average_performance)} / 5`)}<div class="chart">${renderBars(data.performance)}</div></article>
			<article class="panel">${panelHeader("Hiring in progress", "Current role pipeline", `<button class="text-button" data-view="recruitment">View roles</button>`)}<div class="jobs-list">${data.jobs.length ? data.jobs.map((job) => `<div class="job-row"><div><div class="job-title">${escapeHtml(job.title)}</div><div class="job-dept">${escapeHtml(job.department)} · ${Number(job.applicants)} applicants</div></div><span class="job-status ${job.status === "New" ? "new" : ""}">${escapeHtml(job.status)}</span></div>`).join("") : `<div class="empty-state">No open roles.</div>`}</div></article>
			<article class="panel">${panelHeader("Workspace notes", "PeopleOS workforce intelligence")}<p class="detail-copy">Workforce scores are calculated from the current employee records. Review the underlying evidence before making people decisions.</p></article>
		</section>
		<section class="panel policy-panel"><div><h2 class="panel-title">Policy desk</h2><p class="panel-subtitle">Ask a question grounded in workspace policy sources.</p><div id="overview-policy-answer" aria-live="polite"></div></div><form class="policy-form" id="overview-policy-form"><input name="question" placeholder="Ask about a policy..." minlength="3" required><button class="primary-button" type="submit">Ask</button></form></section>`;
}

function employeeRows() {
    const search = (document.getElementById("employee-search")?.value || "").trim().toLowerCase();
    const department = document.getElementById("employee-department-filter")?.value || "All";
    const role = document.getElementById("employee-role-filter")?.value || "All";
    const employees = state.employees.filter((employee) => (state.employeeFilter === "All" || (state.employeeFilter === "Active" ? employee.status === "Active" : employee.status !== "Active")) && (department === "All" || employee.department === department) && (role === "All" || employee.role === role) && `${employee.name} ${employee.role} ${employee.department} ${employee.location}`.toLowerCase().includes(search));
    const pageCount = Math.max(1, Math.ceil(employees.length / state.employeePageSize));
    state.employeePage = Math.min(state.employeePage, pageCount);
    const visibleEmployees = employees.slice((state.employeePage - 1) * state.employeePageSize, state.employeePage * state.employeePageSize);
    if (state.selectedEmployee && !employees.some((employee) => employee.id === state.selectedEmployee)) {
        state.selectedEmployee = null;
        document.getElementById("employee-detail")?.remove();
    }
    const target = document.getElementById("employee-rows");
    if (!target) return;
    target.innerHTML = employees.length ? visibleEmployees.map((employee) => `<tr class="employee-row" data-employee="${employee.id}"><td><strong>${escapeHtml(employee.name)}</strong></td><td>${escapeHtml(employee.role)}</td><td>${escapeHtml(employee.department)}</td><td>${escapeHtml(employee.location)}</td><td><span class="status-pill ${employee.status === "Active" ? "" : "inactive"}">${escapeHtml(employee.status)}</span></td><td>${(Number(employee.performance_score) * 20).toFixed(1)} / 100</td><td><span class="risk-chip ${employee.retention_risk >= 0.55 ? "risk-high" : ""}">${formatPercent(employee.retention_risk)}</span></td></tr>`).join("") : `<tr><td colspan="7" class="empty-state">No employees match this view.</td></tr>`;
    const pagination = document.getElementById("employee-pagination");
    if (pagination) pagination.innerHTML = paginationControls(state.employeePage, state.employeePageSize, employees.length, "employee");
}

function employeeDetail(employee, performance) {
    const skills = String(employee.skills || "").split(",").map((skill) => skill.trim()).filter(Boolean);
    return `<article class="panel employee-detail" id="employee-detail">${panelHeader(escapeHtml(employee.name), `${escapeHtml(employee.role)} · ${escapeHtml(employee.department)}`, `<button class="text-button" data-action="toggle-employee-edit">Edit details</button>`)}
        <div class="detail-grid"><div><span class="detail-label">Skills</span><div class="skill-tags">${skills.map((skill) => `<span>${escapeHtml(skill)}</span>`).join("")}</div></div><div><span class="detail-label">Workforce signals</span><p class="detail-copy">Performance ${performance ? Number(performance.current_score).toFixed(1) : (Number(employee.performance_score) * 20).toFixed(1)} / 100 · Satisfaction ${Number(employee.satisfaction_score).toFixed(1)} / 5 · ${Number(employee.overtime) ? "Overtime flagged" : "No overtime flagged"}</p><p class="detail-copy">Retention risk ${formatPercent(employee.retention_risk)} · Engagement ${Number(employee.engagement_score)}%</p></div></div>
        ${performance ? `<div class="performance-summary"><div><span class="detail-label">Current performance</span><strong>${Number(performance.current_score).toFixed(1)} / 100</strong></div><div><span class="detail-label">Trend</span><strong class="${Number(performance.score_change) >= 0 ? "positive" : "negative"}">${Number(performance.score_change) >= 0 ? "+" : ""}${Number(performance.trend_percentage).toFixed(1)}%</strong></div><div><span class="detail-label">Manager</span><strong>${escapeHtml(performance.employee.manager_name || "Not assigned")}</strong></div></div>
        <section class="performance-section"><h3>Performance history</h3><div class="history-bars">${performance.history.map((item) => `<div class="history-point"><strong>${Number(item.score).toFixed(1)}</strong><span style="height:${Math.max(8, Number(item.score))}%"></span><small>${escapeHtml(formatDate(item.period))}</small></div>`).join("")}</div></section>
        <section class="performance-section"><h3>KPI breakdown</h3><div class="kpi-breakdown">${performance.kpi_breakdown.map((item) => `<div class="kpi-row"><strong>${escapeHtml(item.kpi)}</strong><span>${escapeHtml(item.actual)} / ${escapeHtml(item.target ?? "-")}</span><span>${Number(item.score).toFixed(1)}</span><span>${Number(item.weight).toFixed(1)}%</span><span>${Number(item.contribution).toFixed(1)} pts</span></div>`).join("")}</div></section>
        <section class="performance-section"><h3>Strengths</h3><p class="detail-copy">${escapeHtml(performance.strengths.join(" · "))}</p></section>
        <section class="performance-section"><h3>Feedback evidence</h3><p class="detail-copy">${escapeHtml((performance.feedback_analysis?.positive_evidence || []).join(" · ") || "No positive evidence extracted.")}</p><p class="detail-copy">${escapeHtml((performance.feedback_analysis?.negative_evidence || []).join(" · ") || "No negative evidence extracted.")}</p></section>
        <section class="performance-section"><h3>Development areas</h3><div class="development-list">${performance.development_areas.map((item) => `<div><strong>${escapeHtml(item.skill)}</strong><small>${escapeHtml(item.current_level)} → ${escapeHtml(item.required_level)}</small><p>${escapeHtml(item.recommended_training)}</p></div>`).join("")}</div></section>
        <section class="performance-section"><h3>Why is this score?</h3><p class="detail-copy">${escapeHtml(performance.explainability)}</p></section>` : ""}
		<form class="data-form employee-edit-form hidden" id="employee-edit-form" data-employee-id="${employee.id}">
			<div class="detail-grid"><label>Name<input name="name" value="${escapeHtml(employee.name)}" required></label><label>Role<input name="role" value="${escapeHtml(employee.role)}" required></label><label>Department<input name="department" value="${escapeHtml(employee.department)}" required></label><label>Location<input name="location" value="${escapeHtml(employee.location)}" required></label><label>Skills (comma separated)<input name="skills" value="${escapeHtml(employee.skills)}" required></label><label>Performance score<input name="performance_score" type="number" min="0" max="5" step="0.1" value="${Number(employee.performance_score)}" required></label><label>Satisfaction score<input name="satisfaction_score" type="number" min="0" max="5" step="0.1" value="${Number(employee.satisfaction_score)}" required></label><label>Overtime<select name="overtime"><option value="0" ${Number(employee.overtime) ? "" : "selected"}>No</option><option value="1" ${Number(employee.overtime) ? "selected" : ""}>Yes</option></select></label></div>
			<p class="form-feedback" role="status"></p><div class="employee-detail-actions"><button class="primary-button" type="submit">Save changes</button>${employee.status === "Active" ? `<button class="fire-button" type="button" data-action="fire-employee" data-id="${employee.id}">Mark as departed</button>` : ""}</div>
		</form><div class="detail-analysis"><span class="detail-label">Factors</span><p class="detail-copy">${escapeHtml((employee.factors || []).join(", ") || "No notable risk factors")}</p></div></article>`;
}

async function renderEmployees() {
    state.employees = await api("/api/employees");
    const selected = state.employees.find((employee) => employee.id === state.selectedEmployee);
    const performance = selected ? await api(`/api/employees/${selected.id}/performance`) : null;
    const departments = [...new Set(state.employees.map((employee) => employee.department))].sort();
    const roles = [...new Set(state.employees.map((employee) => employee.role))].sort();
    app.innerHTML = `<section class="panel">${panelHeader("People directory", `${state.employees.length} employee records`)}
		<div class="people-tabs"><button class="people-tab ${state.employeeFilter === "Active" ? "active" : ""}" data-filter="Active">Active <span>${state.employees.filter((person) => person.status === "Active").length}</span></button><button class="people-tab ${state.employeeFilter === "Fired" ? "active" : ""}" data-filter="Fired">Departed <span>${state.employees.filter((person) => person.status !== "Active").length}</span></button><button class="people-tab ${state.employeeFilter === "All" ? "active" : ""}" data-filter="All">All <span>${state.employees.length}</span></button></div>
        <div class="directory-actions"><input class="table-search" id="employee-search" type="search" placeholder="Search people, roles or teams" aria-label="Search employees"><select id="employee-department-filter" aria-label="Filter by department"><option>All</option>${departments.map((item) => `<option>${escapeHtml(item)}</option>`).join("")}</select><select id="employee-role-filter" aria-label="Filter by role"><option>All</option>${roles.map((item) => `<option>${escapeHtml(item)}</option>`).join("")}</select></div>
        <div class="people-table-wrap"><table class="people-table"><thead><tr><th>Name</th><th>Role</th><th>Department</th><th>Location</th><th>Status</th><th>Performance</th><th>Retention risk</th></tr></thead><tbody id="employee-rows"></tbody></table></div><div id="employee-pagination"></div></section>${selected ? employeeDetail(selected, performance) : ""}`;
    employeeRows();
}

function candidateRows(candidates, actions = true, scoreLabel = "Match score") {
    if (!candidates.length) return `<div class="empty-state">No candidates in this pipeline.</div>`;
    return candidates.map((candidate) => `<div class="candidate-row"><span class="person-avatar">${escapeHtml(initials(candidate.name))}</span><div class="candidate-name"><strong>${escapeHtml(candidate.name)}</strong><small>${escapeHtml(candidate.role)} · ${escapeHtml(candidate.experience)}</small></div><span class="candidate-skills">${escapeHtml(candidate.skills)}</span><span class="match-score">${escapeHtml(scoreLabel)}: ${Number(candidate.match ?? candidate.match_score ?? 0)}%</span><div class="candidate-actions"><button class="text-button" data-action="view-candidate" data-candidate="${escapeHtml(candidate.candidate_id || `CAN${String(candidate.id).padStart(3, "0")}`)}">Review</button>${actions ? `<button class="hire-button" data-action="hire-applicant" data-id="${candidate.id}">Hire</button><button class="reject-button" data-action="reject-applicant" data-id="${candidate.id}">Reject</button>` : ""}</div></div>`).join("");
}

function candidateDetailPanel(data) {
    const candidate = data.candidate;
    const topScore = data.job_scores?.[0];
    return `<article class="panel candidate-detail" id="candidate-detail">${panelHeader(escapeHtml(data.name), `${escapeHtml(candidate.current_role || "Candidate")} · ${escapeHtml(candidate.location || "Location not found")}`)}<div class="candidate-detail-summary"><strong>${topScore ? `${Number(topScore.overall_match_score).toFixed(1)} / 100` : "Not scored"}</strong><span>${topScore ? escapeHtml(topScore.job_title) : "Select a specific job to calculate a match"}</span><span class="status-pill">${escapeHtml(candidate.status)}</span></div><section class="candidate-evidence-section"><h3>Documented skills</h3><div class="skill-tags">${data.skills.map((skill) => `<span>${escapeHtml(skill.skill_name)} · ${escapeHtml(skill.proficiency_level || "Not stated")}</span>`).join("") || `<span>Not found in submitted evidence</span>`}</div></section><section class="candidate-evidence-section"><h3>Experience</h3>${data.experience.map((item) => `<p class="detail-copy"><strong>${escapeHtml(item.job_title)}</strong> · ${escapeHtml(item.company)} · ${escapeHtml(item.duration_months)} months<br>${escapeHtml(item.technologies || item.description || "Documented experience")}</p>`).join("") || `<p class="detail-copy">No documented experience found.</p>`}</section><section class="candidate-evidence-section"><h3>Projects</h3>${data.projects.map((item) => `<p class="detail-copy"><strong>${escapeHtml(item.project_name)}</strong> · ${escapeHtml(item.technologies || "Technologies not stated")}<br>${escapeHtml(item.description || "No project description found.")}</p>`).join("") || `<p class="detail-copy">No documented projects found.</p>`}</section><section class="candidate-evidence-section"><h3>Evidence</h3>${data.evidence.slice(0, 5).map((item) => `<p class="detail-copy"><strong>${escapeHtml(item.evidence_type || "Source")}</strong> · ${escapeHtml(item.source_document || "Submitted evidence")}<br>${escapeHtml(item.source_text || "No evidence text found.")}</p>`).join("") || `<p class="detail-copy">No evidence records found.</p>`}</section></article>`;
}

async function renderRecruitment() {
    const data = await api("/api/recruitment");
    state.recruitmentJobs = data.jobs;
    state.recruitmentCandidates = data.candidates;
    renderRecruitmentView();
}

function renderRecruitmentView() {
    const jobStatus = document.getElementById("recruitment-status-filter")?.value || "All";
    const jobDepartment = document.getElementById("recruitment-department-filter")?.value || "All";
    const candidateSearch = (document.getElementById("recruitment-candidate-search")?.value || "").trim().toLowerCase();
    const jobs = state.recruitmentJobs.filter((job) => (jobStatus === "All" || job.status === jobStatus) && (jobDepartment === "All" || job.department === jobDepartment));
    const candidates = state.recruitmentCandidates.filter((candidate) => `${candidate.name} ${candidate.role} ${candidate.skills}`.toLowerCase().includes(candidateSearch));
    const jobPages = Math.max(1, Math.ceil(jobs.length / state.recruitmentPageSize));
    const candidatePages = Math.max(1, Math.ceil(candidates.length / state.recruitmentPageSize));
    state.recruitmentJobPage = Math.min(state.recruitmentJobPage, jobPages);
    state.recruitmentCandidatePage = Math.min(state.recruitmentCandidatePage, candidatePages);
    const visibleJobs = jobs.slice((state.recruitmentJobPage - 1) * state.recruitmentPageSize, state.recruitmentJobPage * state.recruitmentPageSize);
    const visibleCandidates = candidates.slice((state.recruitmentCandidatePage - 1) * state.recruitmentPageSize, state.recruitmentCandidatePage * state.recruitmentPageSize);
    const maxApplicants = Math.max(1, ...jobs.map((job) => job.applicants));
    const departments = [...new Set(state.recruitmentJobs.map((job) => job.department))].sort();
    const statuses = [...new Set(state.recruitmentJobs.map((job) => job.status))].sort();
    app.innerHTML = `<article class="panel">${panelHeader("Open roles", "Hiring activity by role", `<button class="primary-button" data-action="new-role">＋ New role</button>`)}
        <div class="recruitment-filters"><select id="recruitment-status-filter" aria-label="Filter roles by status"><option ${jobStatus === "All" ? "selected" : ""}>All</option>${statuses.map((item) => `<option ${jobStatus === item ? "selected" : ""}>${escapeHtml(item)}</option>`).join("")}</select><select id="recruitment-department-filter" aria-label="Filter roles by department"><option ${jobDepartment === "All" ? "selected" : ""}>All</option>${departments.map((item) => `<option ${jobDepartment === item ? "selected" : ""}>${escapeHtml(item)}</option>`).join("")}</select></div><div class="role-cards">${visibleJobs.map((job) => `<article class="role-card"><div class="role-card-top"><span class="job-status ${job.status === "New" ? "new" : ""}">${escapeHtml(job.status)}</span><span class="role-applicants">${Number(job.applicants)} applicants</span></div><h3>${escapeHtml(job.title)}</h3><p>${escapeHtml(job.department)}</p><div class="role-progress"><span style="width:${Math.min(100, job.applicants / maxApplicants * 100)}%"></span></div></article>`).join("") || `<div class="empty-state">No roles match these filters.</div>`}</div><div id="recruitment-job-pagination">${paginationControls(state.recruitmentJobPage, state.recruitmentPageSize, jobs.length, "recruitment-job")}</div></article>
		<article class="panel applicant-panel">${panelHeader("Candidate shortlist", `${candidates.length} active candidates`, `<button class="text-button" data-action="new-applicant">Add applicant</button>`)}<div class="directory-actions"><input class="table-search" id="recruitment-candidate-search" type="search" value="${escapeHtml(candidateSearch)}" placeholder="Search candidates, roles or skills" aria-label="Search candidates"></div><div class="candidate-list">${candidateRows(visibleCandidates)}</div><div id="recruitment-candidate-pagination">${paginationControls(state.recruitmentCandidatePage, state.recruitmentPageSize, candidates.length, "recruitment-candidate")}</div></article>`;
}

async function renderApplicants() {
    const [candidates, options] = await Promise.all([api("/api/applicants"), loadOptions()]);
    state.applicants = candidates;
    state.options = options;
    renderApplicantList();
}

function renderApplicantList() {
    const candidates = state.applicants;
    const pipeline = candidates.filter((candidate) => !["Hired", "Rejected"].includes(candidate.stage));
    const recruited = candidates.filter((candidate) => candidate.stage === "Hired");
    const selected = state.applicantFilter === "Recruited" ? recruited : state.applicantFilter === "All" ? candidates : pipeline;
    const search = (document.getElementById("applicant-search")?.value || "").trim().toLowerCase();
    const filtered = selected.filter((candidate) => `${candidate.name} ${candidate.role} ${candidate.skills} ${candidate.experience}`.toLowerCase().includes(search));
    const pages = Math.max(1, Math.ceil(filtered.length / state.applicantPageSize));
    state.applicantPage = Math.min(state.applicantPage, pages);
    const visible = filtered.slice((state.applicantPage - 1) * state.applicantPageSize, state.applicantPage * state.applicantPageSize);
    app.innerHTML = `<article class="panel applicant-panel">${panelHeader("Applicants", `${filtered.length} candidates`, `<button class="text-button" data-action="new-resume-applicant">Add By Resume</button><button class="primary-button" data-action="new-applicant">＋ Add applicant</button>`)}
		<div class="people-tabs" aria-label="Filter applicants"><button class="people-tab ${state.applicantFilter === "Pipeline" ? "active" : ""}" data-applicant-filter="Pipeline">In pipeline <span>${pipeline.length}</span></button><button class="people-tab ${state.applicantFilter === "Recruited" ? "active" : ""}" data-applicant-filter="Recruited">Recruited <span>${recruited.length}</span></button><button class="people-tab ${state.applicantFilter === "All" ? "active" : ""}" data-applicant-filter="All">All <span>${candidates.length}</span></button></div><div class="directory-actions"><input class="table-search" id="applicant-search" type="search" value="${escapeHtml(search)}" placeholder="Search applicants, roles or skills" aria-label="Search applicants"></div>
		<div class="candidate-list">${candidateRows(visible, false, "Knowledge score")}</div>${paginationControls(state.applicantPage, state.applicantPageSize, filtered.length, "applicant")}</article>`;
}

async function renderInsights() {
    const data = await api("/api/insights");
    const kpiConfig = state.user?.role === "HR Admin" ? await api("/api/kpi-config") : [];
    const kpiRoles = [...new Set(kpiConfig.map((item) => item.role_id))].map((roleId) => ({ roleId, roleName: kpiConfig.find((item) => item.role_id === roleId)?.role_name, items: kpiConfig.filter((item) => item.role_id === roleId) }));
    const risks = data.risks || [];
    app.innerHTML = `<section class="content-grid"><article class="panel">${panelHeader("Retention risk", "Active employees ordered by calculated risk")}<div class="risk-list">${renderRiskRows(risks)}</div></article><article class="panel">${panelHeader("Department signals", "Active employee averages")}<div class="department-list">${data.departments.map((department) => `<div class="department-row"><div><strong>${escapeHtml(department.name)}</strong><small>${Number(department.headcount)} people · ${Number(department.satisfaction).toFixed(1)} satisfaction</small></div><div class="department-score">${Number(department.performance).toFixed(1)} performance<span class="mini-meter"><i style="width:${Math.min(100, department.risk * 100)}%"></i></span>${formatPercent(department.risk)} risk</div></div>`).join("") || `<div class="empty-state">No department data.</div>`}</div></article></section>
        <article class="panel">${panelHeader("Skill gaps", "Coverage compared with role needs")}<div class="gap-list">${data.skill_gaps.map((gap) => `<div class="gap-row"><div class="gap-label"><strong>${escapeHtml(gap.skill)}</strong><small>${Number(gap.current)}% current · ${Number(gap.required)}% target</small></div><div class="gap-meter"><span style="width:${Number(gap.current)}%"></span><i style="width:${Number(gap.required)}%"></i></div><span class="gap-value">${Number(gap.gap)} pt gap</span></div>`).join("") || `<div class="empty-state">No skill gaps identified.</div>`}</div></article>
        ${kpiRoles.length ? `<article class="panel kpi-config-panel">${panelHeader("Role KPI configuration", "HR Admin controls · active weights must total 100%")}${kpiRoles.map((role) => `<form class="kpi-config-form" id="kpi-config-${escapeHtml(role.roleId)}" data-role-id="${escapeHtml(role.roleId)}"><h3>${escapeHtml(role.roleName)}</h3>${role.items.map((item) => `<label>${escapeHtml(item.kpi_name)}<input name="${escapeHtml(item.role_kpi_id)}" type="number" min="0" max="1" step="0.01" value="${Number(item.weight).toFixed(2)}" required></label>`).join("")}<button class="text-button" type="submit">Save weights</button><p class="form-feedback" role="status"></p></form>`).join("")}</article>` : ""}
		<article class="panel">${panelHeader("Learning plans", "Development activity", `<button class="text-button" data-action="new-learning-plan">Create plan</button>`)}<div class="plan-list">${data.learning_plans.map((plan) => `<div class="plan-row"><div><strong>${escapeHtml(plan.title)}</strong><small>${escapeHtml(plan.employee_name)} · ${escapeHtml(plan.skill)}</small></div><span class="status-pill">${escapeHtml(plan.status)}</span></div>`).join("") || `<div class="empty-state">No learning plans yet.</div>`}</div></article>`;
}

function renderPolicies(policies) {
    return `<article class="panel policy-library">${panelHeader("Policy sources", `${policies.length} workspace documents`, `<button class="text-button" data-action="new-policy">Add source</button>`)}<div class="policy-list">${policies.map((policy) => `<article class="policy-card"><span class="policy-card-icon">▤</span><div><h3>${escapeHtml(policy.title)}</h3><span>${escapeHtml(policy.section)}</span><p>${escapeHtml(policy.content)}</p></div></article>`).join("") || `<div class="empty-state">No policy sources have been added.</div>`}</div></article>
		<section class="panel policy-panel policy-page-form"><div><h2 class="panel-title">Ask a policy question</h2><p class="panel-subtitle">Answers are grounded in the policy sources above.</p><div id="policy-answer" aria-live="polite"></div></div><form class="policy-form" id="policy-form"><input name="question" placeholder="Ask about leave, remote work..." minlength="3" required><button class="primary-button" type="submit">Ask</button></form></section>`;
}

async function loadOptions() {
    if (!state.options) state.options = await api("/api/options");
    return state.options;
}

async function renderPolicyPage() {
    app.innerHTML = renderPolicies(await api("/api/policies"));
}

function renderProfile() {
    app.innerHTML = `<article class="panel profile-panel">${panelHeader("Personal details", "These details are used for your workspace account.")}<form class="data-form profile-form" id="profile-form"><label>Full name<input name="name" value="${escapeHtml(state.user.name)}" minlength="2" required></label><label>Email address<input name="email" type="email" value="${escapeHtml(state.user.email)}" required></label><div class="profile-divider"><span>Change password</span><small>Leave both password fields blank to keep your current password.</small></div><label>New password<input name="password" type="password" minlength="8" autocomplete="new-password"></label><label>Confirm new password<input name="confirm_password" type="password" minlength="8" autocomplete="new-password"></label><p class="form-feedback" role="status"></p><button class="primary-button" type="submit">Save profile</button></form></article>`;
}

async function renderAdmin() {
    if (state.user.role !== "HR Admin") throw new Error("Admin access required.");
    const users = await api("/api/admin/users");
    app.innerHTML = `<article class="panel">${panelHeader("Workspace accounts", `${users.length} accounts`, `<button class="primary-button" data-action="new-account">＋ Add account</button>`)}<div class="account-list">${users.map((user) => `<div class="account-row"><span class="person-avatar">${escapeHtml(initials(user.name))}</span><div class="person"><span>${escapeHtml(user.name)}<small class="person-role">${escapeHtml(user.email)}</small></span></div><span class="account-role">${escapeHtml(user.role)}</span><span class="status-pill ${user.active ? "" : "inactive"}">${user.active ? "Active" : "Disabled"}</span><button class="text-button" data-action="toggle-account" data-id="${user.id}" ${user.id === state.user.id ? "disabled" : ""}>${user.active ? "Disable" : "Enable"}</button></div>`).join("")}</div></article>`;
}

async function loadSection(section = state.section) {
    state.section = section;
    updateHeader();
    app.innerHTML = `<div class="loading-state">Loading ${escapeHtml(sectionInfo[section]?.[0] || "workspace")}...</div>`;
    try {
        if (section === "overview") await renderOverview();
        else if (section === "employees") await renderEmployees();
        else if (section === "recruitment") await renderRecruitment();
        else if (section === "applicants") await renderApplicants();
        else if (section === "insights") await renderInsights();
        else if (section === "policies") await renderPolicyPage();
        else if (section === "profile") renderProfile();
        else if (section === "admin") await renderAdmin();
    } catch (error) {
        app.innerHTML = `<div class="error-state" role="alert">${escapeHtml(error.message || "Could not load this page.")}</div>`;
    }
}

function modal(title, formId, fields, submitLabel) {
    app.insertAdjacentHTML("beforeend", `<div class="modal-backdrop" data-action="backdrop-close"><section class="modal-panel" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}">${panelHeader(title, "", `<button class="text-button" data-action="close-modal" aria-label="Close">Close</button>`)}<form class="data-form" id="${formId}">${fields}<p class="form-feedback" role="status"></p><button class="primary-button" type="submit">${escapeHtml(submitLabel)}</button></form></section></div>`);
}

async function openModal(action) {
    if (action === "new-role") {
        const options = await loadOptions();
        modal("Create a role", "role-form", `<label>Role title<input name="title" minlength="2" required></label><label>Department<select name="department" required>${options.departments.map((department) => `<option>${escapeHtml(department)}</option>`).join("")}</select></label><label>Status<select name="status">${options.job_statuses.map((status) => `<option>${escapeHtml(status)}</option>`).join("")}</select></label>`, "Create role");
    } else if (action === "new-applicant") {
        const options = await loadOptions();
        modal("Add an applicant", "applicant-form", `<label>Candidate name<input name="name" minlength="2" required></label><label>Role<select name="role" required>${options.job_titles.map((title) => `<option>${escapeHtml(title)}</option>`).join("")}</select></label><label>Experience<input name="experience" placeholder="e.g. 5 years" required></label><label>Skills<input name="skills" placeholder="Python, SQL, AWS" minlength="2" required></label><label>Stage<select name="stage"><option>New</option><option>Screening</option><option>Interviewing</option><option>Offer</option></select></label>`, "Add applicant");
    } else if (action === "new-resume-applicant") {
        modal("Add applicant by resume", "resume-applicant-form", `<label>Resume file<input name="resume" type="file" accept=".pdf,.docx,.txt" required></label><p class="detail-copy">Upload a resume and the app will scan the document, extract the candidate details, and add them to the applicant pipeline automatically.</p>`, "Scan resume");
    } else if (action === "new-learning-plan") {
        const employees = await api("/api/employees");
        const active = employees.filter((employee) => employee.status === "Active");
        modal("Create a learning plan", "learning-plan-form", `<label>Employee<select name="employee_id" required>${active.map((employee) => `<option value="${employee.id}">${escapeHtml(employee.name)} · ${escapeHtml(employee.role)}</option>`).join("")}</select></label><label>Skill<input name="skill" minlength="2" required></label><label>Plan title<input name="title" minlength="2" required></label>`, "Create plan");
    } else if (action === "new-policy") {
        modal("Add a policy source", "policy-create-form", `<label>Title<input name="title" minlength="2" required></label><label>Section<input name="section" minlength="2" required></label><label>Policy text<textarea name="content" rows="5" minlength="10" required></textarea></label>`, "Add policy source");
    } else if (action === "new-account") {
        const options = await loadOptions();
        modal("Create a workspace account", "account-form", `<label>Full name<input name="name" minlength="2" required></label><label>Email address<input name="email" type="email" required></label><label>Role<select name="role" required>${options.admin_roles.map((role) => `<option>${escapeHtml(role)}</option>`).join("")}</select></label><label>Password<input name="password" type="password" minlength="8" required></label><label>Confirm password<input name="confirm_password" type="password" minlength="8" required></label>`, "Create account");
    }
}

async function submitForm(form) {
    const values = formValues(form);
    const feedback = (message, isError = true) => setFeedback(form, message, isError);
    try {
        if (form.id === "login-form") {
            const result = await api("/api/auth/login", { method: "POST", body: values });
            state.token = result.token;
            sessionStorage.setItem(tokenKey, result.token);
            await enterWorkspace();
        } else if (form.id === "register-form") {
            await api("/api/auth/register", { method: "POST", body: values });
            renderLoggedOut("Account created. Sign in to continue.");
        } else if (form.id === "role-form") {
            await api("/api/jobs", { method: "POST", body: values });
            await loadSection("recruitment");
        } else if (form.id === "applicant-form") {
            await api("/api/applicants", { method: "POST", body: values });
            await loadSection(state.section);
        } else if (form.id === "resume-applicant-form") {
            const resume = form.querySelector("input[name='resume']")?.files?.[0];
            if (!resume) throw new Error("Choose a resume file to scan.");
            const upload = new FormData();
            upload.append("file", resume);
            await api("/api/candidates/scan", { method: "POST", body: upload });
            feedback("Resume scanned and applicant added.", false);
            await loadSection("applicants");
        } else if (form.id === "employee-edit-form") {
            values.performance_score = Number(values.performance_score);
            values.satisfaction_score = Number(values.satisfaction_score);
            values.overtime = Number(values.overtime);
            const id = form.dataset.employeeId;
            await api(`/api/employees/${id}`, { method: "PUT", body: values });
            state.selectedEmployee = Number(id);
            await loadSection("employees");
        } else if (form.id === "profile-form") {
            if (!values.password) {
                delete values.password;
                delete values.confirm_password;
            }
            const user = await api("/api/auth/profile", { method: "PUT", body: values });
            state.user = user;
            updateHeader();
            feedback("Profile saved.", false);
        } else if (form.id === "learning-plan-form") {
            values.employee_id = Number(values.employee_id);
            await api("/api/learning-plans", { method: "POST", body: values });
            await loadSection("insights");
        } else if (form.id === "policy-create-form") {
            await api("/api/policies", { method: "POST", body: values });
            await loadSection("policies");
        } else if (form.id === "account-form") {
            await api("/api/admin/users", { method: "POST", body: values });
            await loadSection("admin");
        } else if (form.classList.contains("kpi-config-form")) {
            const items = [...form.querySelectorAll("input")].map((input) => ({ role_kpi_id: input.name, weight: Number(input.value) }));
            await api(`/api/kpi-config/${form.dataset.roleId}`, { method: "PUT", body: { items } });
            await loadSection("insights");
        } else if (form.id === "overview-policy-form" || form.id === "policy-form") {
            const result = await api("/api/policies/ask", { method: "POST", body: { question: values.question } });
            const target = document.getElementById(form.id === "policy-form" ? "policy-answer" : "overview-policy-answer");
            if (target) target.innerHTML = `<p class="answer">${escapeHtml(result.answer)}</p><p class="source">${escapeHtml((result.sources || []).join(" · "))}${result.needs_hr_review ? " · HR review needed" : ""}</p>`;
            form.reset();
        }
    } catch (error) {
        feedback(error.message || "The request could not be completed.");
    }
}

async function enterWorkspace() {
    try {
        state.user = await api("/api/auth/me");
        document.body.classList.remove("logged-out");
        shell.classList.add("sidebar-open");
        updateHeader();
        await loadSection("overview");
        refreshNotifications();
    } catch {
        state.token = null;
        sessionStorage.removeItem(tokenKey);
        renderLoggedOut("Your session expired. Please sign in again.");
    }
}

async function logout() {
    try { await api("/api/auth/logout", { method: "POST" }); } catch { /* Clear the local session regardless. */ }
    state.token = null;
    state.user = null;
    sessionStorage.removeItem(tokenKey);
    document.body.classList.remove("logged-out");
    renderLoggedOut();
}

async function refreshNotifications() {
    try {
        const result = await api("/api/notifications");
        const dot = document.getElementById("notification-dot");
        if (dot) dot.classList.toggle("hidden", result.unread_count === 0);
        if (state.notificationOpen) renderNotifications(result.notifications);
    } catch { /* Notifications are non-essential to the current view. */ }
}

function renderNotifications(notifications) {
    document.querySelector(".notification-panel")?.remove();
    const panel = document.createElement("section");
    panel.className = "notification-panel";
    panel.innerHTML = `<div class="notification-header"><div><strong>Notifications</strong><small>${notifications.length} recent updates</small></div><button class="text-button" data-action="read-all">Mark all read</button></div><div class="notification-list">${notifications.map((item) => `<button class="notification-item ${item.read_at ? "" : "unread"}" data-action="read-notification" data-id="${item.id}" data-type="${escapeHtml(item.event_type)}"><span class="notification-icon">${escapeHtml(initials(item.event_type))}</span><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.message)}</small><em>${escapeHtml(formatDate(item.created_at))}${item.actor_name ? ` · ${escapeHtml(item.actor_name)}` : ""}</em></span></button>`).join("") || `<div class="empty-state">No notifications yet.</div>`}</div>`;
    document.body.appendChild(panel);
}

function appendChatMessage(text, type) {
    const messages = document.getElementById("chatbot-messages");
    if (!messages) return null;
    const message = document.createElement("div");
    message.className = `chatbot-message ${type}`;
    message.textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
    return message;
}

document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => {
    if (!state.token || !state.user) return;
    if (button.dataset.section === "admin" && state.user?.role !== "HR Admin") return;
    loadSection(button.dataset.section);
}));

app.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action], [data-view], [data-filter], [data-applicant-filter], [data-employee]");
    if (!button) return;
    if (button.dataset.view) return loadSection(button.dataset.view);
    if (button.dataset.applicantFilter) {
        state.applicantFilter = button.dataset.applicantFilter;
        state.applicantPage = 1;
        return renderApplicantList();
    }
    if (button.dataset.filter) {
        state.employeeFilter = button.dataset.filter;
        state.employeePage = 1;
        document.querySelectorAll(".people-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.filter === state.employeeFilter));
        return employeeRows();
    }
    if (button.dataset.employee) {
        state.selectedEmployee = Number(button.dataset.employee);
        return renderEmployees();
    }
    const action = button.dataset.action;
    if (action === "show-register") return renderRegister();
    if (action === "show-login") return renderLoggedOut();
    if (action === "employee-previous" || action === "employee-next") {
        state.employeePage += action.endsWith("next") ? 1 : -1;
        return employeeRows();
    }
    if (action === "recruitment-job-previous" || action === "recruitment-job-next") {
        state.recruitmentJobPage += action.endsWith("next") ? 1 : -1;
        return renderRecruitmentView();
    }
    if (action === "recruitment-candidate-previous" || action === "recruitment-candidate-next") {
        state.recruitmentCandidatePage += action.endsWith("next") ? 1 : -1;
        return renderRecruitmentView();
    }
    if (action === "applicant-previous" || action === "applicant-next") {
        state.applicantPage += action.endsWith("next") ? 1 : -1;
        return renderApplicantList();
    }
    if (["new-role", "new-applicant", "new-resume-applicant", "new-learning-plan", "new-policy", "new-account"].includes(action)) {
        try { await openModal(action); } catch (error) { app.insertAdjacentHTML("beforeend", `<p class="error-state">${escapeHtml(error.message)}</p>`); }
    } else if (action === "close-modal" || (action === "backdrop-close" && event.target === button)) {
        button.closest(".modal-backdrop")?.remove();
    } else if (action === "toggle-employee-edit") {
        document.getElementById("employee-edit-form")?.classList.toggle("hidden");
    } else if (action === "fire-employee") {
        const reason = window.prompt("Record the reason for this status change:");
        if (!reason || reason.trim().length < 3) return;
        try {
            await api(`/api/employees/${button.dataset.id}/fire`, { method: "POST", body: { reason: reason.trim() } });
            state.selectedEmployee = Number(button.dataset.id);
            await loadSection("employees");
        } catch (error) { window.alert(error.message); }
    } else if (action === "view-candidate") {
        try {
            const candidate = await api(`/api/candidates/${button.dataset.candidate}`);
            document.getElementById("candidate-detail")?.remove();
            app.insertAdjacentHTML("beforeend", candidateDetailPanel(candidate));
            document.getElementById("candidate-detail")?.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (error) { window.alert(error.message); }
    } else if (action === "hire-applicant" || action === "reject-applicant") {
        const verb = action === "hire-applicant" ? "hire" : "reject";
        if (!window.confirm(`Are you sure you want to ${verb} this applicant?`)) return;
        try {
            await api(`/api/applicants/${button.dataset.id}/${verb}`, { method: "POST" });
            await loadSection(state.section);
        } catch (error) { window.alert(error.message); }
    } else if (action === "toggle-account") {
        try {
            await api(`/api/admin/users/${button.dataset.id}/toggle`, { method: "POST" });
            await loadSection("admin");
        } catch (error) { window.alert(error.message); }
    }
});

app.addEventListener("submit", (event) => {
    const form = event.target;
    if (form instanceof HTMLFormElement && form.id !== "chatbot-form") {
        event.preventDefault();
        submitForm(form);
    }
});

app.addEventListener("input", (event) => {
    if (event.target.id === "employee-search") {
        state.employeePage = 1;
        employeeRows();
    }
    if (event.target.id === "recruitment-candidate-search") {
        state.recruitmentCandidatePage = 1;
        const cursor = event.target.selectionStart;
        renderRecruitmentView();
        const search = document.getElementById("recruitment-candidate-search");
        search?.focus();
        search?.setSelectionRange(cursor, cursor);
    }
    if (event.target.id === "applicant-search") {
        state.applicantPage = 1;
        const cursor = event.target.selectionStart;
        renderApplicantList();
        const search = document.getElementById("applicant-search");
        search?.focus();
        search?.setSelectionRange(cursor, cursor);
    }
});

app.addEventListener("change", (event) => {
    if (["employee-department-filter", "employee-role-filter"].includes(event.target.id)) {
        state.employeePage = 1;
        employeeRows();
    }
    if (["recruitment-status-filter", "recruitment-department-filter"].includes(event.target.id)) {
        state.recruitmentJobPage = 1;
        renderRecruitmentView();
    }
    if (event.target.dataset.action === "employee-page-size") {
        state.employeePageSize = Number(event.target.value);
        state.employeePage = 1;
        employeeRows();
    }
    if (["recruitment-job-page-size", "recruitment-candidate-page-size"].includes(event.target.dataset.action)) {
        state.recruitmentPageSize = Number(event.target.value);
        state.recruitmentJobPage = 1;
        state.recruitmentCandidatePage = 1;
        renderRecruitmentView();
    }
    if (event.target.dataset.action === "applicant-page-size") {
        state.applicantPageSize = Number(event.target.value);
        state.applicantPage = 1;
        renderApplicantList();
    }
});

document.getElementById("refresh-button")?.addEventListener("click", () => loadSection(state.section));
document.getElementById("sidebar-toggle")?.addEventListener("click", () => shell.classList.toggle("sidebar-open"));
document.getElementById("account-button")?.addEventListener("click", () => loadSection("profile"));
document.getElementById("logout-button")?.addEventListener("click", logout);
document.getElementById("notification-button")?.addEventListener("click", async () => {
    state.notificationOpen = !state.notificationOpen;
    if (!state.notificationOpen) return document.querySelector(".notification-panel")?.remove();
    try {
        const result = await api("/api/notifications");
        renderNotifications(result.notifications);
    } catch (error) { window.alert(error.message); }
});

document.body.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action='read-notification'], [data-action='read-all']");
    if (!button) {
        if (state.notificationOpen && !event.target.closest(".notification-panel, #notification-button")) {
            state.notificationOpen = false;
            document.querySelector(".notification-panel")?.remove();
        }
        return;
    }
    try {
        if (button.dataset.action === "read-all") await api("/api/notifications/read-all", { method: "POST" });
        else await api(`/api/notifications/${button.dataset.id}/read`, { method: "POST" });
        const result = await api("/api/notifications");
        renderNotifications(result.notifications);
        const dot = document.getElementById("notification-dot");
        if (dot) dot.classList.toggle("hidden", result.unread_count === 0);
    } catch (error) { window.alert(error.message); }
});

document.getElementById("chatbot-launcher")?.addEventListener("click", () => {
    const panel = document.getElementById("chatbot-panel");
    panel.hidden = !panel.hidden;
    if (!panel.hidden) document.getElementById("chatbot-input")?.focus();
});
document.getElementById("chatbot-close")?.addEventListener("click", () => { document.getElementById("chatbot-panel").hidden = true; });
document.getElementById("chatbot-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = document.getElementById("chatbot-input");
    const message = input.value.trim();
    if (!message) return;
    appendChatMessage(message, "user");
    input.value = "";
    const pending = appendChatMessage("Thinking...", "assistant");
    try {
        const result = await api("/api/chat", { method: "POST", body: { message } });
        if (pending) pending.textContent = result.answer;
    } catch (error) {
        if (pending) pending.textContent = error.message;
    }
});

async function boot() {
    if (!state.token) return renderLoggedOut();
    await enterWorkspace();
}

boot();
