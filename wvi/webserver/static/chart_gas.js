
$(document).ready(function () {
    const config_gas =
    {
        type: 'line',
        data:
        {
            labels: Array(plot_size).fill("0000-00-00 00:00:00"),
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
                            min: 0,
                            max: 5000,
                            fontColor: 'rgb(255, 99, 132)',
                        },
                        display: true,
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'kO',
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
                            labelString: 'kO',
                            fontColor: 'rgb(0,99,132)',
                        },
                        id: 'y2',
                        position: 'right',
                    },
                    {
                        ticks:
                        {
                            min: 10,
                            max: 100000,
                            fontColor: 'rgb(255, 99, 0)',
                        },
                        scaleLabel:
                        {
                            display: true,
                            labelString: 'kO',
                            fontColor: 'rgb(255, 99, 0)',
                        },
                        id: 'y3',
                        position: 'right',
                    }
                    ]
            }
        }
    };

    const context = document.getElementById('chart_gas').getContext('2d');

    const lineChart = new Chart(context, config_gas);

    const source = new EventSource("/chart-data");

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (config_gas.data.labels.length === plot_size) {
            config_gas.data.labels.shift();
            config_gas.data.datasets[0].data.shift();
            config_gas.data.datasets[1].data.shift();
            config_gas.data.datasets[2].data.shift();
        }
        config_gas.data.labels.push(data.time);
        config_gas.data.datasets[0].data.push(data.value4);
        config_gas.data.datasets[1].data.push(data.value5);
        config_gas.data.datasets[2].data.push(data.value6);
        lineChart.update();
    }
});