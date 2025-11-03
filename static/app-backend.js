class DataQualityDashboard {
    constructor() {
        this.currentFile = null;
        this.currentFileId = null;
        this.analysisResults = null;
        this.history = [];

        this.init();
    }

    async init() {
        this.loadUserProfile();
        this.setupNavigation();
        this.setupFileUpload();
        this.setupButtons();
        await this.loadHistory();
    }


    loadUserProfile() {
        // Load user data from localStorage
        const userDataString = localStorage.getItem('currentUser');

        if (userDataString) {
            try {
                const userData = JSON.parse(userDataString);

                // Update username display
                const userNameElement = document.getElementById('user-display-name');
                if (userNameElement && userData.username) {
                    userNameElement.textContent = userData.username;
                }
            } catch (error) {
                console.error('Error loading user profile:', error);
            }
        }
    }


    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');

        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();

                // Update active nav item
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');

                // Show corresponding view
                const viewName = item.dataset.view;
                this.showView(viewName);
            });
        });

        // Add logout functionality to user avatar
        const userAvatar = document.querySelector('.user-avatar');
        if (userAvatar) {
            userAvatar.addEventListener('click', () => this.logout());
            userAvatar.style.cursor = 'pointer';
            userAvatar.title = 'Click to logout';
        }
    }

    showView(viewName) {
        const views = document.querySelectorAll('.view');
        views.forEach(view => view.classList.remove('active'));

        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
        }
    }

    async logout() {
        if (confirm('Are you sure you want to logout?')) {
            try {
                // Clear user data from localStorage
                localStorage.removeItem('currentUser');

                await fetch('/auth/logout', { method: 'POST' });
                window.location.href = '/auth/login';
            } catch (error) {
                console.error('Logout error:', error);
            }
        }
    }


    setupFileUpload() {
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');

        // Click to upload
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });

        // File selection
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFile(file);
            }
        });

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');

            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith('.csv')) {
                this.handleFile(file);
            } else {
                alert('Please upload a CSV file');
            }
        });
    }

    async handleFile(file) {
        if (file.size > 50 * 1024 * 1024) {
            alert('File size exceeds 50MB limit');
            return;
        }

        this.currentFile = file;

        // Show progress
        this.showProgress();
        this.updateProgressLabel('Uploading file...');

        try {
            // Upload file to backend
            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                const error = await uploadResponse.json();
                throw new Error(error.message || 'Upload failed');
            }

            const uploadData = await uploadResponse.json();
            this.currentFileId = uploadData.file_id;

            this.updateProgressLabel('Analyzing data...');
            this.updateProgress(50);

            const analyzeResponse = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ file_id: this.currentFileId })
            });

            if (!analyzeResponse.ok) {
                const error = await analyzeResponse.json();
                throw new Error(error.message || 'Analysis failed');
            }

            const analyzeData = await analyzeResponse.json();
            this.analysisResults = analyzeData.data;

            this.updateProgress(100);
            this.updateProgressLabel('Complete!');

            this.updateStats(this.analysisResults);
            await this.loadHistory();

            setTimeout(() => {
                this.hideProgress();
            }, 500);

            setTimeout(() => {
                this.updateAnalysisView(this.analysisResults);
                document.querySelector('[data-view="analyze"]').click();
            }, 800);

        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
            this.hideProgress();
        }
    }

    showProgress() {
        document.querySelector('.upload-content').style.display = 'none';
        document.getElementById('upload-progress').style.display = 'block';
        this.updateProgress(0);
    }

    updateProgress(percent) {
        document.getElementById('progress-fill').style.width = percent + '%';
        document.getElementById('progress-percent').textContent = Math.floor(percent) + '%';
    }

    updateProgressLabel(label) {
        document.getElementById('progress-label').textContent = label;
    }

    hideProgress() {
        document.querySelector('.upload-content').style.display = 'block';
        document.getElementById('upload-progress').style.display = 'none';
        document.getElementById('progress-fill').style.width = '0%';
    }

    updateStats(results) {
        document.getElementById('stat-rows').textContent = results.totalRows.toLocaleString();
        document.getElementById('stat-columns').textContent = results.totalColumns;
        document.getElementById('stat-size').textContent = results.fileSize;
        document.getElementById('stat-score').textContent = results.qualityScore;

        document.getElementById('stats-grid').style.display = 'grid';
    }

    updateAnalysisView(results) {
        const scoreDisplay = document.getElementById('quality-score-display');
        scoreDisplay.textContent = results.qualityScore;

        const circumference = 534;
        const offset = circumference - (results.qualityScore / 100) * circumference;
        document.getElementById('score-circle').style.strokeDashoffset = offset;

        const scoreCircle = document.getElementById('score-circle');
        if (results.qualityScore >= 80) {
            scoreCircle.style.stroke = '#00FF94';
            scoreDisplay.style.color = '#00FF94';
        } else if (results.qualityScore >= 60) {
            scoreCircle.style.stroke = '#FFB800';
            scoreDisplay.style.color = '#FFB800';
        } else {
            scoreCircle.style.stroke = '#FF006E';
            scoreDisplay.style.color = '#FF006E';
        }

        const summaryText = this.generateSummaryText(results);
        document.getElementById('quality-summary-text').textContent = summaryText;
        document.getElementById('analysis-subtitle').textContent = results.filename;

        const completeness = 100 - (results.columns.reduce((sum, col) =>
            sum + parseFloat(col.missingPercentage), 0) / results.columns.length);
        const validity = results.issues.filter(i => i.type === 'Invalid Format').length === 0;
        const consistency = results.issues.filter(i => i.type === 'Logical Inconsistency').length === 0;

        document.getElementById('indicator-complete').classList.toggle('active', completeness > 90);
        document.getElementById('indicator-valid').classList.toggle('active', validity);
        document.getElementById('indicator-consistent').classList.toggle('active', consistency);

        this.renderIssues(results.issues);

        this.renderColumnsTable(results.columns);
    }

    generateSummaryText(results) {
        if (results.qualityScore >= 80) {
            return 'Excellent data quality. Minor issues detected. Dataset is ready for analysis.';
        } else if (results.qualityScore >= 60) {
            return 'Good data quality with some concerns. Review flagged issues before proceeding.';
        } else if (results.qualityScore >= 40) {
            return 'Moderate data quality issues detected. Data cleaning recommended before analysis.';
        } else {
            return 'Significant data quality issues found. Extensive data preparation required.';
        }
    }

    renderIssues(issues) {
        const issuesGrid = document.getElementById('issues-grid');
        const issuesCount = document.getElementById('issues-count');

        issuesCount.textContent = `${issues.length} issue${issues.length !== 1 ? 's' : ''}`;

        if (issues.length === 0) {
            issuesGrid.innerHTML = `
                <div class="empty-state">
                    <svg class="empty-icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="32" cy="32" r="24"/>
                        <path d="M20 32l8 8 16-16"/>
                    </svg>
                    <p class="empty-text">No issues detected</p>
                </div>
            `;
            return;
        }

        issuesGrid.innerHTML = issues.map((issue, index) => `
            <div class="issue-card ${issue.severity}" data-issue-index="${index}">
                <div class="issue-header">
                    <div class="issue-type">${issue.type}</div>
                    <div class="issue-count">${issue.count}</div>
                </div>
                <h4 class="issue-title">${issue.column || 'Dataset'}</h4>
                <p class="issue-description">${issue.description}</p>
            </div>
        `).join('');

        // Add click handlers to issue cards
        document.querySelectorAll('.issue-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const issueIndex = parseInt(card.dataset.issueIndex);
                this.showIssueDetail(issueIndex);
            });
        });
    }

    renderColumnsTable(columns) {
        const columnsTable = document.getElementById('columns-table');

        let html = `
            <div class="column-row header">
                <div class="column-name">Column Name</div>
                <div class="column-type">Type</div>
                <div class="column-missing">Missing</div>
                <div class="column-unique">Unique</div>
                <div class="column-status">Status</div>
            </div>
        `;

        columns.forEach(col => {
            const status = parseFloat(col.missingPercentage) > 10 ? 'error' :
                          parseFloat(col.missingPercentage) > 5 ? 'warning' : 'ok';
            const statusLabel = status === 'error' ? 'Poor' :
                               status === 'warning' ? 'Fair' : 'Good';

            html += `
                <div class="column-row">
                    <div class="column-name">${col.name}</div>
                    <div class="column-type">${col.type}</div>
                    <div class="column-missing">${col.missingPercentage}%</div>
                    <div class="column-unique">${col.uniquePercentage}%</div>
                    <div class="column-status">
                        <span class="status-badge ${status}">${statusLabel}</span>
                    </div>
                </div>
            `;
        });

        columnsTable.innerHTML = html;
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/history');

            if (!response.ok) {
                throw new Error('Failed to load history');
            }

            const data = await response.json();
            this.history = data.history || [];
            this.renderHistory();

        } catch (error) {
            console.error('Error loading history:', error);
            this.history = [];
            this.renderHistory();
        }
    }

    async clearHistory(button) {
        if (button) {
            button.disabled = true;
        }

        try {
            const response = await fetch('/api/history', {
                method: 'DELETE'
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.message || 'Failed to clear history');
            }

            this.history = [];
            this.renderHistory();

            alert(result.message || 'History cleared successfully');
        } catch (error) {
            console.error('Error clearing history:', error);
            alert('Failed to clear history: ' + error.message);
        } finally {
            await this.loadHistory();
            if (button) {
                button.disabled = false;
            }
        }
    }

    renderHistory() {
        const historyList = document.getElementById('history-list');

        if (this.history.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <svg class="empty-icon" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="32" cy="32" r="24"/>
                        <polyline points="32 18 32 32 42 38"/>
                    </svg>
                    <p class="empty-text">No analysis history yet</p>
                </div>
            `;
            return;
        }

        historyList.innerHTML = this.history.map(item => `
            <div class="history-item" data-analysis-id="${item.id}">
                <div class="history-score">
                    <div class="history-score-value">${item.qualityScore}</div>
                </div>
                <div class="history-info">
                    <div class="history-filename">${item.filename}</div>
                    <div class="history-meta">${item.totalRows} rows × ${item.totalColumns} columns · ${item.issuesCount} issues</div>
                </div>
                <div class="history-date">${this.formatDate(item.timestamp)}</div>
                <button class="history-action" onclick="dashboard.viewHistoryItem(${item.id})">View</button>
            </div>
        `).join('');
    }

    async viewHistoryItem(analysisId) {
        try {
            const response = await fetch(`/api/results/${analysisId}`);

            if (!response.ok) {
                throw new Error('Failed to load analysis');
            }

            const data = await response.json();
            this.analysisResults = data.data;

            this.updateAnalysisView(this.analysisResults);
            this.updateStats(this.analysisResults);
            document.querySelector('[data-view="analyze"]').click();

        } catch (error) {
            console.error('Error loading analysis:', error);
            alert('Failed to load analysis');
        }
    }

    showIssueDetail(issueIndex) {
        if (!this.analysisResults || !this.analysisResults.issues) {
            return;
        }

        const issue = this.analysisResults.issues[issueIndex];
        if (!issue) return;

        // Store current issue for table loading
        this.currentIssue = issue;

        // Populate panel content
        document.getElementById('detail-issue-type').textContent = issue.type;
        document.getElementById('detail-severity').textContent = issue.severity;
        document.getElementById('detail-severity').className = `detail-severity ${issue.severity}`;
        document.getElementById('detail-title').textContent = issue.column || 'Dataset';
        document.getElementById('detail-description').textContent = issue.description;
        document.getElementById('detail-count').textContent = issue.count.toLocaleString();

        // Set percentage
        const percentage = issue.percentage ||
            ((issue.count / this.analysisResults.totalRows) * 100).toFixed(1);
        document.getElementById('detail-percentage').textContent = percentage + '%';

        // Generate context-specific content
        this.generateDetailContent(issue);

        // Reset table section
        document.getElementById('affected-rows-section').style.display = 'none';
        document.getElementById('detail-panel').classList.remove('expanded');
        document.getElementById('detail-action').textContent = 'View Affected Rows';
        this.currentPage = 1;
        this.tableExpanded = false;

        // Show panel
        document.getElementById('detail-backdrop').classList.add('active');
        document.getElementById('detail-panel').classList.add('active');

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    hideIssueDetail() {
        document.getElementById('detail-backdrop').classList.remove('active');
        document.getElementById('detail-panel').classList.remove('active');
        document.getElementById('detail-panel').classList.remove('expanded');
        document.getElementById('affected-rows-section').style.display = 'none';
        document.body.style.overflow = '';
        this.currentIssue = null;
        this.tableExpanded = false;
    }

    generateDetailContent(issue) {
        const buttonSection = document.getElementById('ai-analysis-button-section');
        const buttonContainer = document.getElementById('ai-analysis-button-container');
        const summarySection = document.getElementById('executive-summary');
        const summaryText = document.getElementById('summary-text');
        const fullSections = document.getElementById('full-analysis-sections');
        const impactEl = document.getElementById('detail-impact');
        const recommendationsEl = document.getElementById('detail-recommendations');
        const contextEl = document.getElementById('detail-context');

        if (!buttonSection || !buttonContainer || !summarySection || !fullSections || !impactEl || !recommendationsEl || !contextEl) {
            return;
        }

        // Reset previous content
        summarySection.style.display = 'none';
        summaryText.innerHTML = '';
        fullSections.style.display = 'none';
        impactEl.innerHTML = '';
        recommendationsEl.innerHTML = '';
        contextEl.innerHTML = '';

        // Show button section with contextual messaging
        const isOutlier = issue.type === 'Statistical Outlier';
        const helperCopy = isOutlier
            ? 'Click the button below to generate AI-powered insights for these outliers.'
            : `Click the button below to generate AI insights for this ${issue.type.toLowerCase()} issue.`;
        const buttonLabel = isOutlier ? 'Generate Outlier Analysis' : 'Generate Analysis';

        const placeholderHTML = `
            <div class="ai-analysis-container" id="ai-analysis-container">
                <p style="color: var(--cool-gray); margin-bottom: var(--space-4);">
                    ${helperCopy}
                </p>
                <button class="btn-secondary" id="generate-analysis-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                        <line x1="12" y1="22.08" x2="12" y2="12"></line>
                    </svg>
                    ${buttonLabel}
                </button>
            </div>
        `;

        buttonSection.style.display = 'block';
        buttonContainer.innerHTML = placeholderHTML;

        // Setup button click handler
        setTimeout(() => {
            const btn = document.getElementById('generate-analysis-btn');
            if (btn) {
                btn.addEventListener('click', () => this.generateAIAnalysis(issue));
            }
        }, 0);
    }

    generateImpactAnalysis(issue) {
        const impacts = {
            'Missing Values': `
                <p><strong>Data Completeness Impact:</strong> ${issue.count} records have incomplete information in the "${issue.column || 'affected'}" field, representing ${issue.percentage || 'a portion of'} your dataset.</p>
                <p><strong>Analytical Impact:</strong> Missing values can skew statistical analysis, reduce model accuracy, and lead to biased insights if not properly handled.</p>
                <p><strong>Business Impact:</strong> Incomplete patient or claim records may delay processing, affect reporting accuracy, and impact operational efficiency.</p>
            `,
            'Invalid Format': `
                <p><strong>Data Quality Impact:</strong> ${issue.count} entries contain formatting inconsistencies that don't match expected patterns.</p>
                <p><strong>System Impact:</strong> Invalid formats can cause integration failures, processing errors, and data pipeline disruptions.</p>
                <p><strong>Compliance Impact:</strong> Improperly formatted healthcare data may violate industry standards and regulatory requirements.</p>
            `,
            'Statistical Outlier': 'AI_GENERATED',
            'Logical Inconsistency': `
                <p><strong>Data Integrity Impact:</strong> ${issue.count} records contain logically impossible or contradictory values.</p>
                <p><strong>Trust Impact:</strong> Inconsistent data undermines confidence in analytics and decision-making processes.</p>
                <p><strong>Operational Impact:</strong> Logical errors may indicate upstream data collection or system integration issues requiring attention.</p>
            `,
            'Invalid Date': `
                <p><strong>Temporal Data Impact:</strong> ${issue.count} date entries are invalid, malformed, or chronologically impossible.</p>
                <p><strong>Timeline Impact:</strong> Incorrect dates disrupt temporal analysis, trend identification, and historical reporting.</p>
                <p><strong>Audit Impact:</strong> Date inconsistencies can create compliance issues and complicate audit trails in healthcare contexts.</p>
            `,
            'Business Rule Violation': `
                <p><strong>Rule Compliance Impact:</strong> ${issue.count} records violate established business logic or operational constraints.</p>
                <p><strong>Process Impact:</strong> Rule violations may indicate process gaps, training needs, or system configuration issues.</p>
                <p><strong>Quality Control Impact:</strong> These exceptions require review to determine if rules need adjustment or data needs correction.</p>
            `,
            'Duplicate Records': `
                <p><strong>Data Redundancy Impact:</strong> ${issue.count} duplicate entries inflate dataset size and skew frequency-based analyses.</p>
                <p><strong>Accuracy Impact:</strong> Duplicates can double-count events, inflate metrics, and produce misleading reports.</p>
                <p><strong>Storage Impact:</strong> Redundant records waste storage space and increase processing overhead unnecessarily.</p>
            `
        };

        return impacts[issue.type] || `<p>Analyzing impact of ${issue.count} affected records...</p>`;
    }

    generateRecommendations(issue) {
        const recommendations = {
            'Missing Values': `
                <ul class="recommendation-list">
                    <li>Review data collection processes to identify why values are missing</li>
                    <li>Implement validation rules at data entry points to reduce future gaps</li>
                    <li>Consider imputation strategies (mean, median, mode) for numerical fields</li>
                    <li>Flag records with critical missing values for manual review</li>
                    <li>Establish data completeness thresholds for different field types</li>
                </ul>
            `,
            'Invalid Format': `
                <ul class="recommendation-list">
                    <li>Standardize input formats using dropdown menus or formatted input fields</li>
                    <li>Implement real-time validation to catch formatting errors at entry</li>
                    <li>Create data transformation scripts to normalize existing invalid entries</li>
                    <li>Document accepted formats and train staff on data entry standards</li>
                    <li>Use regular expressions to validate common formats (email, phone, dates)</li>
                </ul>
            `,
            'Statistical Outlier': 'AI_GENERATED',
            'Logical Inconsistency': `
                <ul class="recommendation-list">
                    <li>Implement cross-field validation rules to prevent logical conflicts</li>
                    <li>Review and correct inconsistent records through data cleansing</li>
                    <li>Establish data governance policies to prevent future inconsistencies</li>
                    <li>Create automated checks for common logical relationship violations</li>
                    <li>Train staff on data integrity principles and common pitfalls</li>
                </ul>
            `,
            'Invalid Date': `
                <ul class="recommendation-list">
                    <li>Use date picker components to ensure proper date formatting</li>
                    <li>Implement date range validations (e.g., birth dates must be in past)</li>
                    <li>Standardize on a single date format across all systems</li>
                    <li>Add business logic checks for chronological relationships</li>
                    <li>Review timezone handling for date-time fields</li>
                </ul>
            `,
            'Business Rule Violation': `
                <ul class="recommendation-list">
                    <li>Review business rules for accuracy and current relevance</li>
                    <li>Implement automated rule validation at transaction time</li>
                    <li>Create exception workflows for legitimate rule violations</li>
                    <li>Document approved exceptions with authorization trails</li>
                    <li>Regularly audit rule compliance and adjust rules as needed</li>
                </ul>
            `,
            'Duplicate Records': `
                <ul class="recommendation-list">
                    <li>Implement unique constraints on key identifier fields</li>
                    <li>Use fuzzy matching algorithms to detect near-duplicates</li>
                    <li>Create de-duplication workflows with merge capabilities</li>
                    <li>Establish master data management practices</li>
                    <li>Review data import processes to prevent duplicate creation</li>
                </ul>
            `
        };

        return recommendations[issue.type] || `<ul class="recommendation-list"><li>Review and address affected records</li></ul>`;
    }

    generateDeltaDentalContext(issue) {
        const dentalContexts = {
            'Missing Values': `
                <p><strong>Patient Record Completeness:</strong> Complete dental records are essential for treatment continuity and claims processing. Missing patient information can delay appointments, complicate billing, and impact care quality.</p>
                <p><strong>Claims Processing:</strong> Incomplete claim data may result in denials, resubmission requirements, and delayed reimbursements. Ensure all required fields (procedure codes, dates of service, provider information) are captured.</p>
                <p><strong>HIPAA Compliance:</strong> Maintain complete audit trails and patient history as required by healthcare privacy regulations.</p>
            `,
            'Invalid Format': `
                <p><strong>Dental Procedure Codes:</strong> Ensure CDT (Current Dental Terminology) codes are properly formatted and current. Invalid codes will cause automatic claim rejections.</p>
                <p><strong>Provider Identification:</strong> NPI numbers, tax IDs, and license numbers must follow standard formats for successful claims submission and provider verification.</p>
                <p><strong>Patient Identifiers:</strong> Member IDs, policy numbers, and DOB formats must match Delta Dental's system requirements for accurate eligibility verification.</p>
            `,
            'Statistical Outlier': 'AI_GENERATED',
            'Logical Inconsistency': `
                <p><strong>Clinical Logic:</strong> Ensure treatment dates align logically (e.g., follow-ups after initial consultations), age-appropriate procedures, and valid provider-procedure relationships.</p>
                <p><strong>Insurance Logic:</strong> Verify coverage dates encompass service dates, procedure eligibility matches plan type, and benefit limits haven't been exceeded.</p>
                <p><strong>Claim Adjudication:</strong> Logical consistency is critical for automated claims processing. Inconsistencies trigger manual review, delaying payments.</p>
            `,
            'Invalid Date': `
                <p><strong>Date of Service Accuracy:</strong> Correct service dates are crucial for claims payment, coordination of benefits, and fraud prevention.</p>
                <p><strong>Eligibility Verification:</strong> Patient eligibility must be verified against service dates to ensure coverage was active at time of treatment.</p>
                <p><strong>Timely Filing:</strong> Delta Dental has specific timelines for claim submission. Accurate dates ensure compliance with filing deadlines.</p>
            `,
            'Business Rule Violation': `
                <p><strong>Coverage Rules:</strong> Delta Dental plans have specific coverage rules (frequency limitations, age restrictions, pre-authorization requirements) that must be validated.</p>
                <p><strong>Network Requirements:</strong> In-network vs. out-of-network provider rules affect reimbursement levels and member cost-sharing.</p>
                <p><strong>Coordination of Benefits:</strong> When patients have multiple insurance plans, proper COB rules must be applied to prevent overpayment.</p>
            `,
            'Duplicate Records': `
                <p><strong>Duplicate Claims:</strong> Multiple submissions of the same claim can result in overpayment, requiring recovery and investigation for potential fraud.</p>
                <p><strong>Patient Matching:</strong> Duplicate patient records lead to fragmented treatment history, eligibility errors, and member service issues.</p>
                <p><strong>Provider Credentialing:</strong> Duplicate provider records complicate network management, payment accuracy, and quality reporting.</p>
            `
        };

        return dentalContexts[issue.type] || `<p>Ensure data quality aligns with Delta Dental's healthcare standards and regulatory requirements.</p>`;
    }

    async generateAIAnalysis(issue) {
        const btn = document.getElementById('generate-analysis-btn');
        const container = document.getElementById('ai-analysis-container');

        if (!btn || !container) return;

        // Show loading state
        btn.disabled = true;
        btn.innerHTML = `
            <div style="width: 16px; height: 16px; border: 2px solid var(--soft-gray); border-top-color: var(--electric-cyan); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
            Generating Analysis...
        `;

        try {
            if (!this.analysisResults || !this.analysisResults.analysis_id) {
                throw new Error('Analysis ID not found. Please re-run the analysis.');
            }

            const percentage = issue.percentage !== undefined
                ? parseFloat(issue.percentage)
                : parseFloat(((issue.count / (this.analysisResults.totalRows || 1)) * 100).toFixed(1));

            const response = await fetch(`/api/analysis/${this.analysisResults.analysis_id}/generate-issue-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    issue_type: issue.type,
                    column: issue.column,
                    severity: issue.severity,
                    count: issue.count,
                    percentage,
                    description: issue.description
                })
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message || 'Failed to generate analysis');
            }

            // Parse the markdown-formatted response
            const analysisText = result.analysis;

            // Split into sections based on markdown headers (await because it's now async)
            const sections = await this.parseMarkdownSections(analysisText);

            // Hide button section and show analysis results
            document.getElementById('ai-analysis-button-section').style.display = 'none';

            // Display the AI-generated content in the appropriate sections
            document.getElementById('detail-impact').innerHTML = sections.impact || '<p>Analysis unavailable.</p>';
            document.getElementById('detail-recommendations').innerHTML = sections.recommendations || '<p>Recommendations unavailable.</p>';
            document.getElementById('detail-context').innerHTML = sections.context || '<p>Context unavailable.</p>';

            // Extract and display executive summary
            if (sections.summary) {
                document.getElementById('executive-summary').style.display = 'block';
                document.getElementById('summary-text').innerHTML = sections.summary;

                // Setup expand/collapse button
                const expandBtn = document.getElementById('btn-show-full-analysis');
                if (expandBtn) {
                    expandBtn.onclick = () => this.toggleFullAnalysis();
                }
            } else {
                // No summary, show full analysis directly
                document.getElementById('executive-summary').style.display = 'none';
                document.getElementById('full-analysis-sections').style.display = 'block';
            }

        } catch (error) {
            console.error('Error generating AI analysis:', error);
            container.innerHTML = `
                <p style="color: var(--error); margin-bottom: var(--space-4);">
                    Failed to generate analysis: ${error.message}
                </p>
                <button class="btn-secondary" id="generate-analysis-btn-retry">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                    </svg>
                    Retry
                </button>
            `;

            // Setup retry button
            setTimeout(() => {
                const retryBtn = document.getElementById('generate-analysis-btn-retry');
                if (retryBtn) {
                    retryBtn.addEventListener('click', () => this.generateAIAnalysis(issue));
                }
            }, 0);
        }
    }

    async parseMarkdownSections(markdown) {
        // Parse markdown response into sections
        const sections = {
            summary: '',
            impact: '',
            recommendations: '',
            context: ''
        };

        // Helper function to ensure string output
        const ensureString = (value, sectionName) => {
            if (typeof value !== 'string') {
                console.error(`${sectionName} is not a string:`, typeof value, value);
                return '';
            }
            return value;
        };

        // Extract executive summary
        const summaryMatch = markdown.match(/###\s*Executive Summary\s*([\s\S]*?)(?=###|$)/i);
        if (summaryMatch) {
            const result = await this.formatMarkdownContent(summaryMatch[1].trim());
            sections.summary = ensureString(result, 'summary');
        }

        // Split by markdown headers (### Header)
        const impactMatch = markdown.match(/###\s*Impact Analysis\s*([\s\S]*?)(?=###|$)/i);
        const recommendationsMatch = markdown.match(/###\s*Recommended Actions\s*([\s\S]*?)(?=###|$)/i);
        const contextMatch = markdown.match(/###\s*Healthcare Context\s*([\s\S]*?)(?=###|$)/i);

        if (impactMatch) {
            const result = await this.formatMarkdownContent(impactMatch[1].trim());
            sections.impact = ensureString(result, 'impact');
        }

        if (recommendationsMatch) {
            const result = await this.formatMarkdownContent(recommendationsMatch[1].trim());
            sections.recommendations = ensureString(result, 'recommendations');
        }

        if (contextMatch) {
            const result = await this.formatMarkdownContent(contextMatch[1].trim());
            sections.context = ensureString(result, 'context');
        }

        // Final verification
        console.log('Parsed sections types:', {
            summary: typeof sections.summary,
            impact: typeof sections.impact,
            recommendations: typeof sections.recommendations,
            context: typeof sections.context
        });

        return sections;
    }

    async formatMarkdownContent(text) {
        // Check if libraries are loaded
        if (typeof marked === 'undefined') {
            console.error('marked.js library not loaded');
            // Fallback to basic formatting
            return this.fallbackMarkdownFormat(text);
        }

        if (typeof DOMPurify === 'undefined') {
            console.error('DOMPurify library not loaded');
            // Fallback to basic formatting
            return this.fallbackMarkdownFormat(text);
        }

        try {
            // Parse markdown to HTML using marked.js (await because it returns a Promise)
            // Don't use custom renderers - they receive complex token objects in marked.js v16+
            let rawHtml = await marked.parse(text, {
                breaks: true,        // Convert single line breaks to <br>
                gfm: true,           // GitHub Flavored Markdown
                headerIds: false,    // Don't add IDs to headers
                mangle: false        // Don't escape email addresses
            });

            // Ensure rawHtml is a string
            if (typeof rawHtml !== 'string') {
                console.warn('marked.parse did not return a string, converting...', typeof rawHtml);
                rawHtml = String(rawHtml);
            }

            // Post-process HTML to add custom classes
            let processedHtml = rawHtml;

            // Add custom class to unordered lists
            processedHtml = processedHtml.replace(
                /<ul>/g,
                '<ul class="recommendation-list">'
            );

            // Convert subsection labels: <p><strong>Label:</strong> text</p>
            // to: <p class="subsection-content"><span class="subsection-label">Label:</span> text</p>
            processedHtml = processedHtml.replace(
                /<p><strong>([^<]+):<\/strong>\s*([\s\S]*?)<\/p>/g,
                '<p class="subsection-content"><span class="subsection-label">$1:</span> $2</p>'
            );

            // Sanitize HTML for XSS protection (healthcare security requirement)
            const cleanHtml = DOMPurify.sanitize(processedHtml, {
                ALLOWED_TAGS: ['strong', 'p', 'ul', 'ol', 'li', 'span', 'br', 'hr', 'em'],
                ALLOWED_ATTR: ['class'],
                KEEP_CONTENT: true
            });

            // Final safety check: ensure we return a string
            const finalResult = typeof cleanHtml === 'string' ? cleanHtml : String(cleanHtml);

            console.log('formatMarkdownContent returning:', {
                type: typeof finalResult,
                length: finalResult.length,
                preview: finalResult.substring(0, 100)
            });

            return finalResult;
        } catch (error) {
            console.error('Error parsing markdown:', error);
            const fallback = this.fallbackMarkdownFormat(text);
            console.log('formatMarkdownContent fallback type:', typeof fallback);
            return fallback;
        }
    }

    fallbackMarkdownFormat(text) {
        // Basic fallback formatting if libraries don't load
        let html = text.split('\n\n').map(para => {
            para = para.trim();
            if (!para) return '';

            // Handle lists
            if (para.match(/^[-*]\s/m)) {
                const items = para.split('\n')
                    .filter(line => line.trim().match(/^[-*]\s/))
                    .map(line => line.replace(/^[-*]\s/, '').trim())
                    .map(item => {
                        // Process bold text in list items
                        item = item.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
                        return `<li>${item}</li>`;
                    })
                    .join('\n');
                return `<ul class="recommendation-list">${items}</ul>`;
            }
            // Handle horizontal rules
            if (para.match(/^(\*{3,}|-{3,}|_{3,})$/)) {
                return '<hr>';
            }
            // Handle labeled subsections
            if (para.match(/^\*\*([^*]+):\*\*/)) {
                para = para.replace(/^\*\*([^*]+):\*\*/, '<span class="subsection-label">$1:</span>');
                para = para.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
                return `<p class="subsection-content">${para}</p>`;
            }
            // Regular paragraphs
            para = para.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            return `<p>${para}</p>`;
        }).join('\n');

        return html;
    }

    toggleFullAnalysis() {
        const fullSections = document.getElementById('full-analysis-sections');
        const expandIcon = document.getElementById('expand-icon');
        const expandText = document.getElementById('expand-text');

        if (fullSections.style.display === 'none') {
            // Expand
            fullSections.style.display = 'block';
            expandText.textContent = 'Hide Full Analysis';
            expandIcon.style.transform = 'rotate(180deg)';
        } else {
            // Collapse
            fullSections.style.display = 'none';
            expandText.textContent = 'Show Full Analysis';
            expandIcon.style.transform = 'rotate(0deg)';
        }
    }

    setupButtons() {
        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearUpload();
        });

        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportReport();
        });

        const clearHistoryBtn = document.getElementById('clear-history-btn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', async () => {
                if (!confirm('Clear all history?')) {
                    return;
                }

                await this.clearHistory(clearHistoryBtn);
            });
        }

        // Detail panel event listeners
        document.getElementById('detail-close').addEventListener('click', () => {
            this.hideIssueDetail();
        });

        document.getElementById('detail-dismiss').addEventListener('click', () => {
            this.hideIssueDetail();
        });

        document.getElementById('detail-backdrop').addEventListener('click', () => {
            this.hideIssueDetail();
        });

        // Keyboard support - ESC to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideIssueDetail();
            }
        });

        // "View Affected Rows" button - toggle table view
        document.getElementById('detail-action').addEventListener('click', () => {
            if (this.tableExpanded) {
                this.collapseAffectedRows();
            } else {
                this.loadAffectedRows(1);
            }
        });

        // Pagination button handlers
        document.getElementById('btn-prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.loadAffectedRows(this.currentPage - 1);
            }
        });

        document.getElementById('btn-next-page').addEventListener('click', () => {
            if (this.hasMorePages) {
                this.loadAffectedRows(this.currentPage + 1);
            }
        });
    }

    clearUpload() {
        this.currentFile = null;
        this.currentFileId = null;
        this.analysisResults = null;
        document.getElementById('file-input').value = '';
        document.getElementById('stats-grid').style.display = 'none';
    }

    async exportReport() {
        if (!this.analysisResults || !this.analysisResults.analysis_id) {
            alert('No analysis to export');
            return;
        }

        try {
            window.location.href = `/api/export/${this.analysisResults.analysis_id}`;
        } catch (error) {
            console.error('Export error:', error);
            alert('Failed to export report');
        }
    }

    async loadAffectedRows(page = 1) {
        if (!this.currentIssue || !this.analysisResults) {
            return;
        }

        const analysisId = this.analysisResults.analysis_id;
        const issueType = this.currentIssue.type;
        const columnName = this.currentIssue.column || '';
        const limit = 50;
        const offset = (page - 1) * limit;

        // Show table section and loading state
        document.getElementById('affected-rows-section').style.display = 'block';
        document.getElementById('table-loading').style.display = 'flex';
        document.getElementById('table-container').style.display = 'none';
        document.getElementById('table-empty').style.display = 'none';
        document.getElementById('table-error').style.display = 'none';

        // Expand panel
        document.getElementById('detail-panel').classList.add('expanded');
        this.tableExpanded = true;

        // Update button text
        document.getElementById('detail-action').textContent = 'Collapse Table';

        // Scroll to table section
        setTimeout(() => {
            document.getElementById('affected-rows-section').scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }, 400);

        try {
            // Build query URL
            let url = `/api/analysis/${analysisId}/affected-rows?issue_type=${encodeURIComponent(issueType)}&limit=${limit}&offset=${offset}`;
            if (columnName) {
                url += `&column=${encodeURIComponent(columnName)}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || 'Failed to load affected rows');
            }

            // Hide loading, show table
            document.getElementById('table-loading').style.display = 'none';

            if (data.data.rows.length === 0) {
                document.getElementById('table-empty').style.display = 'block';
                return;
            }

            this.currentPage = page;
            this.hasMorePages = data.data.has_more;
            this.renderAffectedRowsTable(data.data);

        } catch (error) {
            console.error('Error loading affected rows:', error);
            document.getElementById('table-loading').style.display = 'none';
            document.getElementById('table-error').style.display = 'block';
            document.getElementById('table-error-message').textContent = error.message;
        }
    }

    renderAffectedRowsTable(data) {
        const { rows, columns, total_count, affected_column } = data;

        // Show table container
        document.getElementById('table-container').style.display = 'block';

        // Update row count
        const start = (this.currentPage - 1) * 50 + 1;
        const end = Math.min(start + rows.length - 1, total_count);
        document.getElementById('table-row-count').textContent =
            `Showing ${start}-${end} of ${total_count} affected rows`;

        // Generate table header
        const thead = document.getElementById('table-head');
        thead.innerHTML = `
            <tr>
                ${columns.map(col => {
                    const isRowIndex = col === 'row_index';
                    const isAffected = col === affected_column;
                    const className = isRowIndex ? 'row-index-col' : (isAffected ? 'highlight-column' : '');
                    return `<th class="${className}">${col === 'row_index' ? '#' : col}</th>`;
                }).join('')}
            </tr>
        `;

        // Generate table body
        const tbody = document.getElementById('table-body');
        tbody.innerHTML = rows.map(row => {
            return `
                <tr>
                    ${columns.map(col => {
                        const isRowIndex = col === 'row_index';
                        const isAffected = col === affected_column;
                        const className = isRowIndex ? 'row-index-col' : (isAffected ? 'highlight-column' : '');
                        const value = row[col] !== null && row[col] !== undefined ? row[col] : '—';
                        return `<td class="${className}" title="${value}">${value}</td>`;
                    }).join('')}
                </tr>
            `;
        }).join('');

        // Update pagination
        const pagination = document.getElementById('table-pagination');
        if (total_count > 50) {
            pagination.style.display = 'flex';

            const totalPages = Math.ceil(total_count / 50);
            document.getElementById('pagination-info').textContent =
                `Page ${this.currentPage} of ${totalPages}`;

            // Update button states
            const prevBtn = document.getElementById('btn-prev-page');
            const nextBtn = document.getElementById('btn-next-page');

            prevBtn.disabled = this.currentPage === 1;
            nextBtn.disabled = !this.hasMorePages;
        } else {
            pagination.style.display = 'none';
        }
    }

    collapseAffectedRows() {
        document.getElementById('affected-rows-section').style.display = 'none';
        document.getElementById('detail-panel').classList.remove('expanded');
        document.getElementById('detail-action').textContent = 'View Affected Rows';
        this.tableExpanded = false;
    }

    formatDate(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return Math.floor(diff / 60000) + ' min ago';
        if (diff < 86400000) return Math.floor(diff / 3600000) + ' hr ago';

        return date.toLocaleDateString();
    }
}

let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new DataQualityDashboard();
});
