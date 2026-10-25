const devicesEl = document.querySelector("#devices");
const alertsEl = document.querySelector("#alert-list");
const linkEl = document.querySelector("#link-status");

function clock(timestamp) {
  return new Date(timestamp * 1000).toLocaleString("zh-CN", { hour12: false });
}

const statusLabel = { normal: "正常", alert: "告警", offline: "离线" };

function deviceCard(device) {
  const label = statusLabel[device.status] || device.status;
  return `
    <article class="card ${device.status}">
      <header>
        <strong>${device.name}</strong>
        <span class="badge ${device.status}">${label}</span>
      </header>
      <div class="temp">${device.temperature.toFixed(1)}<span>°C</span></div>
      <p class="meta">${device.device_id} · 湿度 ${device.humidity.toFixed(1)}% · ${clock(device.timestamp)}</p>
    </article>`;
}

function alertRow(alert) {
  const raised = alert.event === "raise";
  return `
    <article class="alert-row">
      <div>
        <strong>${alert.name}</strong>
        <p class="meta">${raised ? "温度超限" : "恢复正常"} · ${alert.temperature.toFixed(1)}°C</p>
      </div>
      <span class="badge ${raised ? "alert" : "normal"}">${clock(alert.timestamp)}</span>
    </article>`;
}

async function refresh() {
  try {
    const [devices, alerts] = await Promise.all([
      fetch("/api/devices").then((response) => response.json()),
      fetch("/api/alerts").then((response) => response.json()),
    ]);
    linkEl.textContent = "链路正常";
    linkEl.className = "status live";
    devicesEl.innerHTML = devices.length
      ? devices.map(deviceCard).join("")
      : `<article class="empty">还没有设备数据。模拟器启动后，这里会显示三台设备。</article>`;
    alertsEl.innerHTML = alerts.length
      ? alerts.map(alertRow).join("")
      : `<article class="empty">目前没有告警。老化测试台会比较频繁地超过 80°C。</article>`;
  } catch (error) {
    linkEl.textContent = "连接中断";
    linkEl.className = "status down";
  }
}

refresh();
setInterval(refresh, 1500);
