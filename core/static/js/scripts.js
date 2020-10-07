class MyChart {
    constructor(url, chart, canvas, form, giftTypes) {
        this.chart = chart
        this.canvas = canvas
        this.giftTypes = giftTypes
        this.form = form
        this.plot(url, giftTypes[0])
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
            const data = gifts.map(function (item) {
                    return {x: item.added_at, y: item.rate, price: item.price, faceValue: item.face_value}
                }
            )
            if (self.chart) {
                self.chart.destroy()
            }
            self.chart = new Chart(self.canvas, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: giftType,
                        data: data,
                        backgroundColor: "rgba(120,229,229,0.1)",
                        borderColor: "rgb(75,192,192)",
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
            self.chart.data.datasets[datasetIdx].data = []
            json.gifts.forEach(item => {
                    self.chart.data.datasets[datasetIdx].data.push({
                        t: item.added_at,
                        y: item.rate,
                        price: item.price,
                        faceValue: item.face_value
                    })
                }
            )
            self.chart.update()
        })
    }

    changeTimeUnit(unitType) {
        this.chart.options.scales.xAxes[0].time.unit = unitType
        this.chart.update()
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
