# ストレージの速度

自宅デスクトップPC/ノートPC/サーバについて、ストレージの速度を測定したので記録しておきます。  

## 測定ソフト  
CrystalDiskMark 7.0.0g x64 (ADMINモード)  
データサイズは「1GB (x5)」  
「Sequential Queues: 8, Thread: 1」と「Random Queues: 32, Threads: 16」を測定


## 測定対象

| No. |           機種 | ドライブ種別 |           ディスク名 |          接続I/F |
| --: | -------------- | ------------ | -------------------- | ---------------- |
|   1 | デスクトップPC |   システムSSD | CFD CSSD-M2B1TBG3VNF | PCIe4.0 x4(NVMe) |
|   2 |           同上 |     データSSD | INTEL SSDPE2MW400G4  | PCIe3.0 x4(NVMe) |
|   3 |           同上 | テンポラリ<br>RAM Disk | Primo Ramdisk<br>(Direct-IO mode) | DDR4-3200 DRAM |
|   4 |           同上 |           NAS | (No.6 のドライブ)    |   1Gbps Ethernet |
|   5 | Surface GO     |   システムSSD | TOSHIBA KBG30ZPZ128G | PCIe3.0 x4(NVMe) |
|   6 |   おうちサーバ | データSSD+HDD | 記憶域スペース       | 記事参照[^1] |

## 測定結果
MB/s と IOPS を測定しました。  

* MB/s

<style>
table#benchmark_teble_MBPS th, table#benchmark_teble_IOPS th { text-align: center;  vertical-align: middle; }
table#benchmark_teble_MBPS td, table#benchmark_teble_IOPS td { text-align: right;   vertical-align: middle; }
</style>

<canvas id="benchmark_chart_MBPS" height="200"></canvas>

<table id="benchmark_teble_MBPS">
<thead>
<tr><th rowspan="3">No.</th><th colspan="2">Sequential</th><th colspan="2">Random</th></tr>
<tr>          <th>   Read     </th><th>   Write    </th><th>   Read     </th><th>   Write    </th></tr>
</thead>
<tbody>
<tr><th>1</th><td>   4991.864 </td><td>   1021.249 </td><td>   2272.780 </td><td>    963.961 </td></tr>
<tr><th>2</th><td>   2312.482 </td><td>   1033.822 </td><td>   1033.822 </td><td>    908.450 </td></tr>
<tr><th>3</th><td>  22784.540 </td><td>  23415.746 </td><td>   3841.888 </td><td>   3760.213 </td></tr>
<tr><th>4</th><td>    116.039 </td><td>    116.368 </td><td>    112.829 </td><td>     82.975 </td></tr>
<tr><th>5</th><td>   1314.798 </td><td>    125.391 </td><td>     83.797 </td><td>     37.980 </td></tr>
<tr><th>6</th><td>   1219.595 </td><td>    648.890 </td><td>     16.355 </td><td>    129.260 </td></tr>
</tbody>
</table>

* IOPS

<canvas id="benchmark_chart_IOPS" height="200"></canvas>

<table id="benchmark_teble_IOPS">
<thead>
<tr><th rowspan="3">No.</th><th colspan="2">Sequential</th><th colspan="2">Random</th></tr>
<tr>          <th>   Read     </th><th>   Write    </th><th>   Read     </th><th>   Write    </th></tr>
</thead>
<tbody>
<tr><th>1</th><td>   4760.6   </td><td>    973.9   </td><td> 554877.9   </td><td> 235342.0   </td></tr>
<tr><th>2</th><td>   2205.4   </td><td>    985.9   </td><td> 448273.7   </td><td> 221789.6   </td></tr>
<tr><th>3</th><td>  21729.0   </td><td>  22331.0   </td><td> 937960.9   </td><td> 918020.8   </td></tr>
<tr><th>4</th><td>    110.7   </td><td>    111.0   </td><td>  27546.1   </td><td>  20257.6   </td></tr>
<tr><th>5</th><td>   1253.9   </td><td>    119.6   </td><td>  20458.3   </td><td>   9272.5   </td></tr>
<tr><th>6</th><td>   1163.1   </td><td>    618.8   </td><td>   3992.9   </td><td>  31557.6   </td></tr>
</tbody>
</table>

<script src="/Chart.js/Chart.js"></script>
<script>

var MBPS = [[], [], [], []];
var IOPS = [[], [], [], []];

var data_array = document.getElementById('benchmark_teble_MBPS').getElementsByTagName('td');
for (var i = 0; i < data_array.length; i++) {
	var data = data_array[i];
	MBPS[i%4].push(data.textContent);
}

var data_array = document.getElementById('benchmark_teble_IOPS').getElementsByTagName('td');
for (var i = 0; i < data_array.length; i++) {
	var data = data_array[i];
	IOPS[i%4].push(data.textContent);
}


var ctx_MBPS = document.getElementById("benchmark_chart_MBPS");
var ctx_IOPS = document.getElementById("benchmark_chart_IOPS");
var options = {
	scales: {
		yAxes: [{
			ticks: {
				max: 5500,
				min: 0,
				stepSize: 500
			}
		}, {
			ticks: {
				max: 30000,
				min: 0,
				stepSize: 5000
			}
		}]
	}
};
var bgColors = [
	'rgba(255, 99, 132, 0.2)',
	'rgba(54, 162, 235, 0.2)',
	'rgba(255, 206, 86, 0.2)',
	'rgba(75, 192, 192, 0.2)',
	'rgba(153, 102, 255, 0.2)',
	'rgba(255, 159, 64, 0.2)'
];
var bdColors = [
	'rgba(255,99,132,1)',
	'rgba(54, 162, 235, 1)',
	'rgba(255, 206, 86, 1)',
	'rgba(75, 192, 192, 1)',
	'rgba(153, 102, 255, 1)',
	'rgba(255, 159, 64, 1)'
];
var i = 0;
var chart_MBPS = new Chart(ctx_MBPS, {
	type: 'bar',
	data: {
		labels: ["CFD CSSD-M2B1TBG3VNF", "INTEL SSDPE2MW400G4", "Ramdisk", "NAS", "Surface GO", "記憶域スペース"],
		datasets: [{
			label: 'Sequential Read',
			data: MBPS[i=0],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}, {
			label: 'Sequential Write',
			data: MBPS[++i],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}, {
			label: 'Random Read',
			data: MBPS[++i],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}, {
			label: 'Random Write',
			data: MBPS[++i],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}]
	},
	options: {
		scales: {
			yAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'MB/s'
				},
				ticks: {
					max: 5500,
					min: 0,
					stepSize: 500
				}
			}]
		}
	}
});
var chart_IOPS = new Chart(ctx_IOPS, {
	type: 'bar',
	data: {
		labels: ["CFD CSSD-M2B1TBG3VNF", "INTEL SSDPE2MW400G4", "Ramdisk", "NAS", "Surface GO", "記憶域スペース"],
		datasets: [{
			label: 'Sequential Read',
			data: IOPS[i=0],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}, {
			label: 'Sequential Write',
			data: IOPS[++i],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}, {
			label: 'Random Read',
			data: IOPS[++i],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}, {
			label: 'Random Write',
			data: IOPS[++i],
			backgroundColor : bgColors[i],
			borderColor : bdColors[i],
			borderWidth: 1
		}]
	},
	options: {
		scales: {
			yAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'IOPS'
				},
				ticks: {
					max: 600000,
					min: 0,
					stepSize: 100000
				}
			}]
		}
	}
});
</script>


[^1]: [記憶域スペースの記事](/Windows/%E8%A8%98%E6%86%B6%E5%9F%9F%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9/#_10)で構築した、記憶域階層あり・ReFSのボリューム。SSD2本、HDD14本で構成。
