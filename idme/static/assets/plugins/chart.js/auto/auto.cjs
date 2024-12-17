const chartjs = require('../distro/chart.cjs');
const {Chart, registerables} = chartjs;

Chart.register(...registerables);

module.exports = Object.assign(Chart, chartjs);
