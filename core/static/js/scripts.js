class MyChart {
    constructor(url, chart, canvas, giftTypes) {
        this.chart = chart
        this.canvas = canvas
        this.giftTypes = giftTypes
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
        console.log(self.pluginZoomConfig)


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

        $.getJSON(url, {"type": "google_play", "available": false, "priceMin": 5000}, function (json) {
            if (!json.status === true) {
                return false
            }
            updateChart(json.gifts)
        })
    }

    updateChart(url, datasetIdx) {
        const self = this
        $.getJSON(url, {"type": "google_play", "available": false}, function (json) {
            if (!json.status === true) {
                console.log(json.status)
                return false
            }
            self.chart.data.datasets[datasetIdx].data = []
            console.log()
            json.gifts.forEach(item => {
                    self.chart.data.datasets[datasetIdx].data.push({
                        x: item.added_at,
                        y: item.rate,
                        price: item.price,
                        faceValue: item.face_value
                    })
                }
            )
            self.chart.update()
        })
    }
}

function convertDate(date) {
    function zeroFill(string) {
        return ("0" + string).slice(-2)
    }

    const year = date.getFullYear()
    const month = zeroFill(date.getMonth())
    const day = zeroFill(date.getDay())
    const hour = zeroFill(date.getHours())
    const minute = zeroFill(date.getMinutes())
    const second = zeroFill(date.getSeconds())
    return `${year}/${month}/${day} ${hour}:${minute}`
}
