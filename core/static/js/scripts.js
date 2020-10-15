class MyChart {
    constructor(url, chart, canvas, form, giftType) {
        this.chart = chart
        this.canvas = canvas
        this.giftTypes = giftType
        this.form = form
        this.plot(url, giftType)
    }

    plot(url, giftType) {
        const self = this
        const options = {
            scales: {
                xAxes: [{
                    type: "time",
                    time: {
                        unit: "day",
                    }
                }],
            },
            tooltips: {
                titleFontStyle: 'bold',
                titleFontSize: 14,
                callbacks: {
                    title: function (tooltipItem, data) {
                        const currentItem = data.datasets[0].data[tooltipItem[0].index]
                        const date = new Date(tooltipItem[0].xLabel)
                        const dateString = convertDate(date)

                        return `${dateString}  ${tooltipItem[0].yLabel}%`
                    },
                    label: function (tooltipItem, data) {
                        const currentItem = data.datasets[0].data[tooltipItem.index]
                        return ` 額面: ¥${currentItem.faceValue} / 価格: ¥${currentItem.price}`
                    }
                }
            },
            plugins: {
                zoom: {
                    // Container for pan options
                    pan: {
                        enabled: true,
                        mode: 'x',
                    },

                    zoom: {
                        enabled: true,
                        mode: 'xy',
                    }
                }
            },
        }


        function updateChart(gifts) {
            const data = self.genData(gifts)
            if (self.chart) {
                self.chart.destroy()
            }
            self.chart = new Chart(self.canvas, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: giftType,
                        data: data,
                        backgroundColor: self.genColor(data, "rgba(229,120,158,0.1)", "rgba(120,229,229,0.1)"),
                        borderColor: self.genColor(data, "rgb(192,75,108)", "rgb(75,192,192)"),
                    }]
                },
                options: options,
            });
        }

        $.getJSON(url, self.form.serialize(), function (json) {
            if (!json.status === true) {
                return false
            }
            updateChart(json.gifts)
        })
    }

    updateChart(form, url, datasetIdx) {
        const self = this
        $.getJSON(url, form.serialize(), function (json) {
            if (!json.status === true) {
                console.error(json.errors)
                return false
            }
            const datasets = self.chart.data.datasets[datasetIdx]
            datasets.data = []
            datasets.backgroundColor = []
            datasets.borderColor = []
            datasets.label = json.gift_name

            const data = self.genData(json.gifts)
            datasets.data = data
            datasets.backgroundColor = self.genColor(data, "rgba(229,120,158,0.1)", "rgba(120,229,229,0.1)")
            datasets.borderColor = self.genColor(data, "rgb(192,75,108)", "rgb(75,192,192)")
            self.chart.update(data)
        })
    }

    changeTimeUnit(unitType) {
        this.chart.options.scales.xAxes[0].time.unit = unitType
        this.chart.update()
    }

    genData(gifts) {
        return gifts.map(function (item) {
                return {
                    x: item.added_at,
                    y: item.rate,
                    price: item.price,
                    faceValue: item.face_value,
                    sold_at: item.sold_at
                }
            }
        )
    }

    genColor(data, soldColor, onSaleColor) {
        return data.map(d => {
            if (d.sold_at) {
                return soldColor
            } else {
                return onSaleColor
            }
        })
    }
}

function addTimeScaleChangeEvent(myChart, obj, unitType) {
    obj.on("change", function (event) {
        const target = $(event.target)
        if (!target.hasClass("active")) {
            myChart.changeTimeUnit(unitType)
        }
    })
}

function convertDate(date) {
    function zeroFill(string) {
        return ("0" + string).slice(-2)
    }

    const year = date.getFullYear()
    const month = zeroFill(date.getMonth() + 1)
    const day = zeroFill(date.getDate())
    const hour = zeroFill(date.getHours())
    const minute = zeroFill(date.getMinutes())
    const second = zeroFill(date.getSeconds())
    return `${year}/${month}/${day} ${hour}:${minute}`
}
