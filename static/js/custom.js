/**
 * Get CSRF token from Django form
 * @returns {string} CSRF token
 */
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return token;
}

/**
 * Show toast notification with enhanced features
 * @param {string} message - Message to display
 * @param {string} type - Type of message (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (optional)
 * @param {boolean} showProgress - Show progress bar (optional)
 */
function showMessage(message, type = 'success', duration = null, showProgress = true) {
    // Get or create toast container
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = createToastContainer();
    }

    // Create unique toast ID
    const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    
    // Set duration based on type if not specified
    if (!duration) {
        duration = getToastDuration(type);
    }

    // Create toast element
    const toastElement = createToastElement(toastId, message, type, showProgress);
    
    // Add to container
    toastContainer.appendChild(toastElement);
    
    // Initialize Bootstrap toast with custom options
    const bsToast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration
    });

    // Show toast with animation
    setTimeout(() => {
        toastElement.classList.add('show');
        bsToast.show();
    }, 100);

    // Start progress bar animation if enabled
    if (showProgress) {
        startProgressBar(toastElement, duration);
    }

    // Auto-remove after hide
    toastElement.addEventListener('hidden.bs.toast', function() {
        setTimeout(() => {
            if (toastElement.parentNode) {
                toastElement.parentNode.removeChild(toastElement);
            }
        }, 300);
    });

    // Return toast instance for manual control
    return {
        element: toastElement,
        toast: bsToast,
        hide: () => bsToast.hide(),
        show: () => bsToast.show()
    };
}

/**
 * Create toast container if it doesn't exist
 * @returns {HTMLElement} Toast container element
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

/**
 * Create individual toast element
 * @param {string} toastId - Unique toast ID
 * @param {string} message - Toast message
 * @param {string} type - Toast type
 * @param {boolean} showProgress - Whether to show progress bar
 * @returns {HTMLElement} Toast element
 */
function createToastElement(toastId, message, type, showProgress) {
    const toastElement = document.createElement('div');
    toastElement.id = toastId;
    toastElement.className = `toast align-items-center border-0 text-white ${getToastClass(type)} mb-2`;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    // Add custom styles for better appearance
    toastElement.style.minWidth = '300px';
    toastElement.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
    toastElement.style.transform = 'translateX(100%)';
    toastElement.style.transition = 'transform 0.3s ease-in-out';
    
    const progressBarHtml = showProgress ? `
        <div class="toast-progress">
            <div class="toast-progress-bar"></div>
        </div>
    ` : '';
    
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-medium">
                <i class="fas ${getToastIcon(type)} me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        ${progressBarHtml}
    `;
    
    return toastElement;
}

/**
 * Start progress bar animation
 * @param {HTMLElement} toastElement - Toast element
 * @param {number} duration - Duration in milliseconds
 */
function startProgressBar(toastElement, duration) {
    const progressBar = toastElement.querySelector('.toast-progress-bar');
    if (!progressBar) return;
    
    // Style the progress bar
    const progressContainer = toastElement.querySelector('.toast-progress');
    progressContainer.style.cssText = `
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(255, 255, 255, 0.2);
        overflow: hidden;
    `;
    
    progressBar.style.cssText = `
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        width: 100%;
        transform: translateX(-100%);
        transition: transform ${duration}ms linear;
    `;
    
    // Start animation
    setTimeout(() => {
        progressBar.style.transform = 'translateX(0)';
    }, 100);
}

/**
 * Get toast duration based on type
 * @param {string} type - Toast type
 * @returns {number} Duration in milliseconds
 */
function getToastDuration(type) {
    switch(type) {
        case 'success': return 4000;  // 2 seconds
        case 'info': return 4000;     // 1.5 seconds
        case 'warning': return 4000;  // 2.5 seconds
        case 'error': return 4000;    // 4 seconds
        default: return 4000;
    }
}

/**
 * Get Bootstrap class for toast type
 * @param {string} type - Toast type
 * @returns {string} Bootstrap class
 */
function getToastClass(type) {
    switch(type) {
        case 'success': return 'bg-success';
        case 'error': return 'bg-danger';
        case 'warning': return 'bg-warning text-dark';
        case 'info': return 'bg-info';
        default: return 'bg-primary';
    }
}

/**
 * Get FontAwesome icon for toast type
 * @param {string} type - Toast type
 * @returns {string} FontAwesome icon class
 */
function getToastIcon(type) {
    switch(type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        case 'info': return 'fa-info-circle';
        default: return 'fa-bell';
    }
}

/**
 * Show success toast with custom message
 * @param {string} message - Success message
 * @param {number} duration - Duration in milliseconds (optional)
 */
function showSuccess(message, duration = 4000) {
    return showMessage(message, 'success', duration);
}

/**
 * Show error toast with custom message
 * @param {string} message - Error message
 * @param {number} duration - Duration in milliseconds (optional)
 */
function showError(message, duration = 8000) {
    return showMessage(message, 'error', duration);
}

/**
 * Show warning toast with custom message
 * @param {string} message - Warning message
 * @param {number} duration - Duration in milliseconds (optional)
 */
function showWarning(message, duration = 6000) {
    return showMessage(message, 'warning', duration);
}

/**
 * Show info toast with custom message
 * @param {string} message - Info message
 * @param {number} duration - Duration in milliseconds (optional)
 */
function showInfo(message, duration = 5000) {
    return showMessage(message, 'info', duration);
}

/**
 * Clear all active toasts
 */
function clearAllToasts() {
    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        const toasts = toastContainer.querySelectorAll('.toast');
        toasts.forEach(toast => {
            const bsToast = bootstrap.Toast.getInstance(toast);
            if (bsToast) {
                bsToast.hide();
            }
        });
    }
}

/**
 * Show toast with countdown timer
 * @param {string} message - Message to display
 * @param {string} type - Toast type
 * @param {number} duration - Duration in milliseconds
 */
function showToastWithCountdown(message, type = 'info', duration = 10000) {
    const countdownInterval = 1000; // Update every second
    let remaining = Math.ceil(duration / 1000);
    
    const toastInstance = showMessage(`${message} (${remaining}s)`, type, duration, true);
    
    const countdown = setInterval(() => {
        remaining--;
        if (remaining > 0) {
            const messageElement = toastInstance.element.querySelector('.toast-body');
            if (messageElement) {
                messageElement.innerHTML = `<i class="fas ${getToastIcon(type)} me-2"></i>${message} (${remaining}s)`;
            }
        } else {
            clearInterval(countdown);
        }
    }, countdownInterval);
    
    // Clear countdown if toast is manually closed
    toastInstance.element.addEventListener('hidden.bs.toast', () => {
        clearInterval(countdown);
    });
    
    return toastInstance;
}

/**
 * Simple toast function - wrapper for showMessage
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, warning, info)
 * @param {number} duration - Optional duration override
 */
function showToast(message, type = 'info', duration = null) {
    return showMessage(message, type, duration, true);
}

// ============================================================================
// BARCODE SCANNER OPTIMIZATION
// ============================================================================

/**
 * Check if any Bootstrap modal is currently open
 * @returns {boolean}
 */
function isAnyModalOpen() {
    return document.querySelectorAll('.modal.show').length > 0;
}

/**
 * Optimize input field for barcode scanner
 * @param {string} inputId - ID of the input element
 * @param {string} formId - ID of the form element
 */
function triggerFormSubmit(form) {
    if (!form) {
        return;
    }

    if (typeof form.requestSubmit === 'function') {
        form.requestSubmit();
        return;
    }

    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
}

function optimizeForBarcode(inputId = 'studentId', formId = 'entryForm', options = {}) {
    const input = document.getElementById(inputId);
    const form = document.getElementById(formId);
    
    if (!input || !form) return;

    const config = {
        autoSubmitLength: options.autoSubmitLength || 8,
        maxScanGapMs: options.maxScanGapMs || 80,
        maxScanWindowMs: options.maxScanWindowMs || 650,
        submitCooldownMs: options.submitCooldownMs || 500,
    };
    
    // Force focus and prevent losing focus
    input.focus();
    
    // Re-focus when clicking anywhere (skip if a modal is open)
    document.addEventListener('click', function(e) {
        if (isAnyModalOpen()) return;
        setTimeout(() => input.focus(), 100);
    });
    
    // Re-focus on page visibility change (skip if a modal is open)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && !isAnyModalOpen()) {
            setTimeout(() => input.focus(), 100);
        }
    });
    
    let lastInputAt = 0;
    let burstStartAt = 0;
    let burstCount = 0;
    let autoSubmitTimer = null;
    let lastAutoSubmitAt = 0;

    if (!form.dataset.barcodeConsumedValue) {
        form.dataset.barcodeConsumedValue = '';
    }

    function clearAutoSubmitTimer() {
        if (autoSubmitTimer) {
            clearTimeout(autoSubmitTimer);
            autoSubmitTimer = null;
        }
    }

    function isRapidBarcodeEntry(value) {
        const trimmedValue = value.trim();
        const now = performance.now();
        const withinRapidGap = lastInputAt === 0 || (now - lastInputAt) <= config.maxScanGapMs;

        if (!withinRapidGap) {
            burstStartAt = now;
            burstCount = 0;
        } else if (burstCount === 0) {
            burstStartAt = now;
        }

        burstCount += 1;
        lastInputAt = now;

        return trimmedValue.length >= config.autoSubmitLength &&
            burstCount >= config.autoSubmitLength &&
            (now - burstStartAt) <= config.maxScanWindowMs;
    }

    function submitIfAllowed() {
        const now = performance.now();
        const currentValue = input.value.trim();

        if (!currentValue) {
            return;
        }

        if (currentValue === form.dataset.barcodeConsumedValue) {
            return;
        }

        if (form.dataset.submitting === '1') {
            return;
        }

        if ((now - lastAutoSubmitAt) < config.submitCooldownMs) {
            return;
        }

        lastAutoSubmitAt = now;
        form.dataset.barcodeConsumedValue = currentValue;
        burstCount = 0;
        burstStartAt = 0;
        triggerFormSubmit(form);
    }
    
    input.addEventListener('input', function(e) {
        if (this.value.trim() === '') {
            form.dataset.barcodeConsumedValue = '';
        }

        if (isRapidBarcodeEntry(this.value)) {
            clearAutoSubmitTimer();
            autoSubmitTimer = setTimeout(() => {
                if (this.value.trim().length >= config.autoSubmitLength) {
                    submitIfAllowed();
                }
            }, 35);
        } else {
            clearAutoSubmitTimer();
        }
    });
    
    // Barcode scanners often send Enter after the scan; manual typing should not submit here.
    input.addEventListener('keydown', function(e) {
        const isEnterKey = e.key === 'Enter' || e.key === 'NumpadEnter' || e.keyCode === 13;

        if (isEnterKey) {
            e.preventDefault();
            clearAutoSubmitTimer();

            const value = this.value.trim();
            const rapidScan = value.length >= config.autoSubmitLength &&
                burstCount >= config.autoSubmitLength &&
                (performance.now() - burstStartAt) <= config.maxScanWindowMs;

            if (rapidScan) {
                submitIfAllowed();
            } else {
                this.focus();
            }
        }
    });
}

/**
 * Maintain input focus
 * @param {string} inputId - ID of the input element
 */
function maintainInputFocus(inputId = 'studentId') {
    // Ensure input stays focused (skip when a modal is open)
    setInterval(() => {
        if (isAnyModalOpen()) return;
        const input = document.getElementById(inputId);
        if (input && document.activeElement !== input && document.hasFocus()) {
            input.focus();
        }
    }, 1000);
    
    // Handle page focus (skip when a modal is open)
    window.addEventListener('focus', function() {
        if (isAnyModalOpen()) return;
        setTimeout(() => {
            const input = document.getElementById(inputId);
            if (input) input.focus();
        }, 100);
    });
}

// ============================================================================
// ENTRY MONITOR FUNCTIONS
// ============================================================================

/**
 * Initialize Entry Monitor
 */
function initializeEntryMonitor() {
    optimizeForBarcode('studentId', 'entryForm', { autoSubmitLength: 8 });
    maintainInputFocus('studentId');

    const entryToastContainer = document.getElementById('toastContainer') || createToastContainer();
    entryToastContainer.classList.remove('end-0');
    entryToastContainer.classList.add('entry-monitor-toast');

    const entryForm = document.getElementById('entryForm');
    const submitBtn = document.querySelector('button[type="submit"]');
    const studentIdInput = document.getElementById('studentId');

    const registrationModalElement = document.getElementById('entryRegistrationModal');
    const registrationForm = document.getElementById('entryRegistrationForm');
    const registrationSubmitBtn = document.getElementById('entryRegistrationSubmitBtn');
    const registrationStudentId = document.getElementById('registrationStudentId');
    const registrationStudentIdDisplay = document.getElementById('registrationStudentIdDisplay');
    const registrationName = document.getElementById('registrationName');
    const registrationEmail = document.getElementById('registrationEmail');
    const registrationDepartment = document.getElementById('registrationDepartment');
    const registrationModal = registrationModalElement ? new bootstrap.Modal(registrationModalElement) : null;
    let departmentsLoaded = false;

    const eightDigitIdPattern = /^\d{8}$/;

    function isValidEightDigitId(value) {
        return eightDigitIdPattern.test(value);
    }

    function populateDepartmentOptions(departments) {
        registrationDepartment.innerHTML = '<option value="">Select Department</option>';
        departments.forEach(function(department) {
            const option = document.createElement('option');
            option.value = department.id;
            option.textContent = department.name;
            registrationDepartment.appendChild(option);
        });
    }

    function fetchDepartmentsForRegistration(forceRefresh = false) {
        if (!registrationDepartment) {
            return Promise.resolve([]);
        }

        if (departmentsLoaded && !forceRefresh) {
            return Promise.resolve([]);
        }

        registrationDepartment.disabled = true;
        registrationDepartment.innerHTML = '<option value="">Loading departments...</option>';

        return axios.get('/api/departments/', { timeout: 10000 })
            .then(function(response) {
                if (response.data && response.data.status === 'success' && Array.isArray(response.data.departments)) {
                    populateDepartmentOptions(response.data.departments);
                    departmentsLoaded = true;
                    return response.data.departments;
                }

                throw new Error('Invalid department response');
            })
            .catch(function() {
                registrationDepartment.innerHTML = '<option value="">Could not load departments</option>';
                showMessage('Unable to fetch departments. Please try again.', 'error');
                throw new Error('Department fetch failed');
            })
            .finally(function() {
                registrationDepartment.disabled = false;
            });
    }

    function openRegistrationModal(scannedId) {
        if (!registrationModal) {
            showMessage('Registration form is not available right now.', 'error');
            return;
        }

        registrationStudentId.value = scannedId;
        registrationStudentIdDisplay.value = scannedId;
        registrationForm.reset();
        registrationStudentId.value = scannedId;
        registrationStudentIdDisplay.value = scannedId;

        fetchDepartmentsForRegistration()
            .finally(function() {
                registrationModal.show();
            });
    }

    function processEntry(studentId) {
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing Entry...';

        axios.post('/api/entry-exit/', {
            student_id: studentId,
            service_type: 'library'
        }, {
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            timeout: 10000
        })
        .then(function(response) {
            if (response.data.status === 'success') {
                const action = response.data.action;
                const message = response.data.message;

                if (action === 'Entered') {
                    showMessage(`✅ ${message}`, 'success', 2000);
                } else if (action === 'Exited') {
                    showMessage(`🚪 ${message}`, 'info', 2000);
                } else {
                    showMessage(message, 'success', 2000);
                }

                studentIdInput.value = '';
                studentIdInput.focus();
            } else {
                showMessage(response.data.message || 'Unexpected response format', 'error');
                studentIdInput.select();
            }
        })
        .catch(function(error) {
            let errorMessage = 'Error processing entry. Please try again.';

            if (error.response && error.response.data && error.response.data.message) {
                errorMessage = error.response.data.message;
            } else if (error.code === 'ECONNABORTED') {
                errorMessage = 'Request timeout. Please try again.';
            }

            if (error.response && error.response.status === 404 && isValidEightDigitId(studentId)) {
                openRegistrationModal(studentId);
            } else {
                showMessage(errorMessage, 'error');
                studentIdInput.select();
            }
        })
        .finally(function() {
            entryForm.dataset.submitting = '0';
            entryForm.dataset.barcodeConsumedValue = '';
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }
    
    // Handle form submission
    entryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();

        if (entryForm.dataset.submitting === '1') {
            return false;
        }

        const studentId = studentIdInput.value.trim();

        if (!studentId) {
            showMessage('Please enter a valid 8-digit ID.', 'warning');
            studentIdInput.focus();
            return false;
        }

        if (!isValidEightDigitId(studentId)) {
            showMessage('Invalid ID. ID must be exactly 8 digits.', 'warning');
            studentIdInput.focus();
            return false;
        }

        entryForm.dataset.submitting = '1';
        processEntry(studentId);
    });

    if (registrationForm && registrationSubmitBtn) {
        registrationForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const scannedId = registrationStudentId.value.trim();
            const name = registrationName.value.trim();
            const email = registrationEmail.value.trim();
            const departmentId = registrationDepartment.value;

            if (!isValidEightDigitId(scannedId)) {
                showMessage('Invalid ID. Registration is allowed only for valid 8-digit IDs.', 'warning');
                return;
            }

            if (!name || !email || !departmentId) {
                showMessage('Please fill in name, email and department.', 'warning');
                return;
            }

            const originalBtnText = registrationSubmitBtn.innerHTML;
            registrationSubmitBtn.disabled = true;
            registrationSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Registering...';

            axios.post('/api/entry-registration/', {
                student_id: scannedId,
                name: name,
                email: email,
                department_id: departmentId
            }, {
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                timeout: 10000
            })
            .then(function(response) {
                if (response.data.status === 'success') {
                    showMessage(response.data.message || 'Registration completed successfully.', 'success');
                    registrationModal.hide();
                    studentIdInput.value = scannedId;
                    processEntry(scannedId);
                } else {
                    showMessage(response.data.message || 'Registration failed.', 'error');
                }
            })
            .catch(function(error) {
                let errorMessage = 'Registration failed. Please try again.';
                if (error.response && error.response.data && error.response.data.message) {
                    errorMessage = error.response.data.message;
                }
                showMessage(errorMessage, 'error');
            })
            .finally(function() {
                registrationSubmitBtn.disabled = false;
                registrationSubmitBtn.innerHTML = originalBtnText;
            });
        });
    }
}

// ============================================================================
// SERVICE MONITOR FUNCTIONS
// ============================================================================

/**
 * Show seat selection modal
 * @param {string} studentName - Name of the student
 * @param {string} studentId - ID of the student
 */
function showSeatSelectionModal(studentName, studentId) {
    // Set student name in modal
    document.getElementById('modalStudentName').textContent = studentName;
    
    // Load PC layout
    axios.get('/pc-layout/', {
        timeout: 5000
    })
    .then(function(response) {
        document.getElementById('seatLayout').innerHTML = response.data;
        renderSeatLayoutAsLibraryVisual();
        
        // Remove any existing event listeners to prevent duplicates
        const existingHandler = document.querySelector('#seatLayout')?.seatSelectedHandler;
        if (existingHandler) {
            document.removeEventListener('seatSelected', existingHandler);
        }
        
        // Create new event handler for this session
        const seatSelectedHandler = function(event) {
            const seatId = event.detail.seatId;
            const seatNumber = event.detail.seatNumber;
            selectSeat(studentId, seatId, seatNumber);
        };
        
        // Store handler reference for cleanup
        const seatLayoutElement = document.querySelector('#seatLayout');
        if (seatLayoutElement) {
            seatLayoutElement.seatSelectedHandler = seatSelectedHandler;
        }
        
        // Add event listener
        document.addEventListener('seatSelected', seatSelectedHandler);
    })
    .catch(function(error) {
        console.error('Error loading seats:', error);
        document.getElementById('seatLayout').innerHTML = 
            '<div class="alert alert-danger">Error loading seats. Please try again.</div>';
    });
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('seatSelectionModal'));
    modal.show();
    
    // Prevent auto-focus on close button
    const seatSelectionModal = document.getElementById('seatSelectionModal');
    seatSelectionModal.addEventListener('shown.bs.modal', function () {
        // Remove focus from close button
        const closeButton = this.querySelector('.btn-close');
        if (closeButton) {
            closeButton.blur();
        }
        // Don't focus on any specific element, let user click naturally
    });
}

/**
 * Convert plain seat grid to a visual paired-column library layout.
 * Keeps existing seat selection behavior unchanged.
 */
function renderSeatLayoutAsLibraryVisual() {
    const seatLayoutRoot = document.getElementById('seatLayout');
    if (!seatLayoutRoot) return;

    const oldGrid = seatLayoutRoot.querySelector('.seats-grid');
    if (!oldGrid) return;

    const originalSeats = Array.from(oldGrid.querySelectorAll('.seat-cell'));
    if (!originalSeats.length) return;

    const parsePcNumber = (value) => {
        const matched = String(value || '').match(/\d+/);
        return matched ? parseInt(matched[0], 10) : null;
    };

    const seatMap = new Map();
    originalSeats.forEach((seatNode) => {
        const n = parsePcNumber(seatNode.getAttribute('data-seat-number'));
        if (n !== null) {
            seatMap.set(n, {
                seatId: seatNode.getAttribute('data-seat-id'),
                seatNumber: seatNode.getAttribute('data-seat-number'),
                status: String(seatNode.getAttribute('data-status') || '').toLowerCase()
            });
        }
    });

    if (!seatMap.size) return;

    const styleId = 'service-monitor-library-visual-style';
    if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .library-visual-wrap { overflow-x: auto; }
            .library-visual { min-width: 760px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; }
            .pair-block { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; padding: 0.8rem; }
            .pair-title { font-size: 0.8rem; color: #6c757d; text-align: center; margin-top: 1.2rem; line-height: 1.2; font-weight: 700; }
            .pair-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; }
            .pair-col { display: grid; grid-template-rows: repeat(6, 40px); gap: 0.45rem; }
            .seat-node { border-radius: 8px; border: 2px solid transparent; display: flex; align-items: center; justify-content: center; text-decoration: none; }
            .seat-node i { font-size: 0.9rem; }
            .seat-node.available { background: #37c57e; color: #fff; border-color: #2d8f57; cursor: pointer; }
            .seat-node.reserved { background: #2081c4; color: #fff; border-color: #1a6ba3; cursor: not-allowed; }
            .seat-node.maintenance { background: #ffa500; color: #fff; border-color: #e69500; cursor: not-allowed; }
            .seat-node.empty { background: #eef1f4; color: #6c757d; border-color: #d4dbe1; border-style: dashed; }
            .seat-node:hover.available { transform: translateY(-1px); }
            .layout-legend { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem; }
            .layout-legend span { font-size: 0.85rem; }
            .layout-dot { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 0.35rem; vertical-align: -1px; }
        `;
        document.head.appendChild(style);
    }

    const wrap = document.createElement('div');
    wrap.className = 'library-visual-wrap';

    const visual = document.createElement('div');
    visual.className = 'library-visual';

    const existingNumbers = Array.from(seatMap.keys());
    const maxPcNumber = existingNumbers.length ? Math.max(...existingNumbers) : 48;
    const pairCount = Math.max(4, Math.ceil(maxPcNumber / 12));

    for (let pair = 1; pair <= pairCount; pair++) {
        const leftStart = (pair - 1) * 12 + 1;
        const rightStart = leftStart + 6;

        const pairBlock = document.createElement('div');
        pairBlock.className = 'pair-block';

        const cols = document.createElement('div');
        cols.className = 'pair-columns';

        const leftCol = document.createElement('div');
        leftCol.className = 'pair-col';
        for (let n = leftStart + 5; n >= leftStart; n--) {
            leftCol.appendChild(buildNode(n));
        }

        const rightCol = document.createElement('div');
        rightCol.className = 'pair-col';
        for (let n = rightStart; n <= rightStart + 5; n++) {
            rightCol.appendChild(buildNode(n));
        }

        cols.appendChild(leftCol);
        cols.appendChild(rightCol);
        pairBlock.appendChild(cols);

        const title = document.createElement('div');
        title.className = 'pair-title';
        title.textContent = `Pair ${pair}`;
        pairBlock.appendChild(title);

        visual.appendChild(pairBlock);
    }

    wrap.appendChild(visual);

    const legend = document.createElement('div');
    legend.className = 'layout-legend';
    legend.innerHTML = `
        <span><i class="layout-dot" style="background:#37c57e;"></i>Available</span>
        <span><i class="layout-dot" style="background:#2081c4;"></i>Reserved</span>
        <span><i class="layout-dot" style="background:#ffa500;"></i>Maintenance</span>
    `;
    wrap.appendChild(legend);

    oldGrid.replaceWith(wrap);

    function buildNode(n) {
        const seat = seatMap.get(n);
        const node = document.createElement('div');
        node.className = 'seat-node seat-cell';

        if (!seat) {
            node.classList.add('empty');
            return node;
        }

        node.classList.add(seat.status);
        node.setAttribute('data-seat-id', seat.seatId);
        node.setAttribute('data-seat-number', seat.seatNumber);
        node.setAttribute('data-status', seat.status);
        node.textContent = seat.seatNumber;

        if (seat.status === 'available') {
            node.setAttribute('onclick', 'selectSeatElement(this)');
        }

        return node;
    }

}

/**
 * Handle seat selection
 * @param {string} studentId - ID of the student
 * @param {string} seatId - ID of the selected seat
 * @param {string} seatNumber - Number of the selected seat
 */
function selectSeat(studentId, seatId, seatNumber) {
    const selectedSeat = document.querySelector(`[data-seat-id="${seatId}"]`);
    if (selectedSeat) {
        selectedSeat.style.pointerEvents = 'none';
        selectedSeat.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    axios.post('/api/seat-selection/', {
        student_id: studentId,
        seat_id: seatId
    }, {
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        timeout: 5000
    })
    .then(function(response) {
        if (response.data.status === 'success') {
            // Hide modal automatically after seat selection
            const modal = bootstrap.Modal.getInstance(document.getElementById('seatSelectionModal'));
            if (modal) {
                modal.hide();
            }
            
            // Show success toast
            showToast(`✅ ${response.data.message}`, 'success');
            
            // Clear the form and refocus input for next scan (after modal is closed)
            setTimeout(() => {
                const studentIdInput = document.getElementById('studentId') || document.getElementById('student_id');
                if (studentIdInput) {
                    studentIdInput.value = '';
                    studentIdInput.focus();
                }
            }, 300);
            
        } else {
            showToast(response.data.message, 'error');
            // Reset seat if error
            if (selectedSeat) {
                selectedSeat.style.pointerEvents = 'auto';
                selectedSeat.innerHTML = seatNumber;
            }
        }
    })
    .catch(function(error) {
        console.error('Seat selection error:', error);
        let errorMessage = 'Error selecting seat. Please try again.';
        
        if (error.response && error.response.data && error.response.data.message) {
            errorMessage = error.response.data.message;
        } else if (error.code === 'ECONNABORTED') {
            errorMessage = 'Request timeout. Please try again.';
        }
        
        showToast(errorMessage, 'error');
        
        // Reset seat
        if (selectedSeat) {
            selectedSeat.style.pointerEvents = 'auto';
            selectedSeat.innerHTML = seatNumber;
        }
    });
}

/**
 * Initialize Service Monitor
 */
function initializeServiceMonitor() {
    optimizeForBarcode('studentId', 'serviceForm', { autoSubmitLength: 8 });
    maintainInputFocus('studentId');
    const serviceForm = document.getElementById('serviceForm');
    
    // Initialize ticket submission functionality
    initializeTicketSubmission();
    
    // Handle form submission
    serviceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();

        if (serviceForm.dataset.submitting === '1') {
            return false;
        }
        
        console.log('Service form submission intercepted');
        
        const submitBtn = document.getElementById('submitBtn');
        const btnText = document.getElementById('btnText');
        const studentIdInput = document.getElementById('studentId');
        const studentId = studentIdInput.value.trim();
        
        if (!studentId) {
            showMessage('Please enter or scan a valid Student/Faculty ID', 'warning');
            studentIdInput.focus();
            return false;
        }
        
        if (studentId.length < 6) {
            showMessage('ID must be at least 6 characters long', 'warning');
            studentIdInput.focus();
            return false;
        }

        // Store student ID in localStorage for ticket submission
        localStorage.setItem('currentStudentId', studentId);
        serviceForm.dataset.submitting = '1';
        
        // Show loading state
        submitBtn.disabled = true;
        btnText.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        console.log('Sending service request with student ID:', studentId);
        
        // Submit using axios with timeout
        axios.post('/api/service-monitor/', {
            student_id: studentId,
            service_type: 'elibrary'
        }, {
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            timeout: 10000 // 10 second timeout
        })
        .then(function(response) {
            console.log('Service response received:', response.data);
            
            if (response.data.status === 'success') {
                const action = response.data.action;
                const message = response.data.message;
                
                if (response.data.requires_seat_selection) {
                    // Show seat selection modal
                    showSeatSelectionModal(response.data.student_name, response.data.student_id);
                    
                    // Listen for seat selection to clear localStorage
                    document.addEventListener('seatSelected', function(event) {
                        // Clear student ID from localStorage when seat is selected
                        localStorage.removeItem('currentStudentId');
                    }, { once: true });
                    
                } else {
                    // Show success message for exit
                    showMessage(message, 'info');
                    // Clear localStorage on exit
                    localStorage.removeItem('currentStudentId');
                }
                
                // Clear form
                studentIdInput.value = '';
                setTimeout(() => studentIdInput.focus(), 100);
            } else {
                // Handle error responses with proper status
                const errorMessage = response.data.message || 'Unexpected error occurred';
                showMessage(errorMessage, 'error');
                studentIdInput.select();
            }
        })
        .catch(function(error) {
            console.error('Service error:', error);
            let errorMessage = 'Error processing service. Please try again.';
            
            if (error.response && error.response.data && error.response.data.message) {
                errorMessage = error.response.data.message;
                
                // Check if it's a library entry requirement error
                if (error.response.data.requires_library_entry) {
                    showMessage(`🚫 ${errorMessage}`, 'warning');
                } else {
                    showMessage(errorMessage, 'error');
                }
            } else if (error.code === 'ECONNABORTED') {
                errorMessage = 'Request timeout. Please check your connection and try again.';
                showMessage(errorMessage, 'error');
            } else if (error.message) {
                errorMessage = error.message;
                showMessage(errorMessage, 'error');
            } else {
                showMessage(errorMessage, 'error');
            }
            
            studentIdInput.select();
        })
        .finally(function() {
            serviceForm.dataset.submitting = '0';
            serviceForm.dataset.barcodeConsumedValue = '';
            // Reset button state
            submitBtn.disabled = false;
            btnText.innerHTML = 'Access Services / Exit';
        });
    });
}

// ============================================================================
// TICKET SUBMISSION FUNCTIONS
// ============================================================================

/**
 * Open the Report Issue modal programmatically
 * Handles modal transitions from seat selection modal if needed
 */
function openReportIssueModal() {
    const submitTicketModal = document.getElementById('submitTicketModal');
    const seatSelectionModal = document.getElementById('seatSelectionModal');
    const ticketStudentIdInput = document.getElementById('ticketStudentId');

    // Pre-fill student ID from localStorage if available
    const storedId = localStorage.getItem('currentStudentId');
    if (storedId && ticketStudentIdInput) {
        ticketStudentIdInput.value = storedId;
    }

    // Check if seat selection modal is currently open
    const seatModalInstance = seatSelectionModal ? bootstrap.Modal.getInstance(seatSelectionModal) : null;

    if (seatModalInstance) {
        // Hide seat selection modal first, then open ticket modal
        seatSelectionModal.addEventListener('hidden.bs.modal', function openTicket() {
            seatSelectionModal.removeEventListener('hidden.bs.modal', openTicket);
            const ticketModal = new bootstrap.Modal(submitTicketModal);
            ticketModal.show();
        }, { once: true });
        seatModalInstance.hide();
    } else {
        // Directly open ticket modal
        const ticketModal = new bootstrap.Modal(submitTicketModal);
        ticketModal.show();
    }
}

/**
 * Initialize ticket submission functionality
 */
function initializeTicketSubmission() {
    const submitTicketBtn = document.getElementById('submitTicketBtn');
    const submitTicketFormBtn = document.getElementById('submitTicketFormBtn');
    const ticketForm = document.getElementById('ticketSubmissionForm');
    
    if (!submitTicketFormBtn || !ticketForm) {
        console.log('Ticket submission elements not found');
        return;
    }

    // Main page "Report Issue" button — open modal programmatically
    if (submitTicketBtn) {
        submitTicketBtn.addEventListener('click', function () {
            openReportIssueModal();
        });
    }

    // "Report Issue" button inside seat selection modal
    const seatModalReportBtn = document.getElementById('seatModalReportIssueBtn');
    if (seatModalReportBtn) {
        seatModalReportBtn.addEventListener('click', function () {
            openReportIssueModal();
        });
    }

    // Focus on student ID input when ticket modal is shown
    const submitTicketModal = document.getElementById('submitTicketModal');
    if (submitTicketModal) {
        submitTicketModal.addEventListener('shown.bs.modal', function () {
            const idInput = document.getElementById('ticketStudentId');
            if (idInput && !idInput.value) {
                idInput.focus();
            } else {
                const titleInput = document.getElementById('ticketTitle');
                if (titleInput && !titleInput.value) titleInput.focus();
            }
        });
    }
    
    // Handle ticket form submission
    submitTicketFormBtn.addEventListener('click', function(e) {
        e.preventDefault();

        // Get student ID from the modal input field (or fallback to localStorage)
        const ticketStudentIdInput = document.getElementById('ticketStudentId');
        const studentId = (ticketStudentIdInput ? ticketStudentIdInput.value.trim() : '') || localStorage.getItem('currentStudentId');

        if (!studentId) {
            showMessage('Please enter your Student/Faculty ID.', 'error');
            if (ticketStudentIdInput) ticketStudentIdInput.focus();
            return;
        }
        
        const title = document.getElementById('ticketTitle').value.trim();
        const issueType = document.getElementById('ticketIssueType').value;
        const description = document.getElementById('ticketDescription').value.trim();
        
        // Validate form
        if (!title) {
            showMessage('Please enter a title for the issue.', 'warning');
            document.getElementById('ticketTitle').focus();
            return;
        }
        
        if (!issueType) {
            showMessage('Please select an issue type.', 'warning');
            document.getElementById('ticketIssueType').focus();
            return;
        }
        
        if (!description) {
            showMessage('Please enter a description of the issue.', 'warning');
            document.getElementById('ticketDescription').focus();
            return;
        }
        
        // Show loading state
        submitTicketFormBtn.disabled = true;
        submitTicketFormBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
        
        // Submit ticket
        axios.post('/api/submit-ticket/', {
            student_id: studentId,
            title: title,
            issue_type: issueType,
            description: description
        }, {
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            timeout: 10000
        })
        .then(function(response) {
            if (response.data.status === 'success') {
                showMessage(response.data.message, 'success');
                
                // Reset form
                ticketForm.reset();
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(submitTicketModal);
                if (modal) modal.hide();
            } else {
                showMessage(response.data.message || 'Failed to submit ticket', 'error');
            }
        })
        .catch(function(error) {
            console.error('Ticket submission error:', error);
            let errorMessage = 'Error submitting ticket. Please try again.';
            
            if (error.response && error.response.data && error.response.data.message) {
                errorMessage = error.response.data.message;
            }
            
            showMessage(errorMessage, 'error');
        })
        .finally(function() {
            // Reset button state
            submitTicketFormBtn.disabled = false;
            submitTicketFormBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Submit Ticket';
        });
    });
}

// ============================================================================
// SEAT SELECTION FUNCTIONS
// ============================================================================

// Global variables to track selected seat
let selectedSeatId = null;
let selectedSeatNumber = null;

/**
 * Select a seat in the seat selection grid
 * This function is called from the HTML onclick event
 * @param {HTMLElement} seatElement - The clicked seat element
 */
function selectSeatElement(seatElement) {
    // Validate that seatElement is a DOM element
    if (!seatElement || typeof seatElement.getAttribute !== 'function') {
        console.error('Invalid seat element passed to selectSeatElement');
        return;
    }

    const seatId = seatElement.getAttribute('data-seat-id');
    const seatNumber = seatElement.getAttribute('data-seat-number');
    const status = seatElement.getAttribute('data-status');
    
    // Only allow selection of available seats
    if (status !== 'available') {
        return;
    }

    // Remove previous selection (ensure only one seat can be selected)
    document.querySelectorAll('.seat-cell').forEach(cell => {
        cell.classList.remove('selected');
        cell.style.border = '2px solid transparent';
        cell.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.15)';
    });

    // Add selection to clicked seat
    seatElement.classList.add('selected');
    seatElement.style.border = '3px solid #fff';
    seatElement.style.boxShadow = '0 0 0 2px #2081C4, 0 4px 12px rgba(32, 129, 196, 0.4)';
    
    // Store selected seat info
    selectedSeatId = seatId;
    selectedSeatNumber = seatNumber;
    
    // Trigger custom event for the service monitor to handle
    const selectEvent = new CustomEvent('seatSelected', {
        detail: {
            seatId: seatId,
            seatNumber: seatNumber
        }
    });
    document.dispatchEvent(selectEvent);
}

/**
 * Get selected seat information
 * @returns {Object} Selected seat data
 */
function getSelectedSeat() {
    return {
        seatId: selectedSeatId,
        seatNumber: selectedSeatNumber
    };
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the library system based on current page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Determine which system to initialize based on page elements
    if (document.getElementById('entryForm')) {
        // Entry Monitor page
        console.log('Initializing Entry Monitor');
        initializeEntryMonitor();
    } else if (document.getElementById('serviceForm')) {
        // Service Monitor page
        console.log('Initializing Service Monitor');
        initializeServiceMonitor();
    }
    
    // Make seat selection functions globally available
    window.selectSeatElement = selectSeatElement;
    window.getSelectedSeat = getSelectedSeat;
});