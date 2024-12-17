import {Chart, registerables} from '../distro/chart.js';

Chart.register(...registerables);

export * from '../distro/chart.js';
export default Chart;
