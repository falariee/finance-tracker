// Global state
let currentTrip = null;
let currentCurrency = 'USD';
let exchangeRates = {};
let savedConversion = null;

// Currency list
const currencies = [
    { code: 'USD', name: 'US Dollar', flag: '🇺🇸' },
    { code: 'EUR', name: 'Euro', flag: '🇪🇺' },
    { code: 'GBP', name: 'British Pound', flag: '🇬🇧' },
    { code: 'JPY', name: 'Japanese Yen', flag: '🇯🇵' },
    { code: 'AUD', name: 'Australian Dollar', flag: '🇦🇺' },
    { code: 'CAD', name: 'Canadian Dollar', flag: '🇨🇦' },
    { code: 'CHF', name: 'Swiss Franc', flag: '🇨🇭' },
    { code: 'CNY', name: 'Chinese Yuan', flag: '🇨🇳' },
    { code: 'INR', name: 'Indian Rupee', flag: '🇮🇳' },
    { code: 'KRW', name: 'South Korean Won', flag: '🇰🇷' },
    { code: 'SGD', name: 'Singapore Dollar', flag: '🇸🇬' },
    { code: 'HKD', name: 'Hong Kong Dollar', flag: '🇭🇰' },
    { code: 'MXN', name: 'Mexican Peso', flag: '🇲🇽' },
    { code: 'BRL', name: 'Brazilian Real', flag: '🇧🇷' },
    { code: 'ZAR', name: 'South African Rand', flag: '🇿🇦' },
    { code: 'THB', name: 'Thai Baht', flag: '🇹🇭' },
    { code: 'MYR', name: 'Malaysian Ringgit', flag: '🇲🇾' },
    { code: 'IDR', name: 'Indonesian Rupiah', flag: '🇮🇩' },
    { code: 'PHP', name: 'Philippine Peso', flag: '🇵🇭' },
    { code: 'VND', name: 'Vietnamese Dong', flag: '🇻🇳' },
    { code: 'NZD', name: 'New Zealand Dollar', flag: '🇳🇿' },
    { code: 'SEK', name: 'Swedish Krona', flag: '🇸🇪' },
    { code: 'NOK', name: 'Norwegian Krone', flag: '🇳🇴' },
    { code: 'DKK', name: 'Danish Krone', flag: '🇩🇰' },
    { code: 'PLN', name: 'Polish Zloty', flag: '🇵🇱' },
    { code: 'CZK', name: 'Czech Koruna', flag: '🇨🇿' },
    { code: 'HUF', name: 'Hungarian Forint', flag: '🇭🇺' },
    { code: 'TRY', name: 'Turkish Lira', flag: '🇹🇷' },
    { code: 'AED', name: 'UAE Dirham', flag: '🇦🇪' },
    { code: 'SAR', name: 'Saudi Riyal', flag: '🇸🇦' }
];

// DOM Elements
const tripSetup = document.getElementById('tripSetup');
const tripDashboard = document.getElementById('tripDashboard');
const tripForm = document.getElementById('tripForm');
const expenseForm = document.getElementById('expenseForm');
const travelerForm = document.getElementById('travelerForm');
const loadModal = document.getElementById('loadModal');
const converterModal = document.getElementById('converterModal');
const inviteModal = document.getElementById('inviteModal');
const exportModal = document.getElementById('exportModal');
const saveBtn = document.getElementById('saveBtn');
const loadBtn = document.getElementById('loadBtn');
const currencyConverterBtn = document.getElementById('currencyConverterBtn');
const inviteLinkBtn = document.getElementById('inviteLinkBtn');
const exportSummaryBtn = document.getElementById('exportSummaryBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupTabs();
    fetchExchangeRates();
    populateCurrencyDropdowns();
    loadSavedConversion();
    checkDatabaseStatus();
    checkForTripInURL();
});

// Event Listeners
function setupEventListeners() {
    tripForm.addEventListener('submit', handleTripCreate);
    expenseForm.addEventListener('submit', handleExpenseAdd);
    travelerForm.addEventListener('submit', handleTravelerAdd);
    saveBtn.addEventListener('click', handleTripSave);
    loadBtn.addEventListener('click', handleLoadModalOpen);
    currencyConverterBtn.addEventListener('click', handleConverterModalOpen);
    inviteLinkBtn.addEventListener('click', handleInviteModalOpen);
    exportSummaryBtn.addEventListener('click', handleExportModalOpen);
    
    // Modal close buttons
    const closeBtn = document.querySelector('.close');
    closeBtn.addEventListener('click', () => loadModal.style.display = 'none');
    
    const closeConverterBtn = document.querySelector('.close-converter');
    closeConverterBtn.addEventListener('click', () => converterModal.style.display = 'none');
    
    const closeInviteBtn = document.querySelector('.close-invite');
    closeInviteBtn.addEventListener('click', () => inviteModal.style.display = 'none');
    
    const closeExportBtn = document.querySelector('.close-export');
    closeExportBtn.addEventListener('click', () => exportModal.style.display = 'none');
    
    // Close modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target === loadModal) loadModal.style.display = 'none';
        if (e.target === converterModal) converterModal.style.display = 'none';
        if (e.target === inviteModal) inviteModal.style.display = 'none';
        if (e.target === exportModal) exportModal.style.display = 'none';
    });
}

// Toggle other category input
function toggleOtherInput(select) {
    const otherGroup = document.getElementById('otherCategoryGroup');
    const otherInput = document.getElementById('otherCategory');
    
    if (select.value === 'other') {
        otherGroup.style.display = 'block';
        otherInput.required = true;
    } else {
        otherGroup.style.display = 'none';
        otherInput.required = false;
        otherInput.value = '';
    }
}

// Tab System
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Remove active class from all tabs and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            
            // Add active class to clicked tab and corresponding pane
            btn.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            // Load data for reports tab
            if (tabName === 'reports') {
                loadReports();
            } else if (tabName === 'split') {
                loadSplitReport();
            }
        });
    });
}

// Trip Creation
async function handleTripCreate(e) {
    e.preventDefault();
    
    const tripData = {
        name: document.getElementById('tripName').value,
        destination: document.getElementById('destination').value,
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        currency: document.getElementById('currency').value
    };
    
    try {
        const response = await fetch('/api/trip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tripData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentTrip = data.trip;
            currentCurrency = data.trip.currency;
            showDashboard();
            showNotification('Trip created successfully!', 'success');
        } else {
            showNotification('Error creating trip: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error creating trip: ' + error.message, 'error');
    }
}

// Show Dashboard
function showDashboard() {
    tripSetup.style.display = 'none';
    tripDashboard.style.display = 'block';
    saveBtn.style.display = 'inline-flex';
    
    // Update trip info
    document.getElementById('tripNameDisplay').textContent = currentTrip.name;
    document.getElementById('tripDestinationDisplay').textContent = currentTrip.destination;
    document.getElementById('tripDatesDisplay').textContent = 
        `${currentTrip.start_date} to ${currentTrip.end_date}`;
    
    // Populate expense currency dropdown with trip currency as default
    populateExpenseCurrency();
    
    updateSummary();
    loadTravelers();
    loadExpenses();
}

// Populate currency dropdowns
function populateCurrencyDropdowns() {
    const fromCurrency = document.getElementById('fromCurrency');
    const toCurrency = document.getElementById('toCurrency');
    
    currencies.forEach(curr => {
        const option1 = document.createElement('option');
        option1.value = curr.code;
        option1.textContent = `${curr.flag} ${curr.code}`;
        fromCurrency.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = curr.code;
        option2.textContent = `${curr.flag} ${curr.code}`;
        toCurrency.appendChild(option2);
    });
    
    // Set defaults
    fromCurrency.value = 'USD';
    toCurrency.value = 'EUR';
}

// Populate expense currency dropdown
function populateExpenseCurrency() {
    const expenseCurrency = document.getElementById('expenseCurrency');
    expenseCurrency.innerHTML = '';
    
    // Add default currency at the top
    if (currentTrip && currentTrip.currency) {
        const defaultCurr = currencies.find(c => c.code === currentTrip.currency);
        if (defaultCurr) {
            const defaultOption = document.createElement('option');
            defaultOption.value = defaultCurr.code;
            defaultOption.textContent = `${defaultCurr.flag} ${defaultCurr.code} (Default)`;
            defaultOption.selected = true;
            expenseCurrency.appendChild(defaultOption);
            
            // Add separator
            const separator = document.createElement('option');
            separator.disabled = true;
            separator.textContent = '─────────────';
            expenseCurrency.appendChild(separator);
        }
    }
    
    // Add all currencies
    currencies.forEach(curr => {
        // Skip if it's the default currency (already added)
        if (currentTrip && curr.code === currentTrip.currency) {
            return;
        }
        
        const option = document.createElement('option');
        option.value = curr.code;
        option.textContent = `${curr.flag} ${curr.code}`;
        expenseCurrency.appendChild(option);
    });
}

// Fetch exchange rates
async function fetchExchangeRates() {
    try {
        const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
        const data = await response.json();
        exchangeRates = data.rates;
        console.log('Exchange rates loaded successfully');
        updateConversionDisplay();
    } catch (error) {
        console.error('Error fetching exchange rates:', error);
        showNotification('Could not fetch exchange rates', 'warning');
    }
}

// Add Traveler
async function handleTravelerAdd(e) {
    e.preventDefault();
    
    const travelerData = {
        name: document.getElementById('travelerName').value,
        email: document.getElementById('travelerEmail').value
    };
    
    try {
        const response = await fetch('/api/travelers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(travelerData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            travelerForm.reset();
            loadTravelers();
            updatePaidByDropdown();
            showNotification('Traveler added!', 'success');
        } else {
            showNotification('Error adding traveler: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error adding traveler: ' + error.message, 'error');
    }
}

// Load Travelers
async function loadTravelers() {
    try {
        const response = await fetch('/api/travelers');
        const data = await response.json();
        
        if (data.success) {
            const travelersList = document.getElementById('travelersList');
            
            if (data.travelers.length === 0) {
                travelersList.innerHTML = '<p class="empty-state">No travelers yet. Add travelers above!</p>';
            } else {
                travelersList.innerHTML = data.travelers.map(traveler => `
                    <div class="traveler-item">
                        <div class="traveler-info">
                            <div class="traveler-name"><i class="fas fa-user"></i> ${traveler.name}</div>
                            <div class="traveler-email">${traveler.email || 'No email provided'}</div>
                        </div>
                    </div>
                `).join('');
            }
            
            updatePaidByDropdown();
            updateSummary();
        }
    } catch (error) {
        console.error('Error loading travelers:', error);
    }
}

// Update Paid By Dropdown
async function updatePaidByDropdown() {
    try {
        const response = await fetch('/api/travelers');
        const data = await response.json();
        
        if (data.success) {
            const paidBySelect = document.getElementById('paidBy');
            paidBySelect.innerHTML = '<option value="">Select traveler...</option>';
            
            data.travelers.forEach(traveler => {
                const option = document.createElement('option');
                option.value = traveler.name;
                option.textContent = traveler.name;
                paidBySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error updating paid by dropdown:', error);
    }
}

// Add Expense
async function handleExpenseAdd(e) {
    e.preventDefault();
    
    let category = document.getElementById('expenseCategory').value;
    
    // If "other" is selected, use the custom category
    if (category === 'other') {
        const customCategory = document.getElementById('otherCategory').value.trim();
        if (!customCategory) {
            showNotification('Please specify the category', 'error');
            return;
        }
        category = customCategory.toLowerCase();
    }
    
    const expenseData = {
        description: document.getElementById('expenseDesc').value,
        amount: parseFloat(document.getElementById('expenseAmount').value),
        currency: document.getElementById('expenseCurrency').value,
        category: category,
        paid_by: document.getElementById('paidBy').value
    };
    
    try {
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expenseData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            expenseForm.reset();
            loadExpenses();
            updateSummary();
            showNotification('Expense added!', 'success');
        } else {
            showNotification('Error adding expense: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error adding expense: ' + error.message, 'error');
    }
}

// Load Expenses
async function loadExpenses() {
    try {
        const response = await fetch('/api/expenses');
        const data = await response.json();
        
        if (data.success) {
            const expensesList = document.getElementById('expensesList');
            
            if (data.expenses.length === 0) {
                expensesList.innerHTML = '<p class="empty-state">No expenses yet. Add your first expense above!</p>';
            } else {
                expensesList.innerHTML = data.expenses.map(expense => {
                const categoryEmoji = {
                    food: '🍽️',
                    groceries: '🛒',
                    snacks: '🍿',
                    transport: '🚗',
                    accommodation: '🏨',
                    activities: '🎭',
                    shopping: '🛍️',
                    other: '📦'
                };
                
                // Get emoji or default for custom categories
                const emoji = categoryEmoji[expense.category] || '📦';                    // Convert to trip currency if different
                    let displayAmount = expense.amount;
                    let conversionNote = '';
                    if (expense.currency !== currentCurrency && exchangeRates[expense.currency] && exchangeRates[currentCurrency]) {
                        const convertedAmount = (expense.amount / exchangeRates[expense.currency]) * exchangeRates[currentCurrency];
                        conversionNote = ` (≈ ${convertedAmount.toFixed(2)} ${currentCurrency})`;
                    }
                    
                    return `
                        <div class="expense-item">
                            <div class="expense-info">
                                <div class="expense-title">
                                    ${emoji} ${expense.description}
                                </div>
                                <div class="expense-meta">
                                    <span class="category-badge category-${expense.category}">
                                        ${expense.category}
                                    </span>
                                    Paid by ${expense.paid_by} • ${new Date(expense.date).toLocaleDateString()}
                                </div>
                            </div>
                            <div class="expense-amount">
                                ${expense.amount.toFixed(2)} ${expense.currency}${conversionNote}
                            </div>
                            <div class="expense-actions">
                                <button class="icon-btn" onclick="deleteExpense('${expense.id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        }
    } catch (error) {
        console.error('Error loading expenses:', error);
    }
}

// Delete Expense
async function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/expenses/${expenseId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadExpenses();
            updateSummary();
            showNotification('Expense deleted!', 'success');
        } else {
            showNotification('Error deleting expense: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error deleting expense: ' + error.message, 'error');
    }
}

// Update Summary
async function updateSummary() {
    try {
        const response = await fetch('/api/reports/summary');
        const data = await response.json();
        
        if (data.success) {
            const summary = data.summary;
            
            // Show currency breakdown first (original currencies)
            let totalText = '';
            if (summary.currency_breakdown && Object.keys(summary.currency_breakdown).length > 0) {
                const breakdown = Object.entries(summary.currency_breakdown)
                    .map(([curr, amt]) => `${amt.toFixed(2)} ${curr}`)
                    .join(' + ');
                totalText = breakdown;
            }
            
            // Add converted total in default currency below
            totalText += `<br><small style="font-size: 0.8rem; opacity: 0.9; font-weight: 600;">= ${summary.total_expenses.toFixed(2)} ${summary.currency}</small>`;
            
            // Auto-convert to saved conversion currency
            if (savedConversion && savedConversion.to && exchangeRates[summary.currency] && exchangeRates[savedConversion.to]) {
                const convertedTotal = summary.total_expenses * (exchangeRates[savedConversion.to] / exchangeRates[summary.currency]);
                const toFlag = currencies.find(c => c.code === savedConversion.to)?.flag || '';
                totalText += `<br><small style="font-size: 0.85rem; opacity: 0.95; font-weight: 700; color: #fbbf24;">≈ ${toFlag} ${convertedTotal.toFixed(2)} ${savedConversion.to}</small>`;
            }
            
            document.getElementById('totalExpenses').innerHTML = totalText;
            document.getElementById('expenseCount').textContent = summary.num_expenses;
        }
        
        // Update traveler count
        const travelersResponse = await fetch('/api/travelers');
        const travelersData = await travelersResponse.json();
        if (travelersData.success) {
            document.getElementById('travelerCount').textContent = travelersData.travelers.length;
        }
    } catch (error) {
        console.error('Error updating summary:', error);
    }
}

// Load Reports
async function loadReports() {
    await loadCategoryReport();
    await loadPeopleReport();
}

// Category Report
async function loadCategoryReport() {
    try {
        const response = await fetch('/api/reports/categories');
        const data = await response.json();
        
        if (data.success) {
            const categoryReport = document.getElementById('categoryReport');
            
            if (data.categories.length === 0) {
                categoryReport.innerHTML = '<p class="empty-state">No expenses to report</p>';
            } else {
                categoryReport.innerHTML = data.categories.map(cat => {
                    // Build currency breakdown display
                    let currencyBreakdown = '';
                    if (cat.currency_breakdown && Object.keys(cat.currency_breakdown).length > 0) {
                        const breakdown = Object.entries(cat.currency_breakdown)
                            .map(([curr, amt]) => `${amt.toFixed(2)} ${curr}`)
                            .join(' + ');
                        currencyBreakdown = `<div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.25rem;">${breakdown}</div>`;
                    }
                    
                    return `
                        <div class="report-item">
                            <div style="flex: 1;">
                                <div class="report-label">${cat.category.charAt(0).toUpperCase() + cat.category.slice(1)}</div>
                                ${currencyBreakdown}
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${cat.percentage}%"></div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span class="report-value">${cat.amount.toFixed(2)} ${currentTrip.currency}</span>
                                <span class="report-percentage">${cat.percentage}%</span>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        }
    } catch (error) {
        console.error('Error loading category report:', error);
    }
}

// People Report
async function loadPeopleReport() {
    try {
        const response = await fetch('/api/reports/people');
        const data = await response.json();
        
        if (data.success) {
            const peopleReport = document.getElementById('peopleReport');
            
            if (data.people.length === 0) {
                peopleReport.innerHTML = '<p class="empty-state">No expenses to report</p>';
            } else {
                peopleReport.innerHTML = data.people.map(person => `
                    <div class="report-item">
                        <div>
                            <div class="report-label">${person.person}</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${person.percentage}%"></div>
                            </div>
                        </div>
                        <div>
                            <span class="report-value">${person.amount.toFixed(2)} ${currentTrip.currency}</span>
                            <span class="report-percentage">${person.num_expenses} expenses</span>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading people report:', error);
    }
}

// Split Report
async function loadSplitReport() {
    try {
        const response = await fetch('/api/reports/split');
        const data = await response.json();
        
        const splitReport = document.getElementById('splitReport');
        
        if (!data.success) {
            splitReport.innerHTML = `<p class="empty-state">${data.error}</p>`;
            return;
        }
        
        if (data.balances.length === 0) {
            splitReport.innerHTML = '<p class="empty-state">No travelers to split expenses</p>';
        } else {
            splitReport.innerHTML = data.balances.map(balance => {
                const statusClass = balance.status === 'owed' ? 'split-owed' : 
                                  balance.status === 'owes' ? 'split-owes' : 'split-settled';
                const statusText = balance.status === 'owed' ? `Owed ${Math.abs(balance.balance).toFixed(2)}` :
                                 balance.status === 'owes' ? `Owes ${Math.abs(balance.balance).toFixed(2)}` :
                                 'Settled';
                
                return `
                    <div class="split-item">
                        <div>
                            <div style="font-weight: 600; margin-bottom: 0.5rem;">${balance.person}</div>
                            <div style="color: var(--text-secondary); font-size: 0.875rem;">
                                Paid: ${balance.paid.toFixed(2)} • Fair Share: ${balance.fair_share.toFixed(2)}
                            </div>
                        </div>
                        <div class="split-status ${statusClass}">
                            ${statusText}
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading split report:', error);
    }
}

// Save Trip
async function handleTripSave() {
    try {
        const response = await fetch('/api/save', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Trip saved successfully!', 'success');
        } else {
            showNotification('Error saving trip: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error saving trip: ' + error.message, 'error');
    }
}

// Load Modal
async function handleLoadModalOpen() {
    try {
        const response = await fetch('/api/trips');
        const data = await response.json();
        
        if (data.success) {
            const tripsList = document.getElementById('tripsList');
            
            if (data.trips.length === 0) {
                tripsList.innerHTML = '<p class="empty-state">No saved trips found</p>';
            } else {
                tripsList.innerHTML = data.trips.map(trip => `
                    <div class="trip-list-item" onclick="loadTrip('${trip.id}')">
                        <h4>${trip.name}</h4>
                        <p><i class="fas fa-map-marker-alt"></i> ${trip.destination}</p>
                        <p><i class="fas fa-calendar"></i> ${trip.start_date} to ${trip.end_date}</p>
                    </div>
                `).join('');
            }
            
            loadModal.style.display = 'block';
        }
    } catch (error) {
        showNotification('Error loading trips: ' + error.message, 'error');
    }
}

// Load Trip
async function loadTrip(tripId) {
    try {
        const response = await fetch(`/api/load/${tripId}`);
        const data = await response.json();
        
        if (data.success) {
            currentTrip = data.trip;
            currentCurrency = data.trip.currency;
            loadModal.style.display = 'none';
            showDashboard();
            showNotification('Trip loaded successfully!', 'success');
        } else {
            showNotification('Error loading trip: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error loading trip: ' + error.message, 'error');
    }
}

// Check database status
async function checkDatabaseStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.success && !data.database_enabled) {
            // Show warning about no database
            showNotification('⚠️ Database not configured - data will not persist. See DATABASE_SETUP.md', 'warning', 8000);
        }
    } catch (error) {
        console.error('Error checking database status:', error);
    }
}

// Check for trip ID in URL (for shared links)
async function checkForTripInURL() {
    const urlPath = window.location.pathname;
    
    // Check if URL is /join/<trip_id>
    if (urlPath.startsWith('/join/')) {
        const tripId = urlPath.split('/join/')[1];
        if (tripId) {
            // Show loading message
            showNotification('Loading shared trip...', 'info');
            
            // Automatically load the trip
            await loadTrip(tripId);
            
            // Update URL to remove /join/ prefix (optional - for cleaner URL)
            window.history.replaceState({}, '', '/');
        }
    }
    
    // Also check URL parameters (?trip=<id>)
    const urlParams = new URLSearchParams(window.location.search);
    const tripIdParam = urlParams.get('trip');
    if (tripIdParam) {
        showNotification('Loading shared trip...', 'info');
        await loadTrip(tripIdParam);
        // Clean up URL
        window.history.replaceState({}, '', '/');
    }
}

// Currency Converter Modal
function handleConverterModalOpen() {
    converterModal.style.display = 'block';
    document.getElementById('conversionResult').style.display = 'none';
}

// Load saved conversion from localStorage
function loadSavedConversion() {
    const saved = localStorage.getItem('savedConversion');
    if (saved) {
        savedConversion = JSON.parse(saved);
        updateConversionDisplay();
    }
}

// Update conversion display on dashboard
function updateConversionDisplay() {
    const conversionDiv = document.getElementById('currencyBreakdown');
    if (!conversionDiv) return;
    
    if (savedConversion && exchangeRates[savedConversion.from] && exchangeRates[savedConversion.to]) {
        // Recalculate current rate
        const currentRate = exchangeRates[savedConversion.to] / exchangeRates[savedConversion.from];
        const fromFlag = currencies.find(c => c.code === savedConversion.from)?.flag || '';
        const toFlag = currencies.find(c => c.code === savedConversion.to)?.flag || '';
        
        conversionDiv.innerHTML = `
            <div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(255,255,255,0.1); border-radius: 6px; font-size: 0.85rem;">
                <div style="opacity: 0.8; margin-bottom: 0.25rem;">Quick Convert:</div>
                <div style="font-weight: 600;">${fromFlag} 1 ${savedConversion.from} = ${toFlag} ${currentRate.toFixed(4)} ${savedConversion.to}</div>
            </div>
        `;
    } else {
        conversionDiv.innerHTML = '';
    }
}

// Convert Currency
async function convertCurrency() {
    const amount = parseFloat(document.getElementById('convertAmount').value);
    const fromCurr = document.getElementById('fromCurrency').value;
    const toCurr = document.getElementById('toCurrency').value;
    
    if (!amount || amount <= 0) {
        showNotification('Please enter a valid amount', 'error');
        return;
    }
    
    if (!exchangeRates[fromCurr] || !exchangeRates[toCurr]) {
        showNotification('Exchange rates not available', 'error');
        return;
    }
    
    // Convert through USD as base
    const amountInUSD = amount / exchangeRates[fromCurr];
    const convertedAmount = amountInUSD * exchangeRates[toCurr];
    const rate = exchangeRates[toCurr] / exchangeRates[fromCurr];
    
    // Display result
    const resultDiv = document.getElementById('conversionResult');
    const convertedValue = document.getElementById('convertedValue');
    const exchangeRate = document.getElementById('exchangeRate');
    
    convertedValue.textContent = `${convertedAmount.toFixed(2)} ${toCurr}`;
    exchangeRate.textContent = `1 ${fromCurr} = ${rate.toFixed(4)} ${toCurr}`;
    resultDiv.style.display = 'block';
    
    // Save conversion preference
    savedConversion = {
        from: fromCurr,
        to: toCurr,
        rate: rate
    };
    localStorage.setItem('savedConversion', JSON.stringify(savedConversion));
    updateConversionDisplay();
    showNotification('Conversion saved to dashboard', 'success');
}

// Invite Link Modal
function handleInviteModalOpen() {
    if (!currentTrip) {
        showNotification('Please create a trip first', 'error');
        return;
    }
    
    const inviteLink = `${window.location.origin}/join/${currentTrip.id}`;
    document.getElementById('inviteLink').value = inviteLink;
    inviteModal.style.display = 'block';
}

// Copy Invite Link
function copyInviteLink() {
    const inviteLinkInput = document.getElementById('inviteLink');
    inviteLinkInput.select();
    inviteLinkInput.setSelectionRange(0, 99999); // For mobile devices
    
    navigator.clipboard.writeText(inviteLinkInput.value).then(() => {
        showNotification('Invite link copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy link', 'error');
    });
}

// Export Modal
function handleExportModalOpen() {
    if (!currentTrip) {
        showNotification('Please create a trip first', 'error');
        return;
    }
    exportModal.style.display = 'block';
}

// Export as Excel
async function exportExcel() {
    try {
        // First save the current trip
        const saveResponse = await fetch('/api/save', {
            method: 'POST'
        });
        
        const saveData = await saveResponse.json();
        
        if (saveData.success) {
            showNotification('Generating Excel file...', 'success');
            setTimeout(() => {
                window.location.href = `/api/export/excel/${currentTrip.id}`;
            }, 500);
            exportModal.style.display = 'none';
        } else {
            showNotification('Error saving trip: ' + saveData.error, 'error');
        }
    } catch (error) {
        showNotification('Error exporting Excel: ' + error.message, 'error');
    }
}

// Export as PDF Summary
async function exportPDF() {
    try {
        const response = await fetch(`/api/export/summary/${currentTrip.id}`);
        const data = await response.json();
        
        if (data.success) {
            // Create a printable summary
            const printWindow = window.open('', '', 'height=600,width=800');
            printWindow.document.write(`
                <html>
                <head>
                    <title>Trip Summary - ${currentTrip.name}</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        h1 { color: #4f46e5; }
                        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #4f46e5; color: white; }
                        .summary-box { background: #f3f4f6; padding: 15px; margin: 10px 0; border-radius: 8px; }
                    </style>
                </head>
                <body>
                    <h1>🛫 ${currentTrip.name}</h1>
                    <div class="summary-box">
                        <p><strong>Destination:</strong> ${currentTrip.destination}</p>
                        <p><strong>Dates:</strong> ${currentTrip.start_date} to ${currentTrip.end_date}</p>
                        <p><strong>Currency:</strong> ${currentTrip.currency}</p>
                    </div>
                    <h2>Summary</h2>
                    <div class="summary-box">
                        <p><strong>Total Expenses:</strong> ${data.summary.total_expenses.toFixed(2)} ${currentTrip.currency}</p>
                        <p><strong>Number of Expenses:</strong> ${data.summary.num_expenses}</p>
                        <p><strong>Average per Expense:</strong> ${data.summary.average_expense.toFixed(2)} ${currentTrip.currency}</p>
                    </div>
                    ${generateExpenseTable(data.expenses)}
                    ${generateCategoryTable(data.categories)}
                    <p style="margin-top: 30px; text-align: center; color: #6b7280;">
                        Generated on ${new Date().toLocaleString()}
                    </p>
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
            exportModal.style.display = 'none';
        }
    } catch (error) {
        showNotification('Error generating PDF: ' + error.message, 'error');
    }
}

// Helper function to generate expense table
function generateExpenseTable(expenses) {
    if (!expenses || expenses.length === 0) return '';
    
    let html = '<h2>Expenses</h2><table><thead><tr><th>Date</th><th>Description</th><th>Category</th><th>Amount</th><th>Paid By</th></tr></thead><tbody>';
    
    expenses.forEach(exp => {
        html += `<tr>
            <td>${new Date(exp.date).toLocaleDateString()}</td>
            <td>${exp.description}</td>
            <td>${exp.category}</td>
            <td>${exp.amount.toFixed(2)} ${exp.currency}</td>
            <td>${exp.paid_by}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    return html;
}

// Helper function to generate category table
function generateCategoryTable(categories) {
    if (!categories || categories.length === 0) return '';
    
    let html = '<h2>Category Breakdown</h2><table><thead><tr><th>Category</th><th>Amount</th><th>Percentage</th></tr></thead><tbody>';
    
    categories.forEach(cat => {
        html += `<tr>
            <td>${cat.category}</td>
            <td>${cat.amount.toFixed(2)}</td>
            <td>${cat.percentage}%</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    return html;
}

// Notification System
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#4f46e5'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 1001;
        animation: slideInRight 0.3s;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
