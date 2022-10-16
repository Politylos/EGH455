$(document).ready(function () {
    const config_bme280 =
    {
        type: 'line',
        data:
        {
            labels: Array(plot_size).fill("00:00:00"),
            datasets:
                [
                    {
                        label: "Temperature",
                        backgroundColor: 'rgb(255, 99, 132)',
                        borderColor: 'rgb(255, 99, 132)',
                        //data: Array(plot_size).fill(null).extend({{values | safe }}),
                        data: {{ values | safe }},
                        fill: false,
                        yAxisID: 'y1',
                    },
                    {
                        label: "Humidity",
                        backgroundColor: 'rgb(0,99,132)',
                        borderColor: 'rgb(0,99,132)',
                        data: Array(plot_size).fill(null),
                        fill: false,
                        yAxisID: 'y2',
                    },
                    {
                        label: "Pressure",
                        backgroundColor: 'rgb(255, 99, 0)',
                        borderColor: 'rgb(255, 99, 0)',
                        data: Array(plot_size).fill(null),
                        fill: false,
                        yAxisID: 'y3',
                    },
                ]
        },
        options:
        {
            responsive: false,
            title:
            {
                display: true,
                text: 'BME280 Sensor'
            },
            tooltips:
            {
                mode: 'index',
                intersect: false,
            },
            hover:
            {
                mode: 'nearest',
                intersect: true
            },
            elements:
            {
                line:
                {
                    tension: 0,
                },
                point:
                {
                    radius: 0,
                    borderWidth: 2,
                    pointStyle: 'circle',
                },
            },
            scales:
            {
                xAxes:
                    [{
                        display: true,
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'Time',
                        }
                    }],
                yAxes:
                    [{
                        ticks:
                        {
                            min: 0,
                            max: 50,
                            fontColor: 'rgb(255, 99, 132)',
                        },
                        display: true,
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'Temperature (°C)',
                            fontColor: 'rgb(255, 99, 132)',
                        },
                        id: 'y1',
                        position: 'left',
                    },
                    {
                        ticks:
                        {
                            min: 0,
                            max: 100,
                            fontColor: 'rgb(0,99,132)',
                        },
                        display: true,
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'Humidity (%)',
                            fontColor: 'rgb(0,99,132)',
                        },
                        id: 'y2',
                        position: 'right',
                    },
                    {
                        ticks:
                        {
                            min: 800,
                            max: 1200,
                            fontColor: 'rgb(255, 99, 0)',
                        },
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'Pressure (hPa)',
                            fontColor: 'rgb(255, 99, 0)',
                        },
                        id: 'y3',
                        position: 'right',
                    }
                    ]
            }
        }
    };
    const config_gas =
    {
        type: 'line',
        data:
        {
            labels: Array(plot_size).fill("00:00:00"),
            datasets:
                [
                    {
                        label: "Gas Oxidising",
                        backgroundColor: 'rgb(255, 99, 132)',
                        borderColor: 'rgb(255, 99, 132)',
                        data: Array(plot_size).fill(null),
                        fill: false,
                        yAxisID: 'y1',
                    },
                    {
                        label: "Gas Reducing",
                        backgroundColor: 'rgb(0,99,132)',
                        borderColor: 'rgb(0,99,132)',
                        data: Array(plot_size).fill(null),
                        fill: false,
                        yAxisID: 'y2',
                    },
                    {
                        label: "Gas NH3",
                        backgroundColor: 'rgb(255, 99, 0)',
                        borderColor: 'rgb(255, 99, 0)',
                        data: Array(plot_size).fill(null),
                        fill: false,
                        yAxisID: 'y3',
                    },
                ]
        },
        options:
        {
            responsive: false,
            title:
            {
                display: true,
                text: 'Gas Sensor'
            },
            tooltips:
            {
                mode: 'index',
                intersect: false,
            },
            hover:
            {
                mode: 'nearest',
                intersect: true
            },
            elements:
            {
                line:
                {
                    tension: 0,
                },
                point:
                {
                    radius: 0,
                    borderWidth: 2,
                    pointStyle: 'circle',
                },
            },
            scales:
            {
                xAxes:
                    [{
                        display: true,
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'Time',
                        }
                    }],
                yAxes:
                    [{
                        ticks:
                        {
                            min: 10,
                            max: 30000,
                            fontColor: 'rgb(255, 99, 132)',
                        },
                        display: true,
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'Oxidising (Ω)',
                            fontColor: 'rgb(255, 99, 132)',
                        },
                        id: 'y1',
                        position: 'left',
                    },
                    {
                        ticks:
                        {
                            min: 100,
                            max: 500000,
                            fontColor: 'rgb(0,99,132)',
                        },
                        display: true,
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'Reducing (Ω)',
                            fontColor: 'rgb(0,99,132)',
                        },
                        id: 'y2',
                        position: 'right',
                    },
                    {
                        ticks:
                        {
                            min: 100,
                            max: 500000,
                            fontColor: 'rgb(255, 99, 0)',
                        },
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'NH3 (Ω)',
                            fontColor: 'rgb(255, 99, 0)',
                        },
                        id: 'y3',
                        position: 'right',
                    }
                    ]
            }
        }
    };

    const context_bme280 = document.getElementById('chart_bme280').getContext('2d');
    const context_gas = document.getElementById('chart_gas').getContext('2d');

    const lineChart_bme280 = new Chart(context_bme280, config_bme280);
    const lineChart_gas = new Chart(context_gas, config_gas);

    const source = new EventSource("/chart-data");

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (config_bme280.data.labels.length === plot_size) {
            config_bme280.data.labels.shift();
            config_bme280.data.datasets[0].data.shift();
            config_bme280.data.datasets[1].data.shift();
            config_bme280.data.datasets[2].data.shift();
            config_gas.data.labels.shift();
            config_gas.data.datasets[0].data.shift();
            config_gas.data.datasets[1].data.shift();
            config_gas.data.datasets[2].data.shift();
        }
        config_bme280.data.labels.push(data.time);
        config_bme280.data.datasets[0].data.push(data.value1.toFixed(2));
        config_bme280.data.datasets[1].data.push(data.value2.toFixed(2));
        config_bme280.data.datasets[2].data.push(data.value3.toFixed(2));

        config_gas.data.labels.push(data.time);
        config_gas.data.datasets[0].data.push(data.value4);
        config_gas.data.datasets[1].data.push(data.value5);
        config_gas.data.datasets[2].data.push(data.value6);

        lineChart_bme280.update();
        lineChart_gas.update();
    }
    $("#0").click(function () {
        plot_size = 600;
        lineChart_bme280.update();
        lineChart_gas.update();
    });
    $("#1").click(function () {
        plot_size = 60;
        lineChart_bme280.update();
        lineChart_gas.update();
    });
});

