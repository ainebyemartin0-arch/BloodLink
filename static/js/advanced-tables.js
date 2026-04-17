// ===== ADVANCED DATA TABLES COMPONENT =====

class AdvancedTable {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id '${containerId}' not found`);
            return;
        }

        this.options = {
            data: options.data || [],
            columns: options.columns || [],
            sortable: options.sortable !== false,
            filterable: options.filterable !== false,
            searchable: options.searchable !== false,
            pagination: options.pagination !== false,
            pageSize: options.pageSize || 10,
            pageSizes: options.pageSizes || [10, 25, 50, 100],
            showActions: options.showActions !== false,
            actions: options.actions || [],
            emptyMessage: options.emptyMessage || 'No data available',
            loadingMessage: options.loadingMessage || 'Loading...',
            onRowClick: options.onRowClick || null,
            onSort: options.onSort || null,
            onFilter: options.onFilter || null,
            onPageChange: options.onPageChange || null,
            ...options
        };

        this.currentPage = 1;
        this.pageSize = this.options.pageSize;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.filters = {};
        this.searchTerm = '';
        this.loading = false;

        this.init();
    }

    init() {
        this.createTableStructure();
        this.bindEvents();
        this.render();
    }

    createTableStructure() {
        const controlsHtml = this.createControls();
        const tableHtml = this.createTable();
        const paginationHtml = this.createPagination();

        this.container.innerHTML = `
            ${controlsHtml}
            ${tableHtml}
            ${paginationHtml}
        `;

        // Store references to elements
        this.searchInput = this.container.querySelector('.table-search-input');
        this.filterSelects = this.container.querySelectorAll('.table-filter');
        this.tableElement = this.container.querySelector('.advanced-table');
        this.tbodyElement = this.container.querySelector('.advanced-table tbody');
        this.paginationInfo = this.container.querySelector('.pagination-info');
        this.paginationControls = this.container.querySelector('.pagination-controls');
        this.pageSizeSelect = this.container.querySelector('.pagination-page-size select');
    }

    createControls() {
        if (!this.options.filterable && !this.options.searchable) {
            return '';
        }

        return `
            <div class="table-controls">
                ${this.options.searchable ? `
                    <div class="table-search">
                        <i class="material-icons table-search-icon">search</i>
                        <input type="text" class="table-search-input" placeholder="Search...">
                    </div>
                ` : ''}
                
                <div class="table-filters">
                    ${this.options.columns.map(column => {
                        if (column.filterable && column.filterOptions) {
                            return `
                                <select class="table-filter" data-column="${column.key}">
                                    <option value="">${column.filterPlaceholder || `Filter by ${column.title}`}</option>
                                    ${column.filterOptions.map(option => 
                                        `<option value="${option.value}">${option.label}</option>`
                                    ).join('')}
                                </select>
                            `;
                        }
                        return '';
                    }).join('')}
                </div>
                
                <div class="table-actions">
                    <button class="table-btn" onclick="advancedTable.exportData()">
                        <i class="material-icons">download</i>
                        Export
                    </button>
                    <button class="table-btn" onclick="advancedTable.refresh()">
                        <i class="material-icons">refresh</i>
                        Refresh
                    </button>
                </div>
            </div>
        `;
    }

    createTable() {
        const headers = this.options.columns.map(column => {
            const sortableClass = this.options.sortable && column.sortable !== false ? 'sortable' : '';
            const sortIcon = this.getSortIcon(column.key);
            
            return `
                <th class="${sortableClass}" data-column="${column.key}">
                    ${column.title}
                    ${this.options.sortable && column.sortable !== false ? `
                        <i class="material-icons sort-icon ${sortIcon}">${sortIcon === 'active' ? 
                            (this.sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward') : 
                            'unfold_more'}</i>
                    ` : ''}
                </th>
            `;
        }).join('');

        if (this.options.showActions) {
            headers += '<th class="table-actions-header">Actions</th>';
        }

        return `
            <div class="advanced-table-container">
                <table class="advanced-table">
                    <thead>
                        <tr>${headers}</tr>
                    </thead>
                    <tbody>
                        <!-- Table rows will be inserted here -->
                    </tbody>
                </table>
            </div>
        `;
    }

    createPagination() {
        if (!this.options.pagination) {
            return '';
        }

        return `
            <div class="table-pagination">
                <div class="pagination-info">
                    Showing <span class="pagination-start">0</span> to <span class="pagination-end">0</span> 
                    of <span class="pagination-total">0</span> entries
                </div>
                
                <div class="pagination-controls">
                    <button class="pagination-btn" onclick="advancedTable.goToPage(1)" ${this.currentPage === 1 ? 'disabled' : ''}>
                        <i class="material-icons">first_page</i>
                    </button>
                    <button class="pagination-btn" onclick="advancedTable.previousPage()" ${this.currentPage === 1 ? 'disabled' : ''}>
                        <i class="material-icons">chevron_left</i>
                    </button>
                    
                    <div class="pagination-numbers">
                        <!-- Page numbers will be inserted here -->
                    </div>
                    
                    <button class="pagination-btn" onclick="advancedTable.nextPage()" ${this.isLastPage() ? 'disabled' : ''}>
                        <i class="material-icons">chevron_right</i>
                    </button>
                    <button class="pagination-btn" onclick="advancedTable.goToPage(this.totalPages)" ${this.isLastPage() ? 'disabled' : ''}>
                        <i class="material-icons">last_page</i>
                    </button>
                </div>
                
                <div class="pagination-page-size">
                    <span>Show</span>
                    <select class="pagination-size-select" onchange="advancedTable.changePageSize(this.value)">
                        ${this.options.pageSizes.map(size => 
                            `<option value="${size}" ${size === this.pageSize ? 'selected' : ''}>${size}</option>`
                        ).join('')}
                    </select>
                    <span>entries</span>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Search event
        if (this.searchInput) {
            let searchTimeout;
            this.searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchTerm = e.target.value;
                    this.currentPage = 1;
                    this.render();
                }, 300);
            });
        }

        // Filter events
        this.filterSelects.forEach(select => {
            select.addEventListener('change', (e) => {
                const column = e.target.dataset.column;
                this.filters[column] = e.target.value;
                this.currentPage = 1;
                this.render();
            });
        });

        // Sort events
        if (this.options.sortable) {
            this.container.querySelectorAll('th.sortable').forEach(th => {
                th.addEventListener('click', () => {
                    const column = th.dataset.column;
                    this.sort(column);
                });
            });
        }

        // Page size change
        if (this.pageSizeSelect) {
            this.pageSizeSelect.addEventListener('change', (e) => {
                this.changePageSize(parseInt(e.target.value));
            });
        }
    }

    getFilteredData() {
        let data = [...this.options.data];

        // Apply search
        if (this.searchTerm) {
            data = data.filter(row => {
                return this.options.columns.some(column => {
                    const value = this.getNestedValue(row, column.key);
                    return value && value.toString().toLowerCase().includes(this.searchTerm.toLowerCase());
                });
            });
        }

        // Apply filters
        Object.keys(this.filters).forEach(column => {
            const filterValue = this.filters[column];
            if (filterValue) {
                data = data.filter(row => {
                    const value = this.getNestedValue(row, column);
                    return value == filterValue;
                });
            }
        });

        return data;
    }

    getSortedData(data) {
        if (!this.sortColumn) {
            return data;
        }

        return data.sort((a, b) => {
            const aValue = this.getNestedValue(a, this.sortColumn);
            const bValue = this.getNestedValue(b, this.sortColumn);

            if (aValue === null || aValue === undefined) return 1;
            if (bValue === null || bValue === undefined) return -1;

            let comparison = 0;
            if (typeof aValue === 'string' && typeof bValue === 'string') {
                comparison = aValue.localeCompare(bValue);
            } else {
                comparison = aValue - bValue;
            }

            return this.sortDirection === 'asc' ? comparison : -comparison;
        });
    }

    getPaginatedData(data) {
        if (!this.options.pagination) {
            return data;
        }

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        return data.slice(startIndex, endIndex);
    }

    render() {
        if (this.loading) {
            this.renderLoading();
            return;
        }

        const filteredData = this.getFilteredData();
        const sortedData = this.getSortedData(filteredData);
        const paginatedData = this.getPaginatedData(sortedData);

        this.renderTableRows(paginatedData);
        this.renderPagination(filteredData.length);
        this.updateSortIcons();
    }

    renderTableRows(data) {
        if (data.length === 0) {
            this.renderEmpty();
            return;
        }

        const rows = data.map(row => {
            const cells = this.options.columns.map(column => {
                const value = this.getNestedValue(row, column.key);
                const formattedValue = column.render ? column.render(value, row) : this.formatValue(value, column);
                
                return `<td>${formattedValue}</td>`;
            }).join('');

            const actions = this.options.showActions ? this.renderActions(row) : '';

            return `
                <tr ${this.options.onRowClick ? `onclick="advancedTable.handleRowClick(${JSON.stringify(row).replace(/"/g, '&quot;')})"` : ''}>
                    ${cells}
                    ${actions}
                </tr>
            `;
        }).join('');

        this.tbodyElement.innerHTML = rows;
    }

    renderActions(row) {
        const actions = this.options.actions.map(action => {
            if (action.visible && !action.visible(row)) {
                return '';
            }

            return `
                <button class="table-action-btn ${action.class || ''}" 
                        onclick="advancedTable.handleAction('${action.key}', ${JSON.stringify(row).replace(/"/g, '&quot;')})"
                        title="${action.title || action.key}">
                    <i class="material-icons">${action.icon}</i>
                </button>
            `;
        }).join('');

        return `<td class="table-row-actions">${actions}</td>`;
    }

    renderEmpty() {
        this.tbodyElement.innerHTML = `
            <tr>
                <td colspan="${this.options.columns.length + (this.options.showActions ? 1 : 0)}" class="table-empty">
                    <i class="material-icons table-empty-icon">inbox</i>
                    <div class="table-empty-title">No data found</div>
                    <div class="table-empty-message">${this.options.emptyMessage}</div>
                    ${this.options.emptyAction ? `
                        <button class="table-empty-action" onclick="${this.options.emptyAction}">
                            ${this.options.emptyActionText || 'Add New'}
                        </button>
                    ` : ''}
                </td>
            </tr>
        `;
    }

    renderLoading() {
        this.tbodyElement.innerHTML = `
            <tr>
                <td colspan="${this.options.columns.length + (this.options.showActions ? 1 : 0)}" class="table-loading">
                    <div class="table-loading-spinner"></div>
                    <div>${this.options.loadingMessage}</div>
                </td>
            </tr>
        `;
    }

    renderPagination(totalItems) {
        if (!this.options.pagination) {
            return;
        }

        this.totalPages = Math.ceil(totalItems / this.pageSize);
        const startItem = totalItems === 0 ? 0 : (this.currentPage - 1) * this.pageSize + 1;
        const endItem = Math.min(this.currentPage * this.pageSize, totalItems);

        // Update pagination info
        this.paginationInfo.innerHTML = `
            Showing <span class="pagination-start">${startItem}</span> to <span class="pagination-end">${endItem}</span> 
            of <span class="pagination-total">${totalItems}</span> entries
        `;

        // Update pagination controls
        this.updatePaginationControls();
    }

    updatePaginationControls() {
        if (!this.paginationControls) {
            return;
        }

        const numbersContainer = this.paginationControls.querySelector('.pagination-numbers');
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        const pageNumbers = [];
        for (let i = startPage; i <= endPage; i++) {
            pageNumbers.push(`
                <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" 
                        onclick="advancedTable.goToPage(${i})">
                    ${i}
                </button>
            `);
        }

        numbersContainer.innerHTML = pageNumbers.join('');
    }

    updateSortIcons() {
        this.container.querySelectorAll('.sort-icon').forEach(icon => {
            icon.classList.remove('active');
            icon.textContent = 'unfold_more';
        });

        if (this.sortColumn) {
            const activeIcon = this.container.querySelector(`th[data-column="${this.sortColumn}"] .sort-icon`);
            if (activeIcon) {
                activeIcon.classList.add('active');
                activeIcon.textContent = this.sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward';
            }
        }
    }

    getSortIcon(column) {
        return this.sortColumn === column ? 'active' : '';
    }

    formatValue(value, column) {
        if (value === null || value === undefined) {
            return '-';
        }

        if (column.type === 'date') {
            return new Date(value).toLocaleDateString();
        }

        if (column.type === 'datetime') {
            return new Date(value).toLocaleString();
        }

        if (column.type === 'currency') {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(value);
        }

        if (column.type === 'number') {
            return new Intl.NumberFormat().format(value);
        }

        if (column.badge) {
            const badgeClass = column.badgeClass || 'table-badge-info';
            return `<span class="table-badge ${badgeClass}">${value}</span>`;
        }

        return value;
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current && current[key], obj);
    }

    // Public methods
    sort(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }

        this.render();

        if (this.options.onSort) {
            this.options.onSort(column, this.sortDirection);
        }
    }

    goToPage(page) {
        if (page < 1 || page > this.totalPages) {
            return;
        }

        this.currentPage = page;
        this.render();

        if (this.options.onPageChange) {
            this.options.onPageChange(page, this.pageSize);
        }
    }

    nextPage() {
        if (!this.isLastPage()) {
            this.goToPage(this.currentPage + 1);
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }

    isLastPage() {
        return this.currentPage >= this.totalPages;
    }

    changePageSize(newSize) {
        this.pageSize = newSize;
        this.currentPage = 1;
        this.render();

        if (this.options.onPageChange) {
            this.options.onPageChange(this.currentPage, this.pageSize);
        }
    }

    refresh() {
        this.render();
    }

    setData(newData) {
        this.options.data = newData;
        this.currentPage = 1;
        this.render();
    }

    getData() {
        return this.options.data;
    }

    setLoading(loading) {
        this.loading = loading;
        this.render();
    }

    handleRowClick(row) {
        if (this.options.onRowClick) {
            this.options.onRowClick(row);
        }
    }

    handleAction(actionKey, row) {
        const action = this.options.actions.find(a => a.key === actionKey);
        if (action && action.handler) {
            action.handler(row);
        }
    }

    exportData() {
        const data = this.getFilteredData();
        const csv = this.convertToCSV(data);
        this.downloadCSV(csv, 'table-export.csv');
    }

    convertToCSV(data) {
        if (data.length === 0) {
            return '';
        }

        const headers = this.options.columns.map(col => col.title).join(',');
        const rows = data.map(row => {
            return this.options.columns.map(col => {
                const value = this.getNestedValue(row, col.key);
                return typeof value === 'string' && value.includes(',') ? 
                    `"${value.replace(/"/g, '""')}"` : value;
            }).join(',');
        });

        return [headers, ...rows].join('\n');
    }

    downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Export for global use
window.AdvancedTable = AdvancedTable;
