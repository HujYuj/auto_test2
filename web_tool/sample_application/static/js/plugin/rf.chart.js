function RfLineChart(pChartCanvasId, pLabel, pBorderColor, pIsLabelAutoIncrease, pDataSizeLimit) {
    this._chartCanvasId = pChartCanvasId;
    this._label = pLabel;
    this._borderColor = pBorderColor
    this._labelAutoIncreaseStart = null;
    if (pIsLabelAutoIncrease && pIsLabelAutoIncrease == true) {
        this._labelAutoIncreaseStart = 1;
    }   
    this._dataSizeLimit = pDataSizeLimit;
    
    this._chart = null
    
    this.initChart();
}

RfLineChart.prototype.initChart = function () {
    var _this = this;
    
    var ctx = $(this._chartCanvasId);
    this._chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{ 
                data: [],
                label: this._label,
                borderColor: this._borderColor,
                fill: false
              }
            ]
        },
        options: {
            maintainAspectRatio: false,
            elements: {
                line: {
                    tension: 0
                }
            },
            scales: {
                yAxes: [{
                    display: true,
                    ticks: {
                        beginAtZero: true,
                        max: 1,
                        min: 0,
                    }
                }]
            },
            legend: {
                onClick: (e) => e.stopPropagation()
            }
        }
    });
};

RfLineChart.prototype.addData = function(pData, pLabel) {
    if (this._labelAutoIncreaseStart != null) {
        if (this._dataSizeLimit != null && this._chart.data.labels.length < this._dataSizeLimit) {
            this._chart.data.labels.push(this._labelAutoIncreaseStart);
            this._labelAutoIncreaseStart += 1
        }
    } else {
        if (this._dataSizeLimit != null && this._chart.data.labels.length >= this._dataSizeLimit) {
            this._chart.data.labels.shift();
        }
        this._chart.data.labels.push(pLabel);
    }
    this._chart.data.datasets.forEach((dataset) => {
        if (this._dataSizeLimit != null && dataset.data.length >= this._dataSizeLimit) {
            dataset.data.shift();
        }
        dataset.data.push(pData);
    });
    this._chart.update();
};

RfLineChart.prototype.clearData = function() {
    this._chart.data.labels.length = 0;
    this._chart.data.datasets.forEach((dataset) => {
        dataset.data.length = 0;
    });
    this._chart.update();
    if (this._labelAutoIncreaseStart) {
        this._labelAutoIncreaseStart = 1;
    }
};

