/**
 * IUBAT Library Management System - Custom JavaScript
 * Contains all JavaScript functions for Entry Monitor, Service Monitor, and Seat Selection
 */

// ============================================================================
// GLOBAL UTILITY FUNCTIONS
// ============================================================================

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
        case 'success': return 2000;  // 2 seconds
        case 'info': return 1500;     // 1.5 seconds
        case 'warning': return 2500;  // 2.5 seconds
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
 * Optimize input field for barcode scanner
 * @param {string} inputId - ID of the input element
 * @param {string} formId - ID of the form element
 */
function optimizeForBarcode(inputId = 'studentId', formId = 'entryForm') {
    const input = document.getElementById(inputId);
    const form = document.getElementById(formId);
    
    if (!input || !form) return;
    
    // Force focus and prevent losing focus
    input.focus();
    
    // Re-focus when clicking anywhere
    document.addEventListener('click', function() {
        setTimeout(() => input.focus(), 100);
    });
    
    // Re-focus on page visibility change
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            setTimeout(() => input.focus(), 100);
        }
    });
    
    // Handle rapid input (typical of barcode scanners)
    let inputBuffer = '';
    let inputTimeout;
    
    input.addEventListener('input', function(e) {
        clearTimeout(inputTimeout);
        inputBuffer += e.data || '';
        
        // If input seems to be from a barcode scanner (rapid input)
        if (e.inputType === 'insertText' && inputBuffer.length > 5) {
            inputTimeout = setTimeout(() => {
                // Auto-submit if input looks like a complete barcode
                if (this.value.length >= 6) {
                    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
                inputBuffer = '';
            }, 50);
        } else {
            // Regular typing
            inputTimeout = setTimeout(() => {
                inputBuffer = '';
            }, 500);
        }
    });
    
    // Handle barcode scanner that sends Enter key
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.length >= 6) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        }
    });
}

/**
 * Maintain input focus
 * @param {string} inputId - ID of the input element
 */
function maintainInputFocus(inputId = 'studentId') {
    // Ensure input stays focused
    setInterval(() => {
        const input = document.getElementById(inputId);
        if (input && document.activeElement !== input && document.hasFocus()) {
            input.focus();
        }
    }, 1000);
    
    // Handle page focus
    window.addEventListener('focus', function() {
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
    optimizeForBarcode('studentId', 'entryForm');
    maintainInputFocus('studentId');
    
    // Handle form submission
    document.getElementById('entryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Entry form submission intercepted');
        
        const submitBtn = document.querySelector('button[type="submit"]');
        const studentIdInput = document.getElementById('studentId');
        const studentId = studentIdInput.value.trim();
        
        if (!studentId) {
            showMessage('Please enter a valid Student/Faculty ID', 'warning');
            studentIdInput.focus();
            return false;
        }
        
        if (studentId.length < 6) {
            showMessage('ID must be at least 6 characters long', 'warning');
            studentIdInput.focus();
            return false;
        }
        
        // Show loading state
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing Entry...';
        
        // Prepare request data
        const requestData = {
            student_id: studentId,
            service_type: 'library'
        };
        
        console.log('Sending entry request with student ID:', studentId);
        
        // Submit using axios
        axios.post('/api/entry-exit/', requestData, {
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            timeout: 10000
        })
        .then(function(response) {
            console.log('Entry response received:', response.data);
            
            if (response.data.status === 'success') {
                const action = response.data.action;
                const message = response.data.message;
                
                // Show appropriate success message
                if (action === 'Entered') {
                    showMessage(`✅ ${message}`, 'success');
                } else if (action === 'Exited') {
                    showMessage(`🚪 ${message}`, 'info');
                } else {
                    showMessage(message, 'success');
                }
            } else {
                showMessage(response.data.message || 'Unexpected response format', 'error');
            }
            
            // Clear form and reset
            studentIdInput.value = '';
            studentIdInput.focus();
        })
        .catch(function(error) {
            console.error('Entry error:', error);
            let errorMessage = 'Error processing entry. Please try again.';
            
            if (error.response && error.response.data && error.response.data.message) {
                errorMessage = error.response.data.message;
            } else if (error.code === 'ECONNABORTED') {
                errorMessage = 'Request timeout. Please try again.';
            }
            
            showMessage(errorMessage, 'error');
            studentIdInput.select();
        })
        .finally(function() {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    });
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
    optimizeForBarcode('studentId', 'serviceForm');
    maintainInputFocus('studentId');
    
    // Handle form submission
    document.getElementById('serviceForm').addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
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
                } else {
                    // Show success message for exit
                    showMessage(message, 'info');
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
            // Reset button state
            submitBtn.disabled = false;
            btnText.innerHTML = 'Access Services / Exit';
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