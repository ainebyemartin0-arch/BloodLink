// ===== INTERACTIVE CHARTS COMPONENT =====

class InteractiveChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.options = {
            type: options.type || 'line',
            data: options.data || [],
            labels: options.labels || [],
            colors: options.colors || ['#dc2626', '#3b82f6', '#10b981', '#f59e0b'],
            backgroundColor: options.backgroundColor || 'rgba(220, 38, 38, 0.1)',
            borderColor: options.borderColor || '#dc2626',
            borderWidth: options.borderWidth || 2,
            pointRadius: options.pointRadius || 4,
            tension: options.tension || 0.4,
            responsive: options.responsive !== false,
            maintainAspectRatio: options.maintainAspectRatio !== false,
            animation: options.animation !== false,
            legend: options.legend !== false,
            grid: options.grid !== false,
            tooltips: options.tooltips !== false,
            onClick: options.onClick || null,
            ...options
        };

        this.padding = { top: 20, right: 20, bottom: 40, left: 60 };
        this.hoveredPoint = null;
        this.animationProgress = 0;

        this.init();
    }

    init() {
        this.setupCanvas();
        this.bindEvents();
        this.animate();
    }

    setupCanvas() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        
        this.width = rect.width;
        this.height = rect.height;
        this.chartWidth = this.width - this.padding.left - this.padding.right;
        this.chartHeight = this.height - this.padding.top - this.padding.bottom;
    }

    bindEvents() {
        if (this.options.tooltips) {
            this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
            this.canvas.addEventListener('mouseleave', () => this.handleMouseLeave());
        }

        if (this.options.onClick) {
            this.canvas.addEventListener('click', (e) => this.handleClick(e));
        }

        window.addEventListener('resize', () => {
            this.setupCanvas();
            this.draw();
        });
    }

    animate() {
        if (this.options.animation && this.animationProgress < 1) {
            this.animationProgress += 0.02;
            if (this.animationProgress > 1) this.animationProgress = 1;
            requestAnimationFrame(() => this.animate());
        }
        this.draw();
    }

    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        switch (this.options.type) {
            case 'line':
                this.drawLineChart();
                break;
            case 'bar':
                this.drawBarChart();
                break;
            case 'pie':
                this.drawPieChart();
                break;
            case 'doughnut':
                this.drawDoughnutChart();
                break;
            case 'area':
                this.drawAreaChart();
                break;
            default:
                this.drawLineChart();
        }

        if (this.options.legend) {
            this.drawLegend();
        }
    }

    drawLineChart() {
        const datasets = this.options.data;
        const labels = this.options.labels;
        
        if (datasets.length === 0 || labels.length === 0) return;

        const maxValue = this.getMaxValue();
        const xStep = this.chartWidth / (labels.length - 1);
        const yScale = this.chartHeight / maxValue;

        // Draw grid
        if (this.options.grid) {
            this.drawGrid(maxValue);
        }

        // Draw axes
        this.drawAxes();

        // Draw lines
        datasets.forEach((dataset, datasetIndex) => {
            const color = this.options.colors[datasetIndex % this.options.colors.length];
            
            this.ctx.beginPath();
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = this.options.borderWidth;
            
            dataset.forEach((value, index) => {
                const x = this.padding.left + index * xStep;
                const y = this.padding.top + this.chartHeight - (value * yScale * this.animationProgress);
                
                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    if (this.options.tension > 0) {
                        const prevX = this.padding.left + (index - 1) * xStep;
                        const prevY = this.padding.top + this.chartHeight - (dataset[index - 1] * yScale * this.animationProgress);
                        const cp1x = prevX + xStep * this.options.tension;
                        const cp1y = prevY;
                        const cp2x = x - xStep * this.options.tension;
                        const cp2y = y;
                        this.ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y);
                    } else {
                        this.ctx.lineTo(x, y);
                    }
                }
            });
            
            this.ctx.stroke();

            // Draw points
            dataset.forEach((value, index) => {
                const x = this.padding.left + index * xStep;
                const y = this.padding.top + this.chartHeight - (value * yScale * this.animationProgress);
                
                this.ctx.beginPath();
                this.ctx.arc(x, y, this.options.pointRadius, 0, 2 * Math.PI);
                this.ctx.fillStyle = color;
                this.ctx.fill();
                this.ctx.strokeStyle = '#ffffff';
                this.ctx.lineWidth = 2;
                this.ctx.stroke();
            });
        });

        // Draw labels
        this.drawLabels();
    }

    drawBarChart() {
        const datasets = this.options.data;
        const labels = this.options.labels;
        
        if (datasets.length === 0 || labels.length === 0) return;

        const maxValue = this.getMaxValue();
        const barWidth = this.chartWidth / labels.length / datasets.length * 0.8;
        const groupWidth = this.chartWidth / labels.length;
        const yScale = this.chartHeight / maxValue;

        // Draw grid
        if (this.options.grid) {
            this.drawGrid(maxValue);
        }

        // Draw axes
        this.drawAxes();

        // Draw bars
        datasets.forEach((dataset, datasetIndex) => {
            const color = this.options.colors[datasetIndex % this.options.colors.length];
            
            dataset.forEach((value, index) => {
                const x = this.padding.left + index * groupWidth + datasetIndex * (groupWidth / datasets.length) + (groupWidth / datasets.length - barWidth) / 2;
                const barHeight = value * yScale * this.animationProgress;
                const y = this.padding.top + this.chartHeight - barHeight;
                
                // Draw bar with gradient
                const gradient = this.ctx.createLinearGradient(0, y, 0, y + barHeight);
                gradient.addColorStop(0, color);
                gradient.addColorStop(1, this.adjustColorBrightness(color, -20));
                
                this.ctx.fillStyle = gradient;
                this.ctx.fillRect(x, y, barWidth, barHeight);
                
                // Add hover effect
                if (this.hoveredPoint && this.hoveredPoint.datasetIndex === datasetIndex && this.hoveredPoint.index === index) {
                    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
                    this.ctx.fillRect(x, y, barWidth, barHeight);
                }
            });
        });

        // Draw labels
        this.drawLabels();
    }

    drawPieChart() {
        const data = this.options.data[0] || [];
        const labels = this.options.labels;
        
        if (data.length === 0) return;

        const total = data.reduce((sum, value) => sum + value, 0);
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const radius = Math.min(this.chartWidth, this.chartHeight) / 2 * 0.8;
        
        let currentAngle = -Math.PI / 2;
        
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI * this.animationProgress;
            const color = this.options.colors[index % this.options.colors.length];
            
            // Draw slice
            this.ctx.beginPath();
            this.ctx.moveTo(centerX, centerY);
            this.ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            this.ctx.closePath();
            
            // Add gradient
            const gradient = this.ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
            gradient.addColorStop(0, this.adjustColorBrightness(color, 20));
            gradient.addColorStop(1, color);
            
            this.ctx.fillStyle = gradient;
            this.ctx.fill();
            
            // Draw border
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Store slice info for tooltips
            this.sliceInfo = this.sliceInfo || [];
            this.sliceInfo[index] = {
                startAngle: currentAngle,
                endAngle: currentAngle + sliceAngle,
                value: value,
                label: labels[index],
                color: color
            };
            
            currentAngle += sliceAngle;
        });

        // Draw labels
        if (labels.length > 0) {
            this.drawPieLabels(data, labels, total, centerX, centerY, radius);
        }
    }

    drawDoughnutChart() {
        const data = this.options.data[0] || [];
        const labels = this.options.labels;
        
        if (data.length === 0) return;

        const total = data.reduce((sum, value) => sum + value, 0);
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const outerRadius = Math.min(this.chartWidth, this.chartHeight) / 2 * 0.8;
        const innerRadius = outerRadius * 0.6;
        
        let currentAngle = -Math.PI / 2;
        
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI * this.animationProgress;
            const color = this.options.colors[index % this.options.colors.length];
            
            // Draw slice
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, outerRadius, currentAngle, currentAngle + sliceAngle);
            this.ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
            this.ctx.closePath();
            
            // Add gradient
            const gradient = this.ctx.createRadialGradient(centerX, centerY, innerRadius, centerX, centerY, outerRadius);
            gradient.addColorStop(0, this.adjustColorBrightness(color, 20));
            gradient.addColorStop(1, color);
            
            this.ctx.fillStyle = gradient;
            this.ctx.fill();
            
            // Draw border
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            currentAngle += sliceAngle;
        });

        // Draw center text
        const centerText = this.options.centerText || '';
        if (centerText) {
            this.ctx.fillStyle = this.options.textColor || '#1a1a1a';
            this.ctx.font = 'bold 16px Inter';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(centerText, centerX, centerY);
        }
    }

    drawAreaChart() {
        const datasets = this.options.data;
        const labels = this.options.labels;
        
        if (datasets.length === 0 || labels.length === 0) return;

        const maxValue = this.getMaxValue();
        const xStep = this.chartWidth / (labels.length - 1);
        const yScale = this.chartHeight / maxValue;

        // Draw grid
        if (this.options.grid) {
            this.drawGrid(maxValue);
        }

        // Draw axes
        this.drawAxes();

        // Draw areas
        datasets.forEach((dataset, datasetIndex) => {
            const color = this.options.colors[datasetIndex % this.options.colors.length];
            
            // Create gradient for area
            const gradient = this.ctx.createLinearGradient(0, this.padding.top, 0, this.height - this.padding.bottom);
            gradient.addColorStop(0, color + '40');
            gradient.addColorStop(1, color + '10');
            
            this.ctx.beginPath();
            this.ctx.fillStyle = gradient;
            
            dataset.forEach((value, index) => {
                const x = this.padding.left + index * xStep;
                const y = this.padding.top + this.chartHeight - (value * yScale * this.animationProgress);
                
                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    if (this.options.tension > 0) {
                        const prevX = this.padding.left + (index - 1) * xStep;
                        const prevY = this.padding.top + this.chartHeight - (dataset[index - 1] * yScale * this.animationProgress);
                        const cp1x = prevX + xStep * this.options.tension;
                        const cp1y = prevY;
                        const cp2x = x - xStep * this.options.tension;
                        const cp2y = y;
                        this.ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y);
                    } else {
                        this.ctx.lineTo(x, y);
                    }
                }
            });
            
            // Complete the area
            this.ctx.lineTo(this.padding.left + (dataset.length - 1) * xStep, this.height - this.padding.bottom);
            this.ctx.lineTo(this.padding.left, this.height - this.padding.bottom);
            this.ctx.closePath();
            this.ctx.fill();
            
            // Draw line on top
            this.ctx.beginPath();
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = this.options.borderWidth;
            
            dataset.forEach((value, index) => {
                const x = this.padding.left + index * xStep;
                const y = this.padding.top + this.chartHeight - (value * yScale * this.animationProgress);
                
                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    if (this.options.tension > 0) {
                        const prevX = this.padding.left + (index - 1) * xStep;
                        const prevY = this.padding.top + this.chartHeight - (dataset[index - 1] * yScale * this.animationProgress);
                        const cp1x = prevX + xStep * this.options.tension;
                        const cp1y = prevY;
                        const cp2x = x - xStep * this.options.tension;
                        const cp2y = y;
                        this.ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y);
                    } else {
                        this.ctx.lineTo(x, y);
                    }
                }
            });
            
            this.ctx.stroke();
        });

        // Draw labels
        this.drawLabels();
    }

    drawGrid(maxValue) {
        const gridLines = 5;
        const step = maxValue / gridLines;
        
        this.ctx.strokeStyle = '#e5e7eb';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        
        for (let i = 0; i <= gridLines; i++) {
            const y = this.padding.top + (i * this.chartHeight / gridLines);
            this.ctx.beginPath();
            this.ctx.moveTo(this.padding.left, y);
            this.ctx.lineTo(this.width - this.padding.right, y);
            this.ctx.stroke();
        }
        
        this.ctx.setLineDash([]);
    }

    drawAxes() {
        this.ctx.strokeStyle = '#374151';
        this.ctx.lineWidth = 2;
        
        // Y-axis
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding.left, this.padding.top);
        this.ctx.lineTo(this.padding.left, this.height - this.padding.bottom);
        this.ctx.stroke();
        
        // X-axis
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding.left, this.height - this.padding.bottom);
        this.ctx.lineTo(this.width - this.padding.right, this.height - this.padding.bottom);
        this.ctx.stroke();
    }

    drawLabels() {
        const labels = this.options.labels;
        const maxValue = this.getMaxValue();
        const xStep = this.chartWidth / (labels.length - 1);
        const yScale = this.chartHeight / maxValue;
        
        this.ctx.fillStyle = '#6b7280';
        this.ctx.font = '12px Inter';
        
        // X-axis labels
        labels.forEach((label, index) => {
            const x = this.padding.left + index * xStep;
            const y = this.height - this.padding.bottom + 20;
            this.ctx.textAlign = 'center';
            this.ctx.fillText(label, x, y);
        });
        
        // Y-axis labels
        const gridLines = 5;
        const step = maxValue / gridLines;
        
        this.ctx.textAlign = 'right';
        for (let i = 0; i <= gridLines; i++) {
            const value = Math.round(i * step);
            const y = this.padding.top + this.chartHeight - (i * this.chartHeight / gridLines);
            this.ctx.fillText(value.toString(), this.padding.left - 10, y + 4);
        }
    }

    drawPieLabels(data, labels, total, centerX, centerY, radius) {
        const labelRadius = radius + 30;
        
        data.forEach((value, index) => {
            const percentage = ((value / total) * 100).toFixed(1);
            const angle = (index / data.length) * 2 * Math.PI - Math.PI / 2;
            const x = centerX + Math.cos(angle) * labelRadius;
            const y = centerY + Math.sin(angle) * labelRadius;
            
            this.ctx.fillStyle = '#374151';
            this.ctx.font = '12px Inter';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(`${labels[index]}: ${percentage}%`, x, y);
        });
    }

    drawLegend() {
        const legendItems = this.options.legendItems || this.options.labels;
        const legendX = this.width - 150;
        const legendY = 20;
        
        this.ctx.fillStyle = '#374151';
        this.ctx.font = '12px Inter';
        
        legendItems.forEach((label, index) => {
            const color = this.options.colors[index % this.options.colors.length];
            const y = legendY + index * 25;
            
            // Color box
            this.ctx.fillStyle = color;
            this.ctx.fillRect(legendX, y, 15, 15);
            
            // Label
            this.ctx.fillStyle = '#374151';
            this.ctx.textAlign = 'left';
            this.ctx.fillText(label, legendX + 25, y + 12);
        });
    }

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Check if hovering over a data point
        this.hoveredPoint = this.getPointAt(x, y);
        
        if (this.hoveredPoint) {
            this.showTooltip(e.clientX, e.clientY, this.hoveredPoint);
            this.canvas.style.cursor = 'pointer';
        } else {
            this.hideTooltip();
            this.canvas.style.cursor = 'default';
        }
        
        this.draw();
    }

    handleMouseLeave() {
        this.hoveredPoint = null;
        this.hideTooltip();
        this.canvas.style.cursor = 'default';
        this.draw();
    }

    handleClick(e) {
        if (this.hoveredPoint && this.options.onClick) {
            this.options.onClick(this.hoveredPoint);
        }
    }

    getPointAt(x, y) {
        // This is a simplified implementation
        // In a real implementation, you'd need to calculate based on chart type
        return null;
    }

    showTooltip(x, y, point) {
        // Create or update tooltip element
        let tooltip = document.getElementById('chart-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'chart-tooltip';
            tooltip.style.cssText = `
                position: fixed;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.2s ease;
            `;
            document.body.appendChild(tooltip);
        }
        
        tooltip.innerHTML = `
            <div><strong>${point.label || ''}</strong></div>
            <div>Value: ${point.value || ''}</div>
        `;
        
        tooltip.style.left = x + 10 + 'px';
        tooltip.style.top = y - 30 + 'px';
        tooltip.style.opacity = '1';
    }

    hideTooltip() {
        const tooltip = document.getElementById('chart-tooltip');
        if (tooltip) {
            tooltip.style.opacity = '0';
            setTimeout(() => {
                if (tooltip.parentNode) {
                    tooltip.parentNode.removeChild(tooltip);
                }
            }, 200);
        }
    }

    getMaxValue() {
        let max = 0;
        this.options.data.forEach(dataset => {
            dataset.forEach(value => {
                if (value > max) max = value;
            });
        });
        return max;
    }

    adjustColorBrightness(color, percent) {
        const num = parseInt(color.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255))
            .toString(16).slice(1);
    }

    // Public methods
    updateData(newData) {
        this.options.data = newData;
        this.animationProgress = 0;
        this.animate();
    }

    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
        this.draw();
    }

    destroy() {
        // Clean up event listeners
        this.canvas.removeEventListener('mousemove', this.handleMouseMove);
        this.canvas.removeEventListener('mouseleave', this.handleMouseLeave);
        this.canvas.removeEventListener('click', this.handleClick);
        window.removeEventListener('resize', this.setupCanvas);
        
        // Remove tooltip
        const tooltip = document.getElementById('chart-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
}

// Export for global use
window.InteractiveChart = InteractiveChart;
