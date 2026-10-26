// ---------- Construction des cadrans SVG ----------

const SVG_NS = "http://www.w3.org/2000/svg";
const CX = 200, CY = 200;
const START_DEG = 135;   // 0 en bas à gauche
const SWEEP_DEG = 270;   // jusqu'en bas à droite

function el(tag, attrs, parent) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (parent) parent.appendChild(node);
  return node;
}

function polar(r, deg) {
  const rad = (deg * Math.PI) / 180;
  return [CX + r * Math.cos(rad), CY + r * Math.sin(rad)];
}

function arcPath(r, fromDeg, toDeg) {
  const [x1, y1] = polar(r, fromDeg);
  const [x2, y2] = polar(r, toDeg);
  const large = toDeg - fromDeg > 180 ? 1 : 0;
  return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
}

function buildGauge(svg, { max, major, minor, redFrom, title, label }) {
  const toDeg = (v) => START_DEG + (Math.min(Math.max(v, 0), max) / max) * SWEEP_DEG;

  el("circle", { class: "face", cx: CX, cy: CY, r: 190 }, svg);
  el("path", { class: "arc-track", d: arcPath(176, START_DEG, START_DEG + SWEEP_DEG) }, svg);
  const valueArc = el("path", { class: "arc-value", d: "" }, svg);

  if (redFrom != null) {
    el("path", { class: "redzone", d: arcPath(160, toDeg(redFrom), toDeg(max)) }, svg);
  }

  for (let v = 0; v <= max + 1e-9; v += minor) {
    const isMajor = Math.abs(v / major - Math.round(v / major)) < 1e-6;
    const deg = toDeg(v);
    const red = redFrom != null && v >= redFrom;
    const [x1, y1] = polar(166, deg);
    const [x2, y2] = polar(isMajor ? 146 : 156, deg);
    el("line", {
      class: `${isMajor ? "tick-major" : "tick-minor"}${red ? " tick-red" : ""}`,
      x1, y1, x2, y2,
    }, svg);

    if (isMajor) {
      const [tx, ty] = polar(124, deg);
      const t = el("text", { class: `num${red ? " red" : ""}`, x: tx, y: ty }, svg);
      t.textContent = label(v);
    }
  }

  const t = el("text", { class: "title", x: CX, y: 150 }, svg);
  t.textContent = title;

  const needle = el("g", {}, svg);
  el("polygon", { class: "needle", points: `${CX - 22},${CY - 4} ${CX + 165},${CY} ${CX - 22},${CY + 4}` }, needle);
  el("circle", { class: "hub", cx: CX, cy: CY, r: 16 }, svg);

  return (v) => {
    const deg = toDeg(v);
    needle.setAttribute("transform", `rotate(${deg} ${CX} ${CY})`);
    valueArc.setAttribute("d", deg > START_DEG + 0.5 ? arcPath(176, START_DEG, deg) : "");
  };
}

const RPM_MAX = 8000;
const RPM_RED = 6500;
const SPEED_MAX = 260;

const setTacho = buildGauge(document.getElementById("tacho"), {
  max: RPM_MAX, major: 1000, minor: 250, redFrom: RPM_RED,
  title: "x1000 TR/MIN", label: (v) => v / 1000,
});

const setSpeedo = buildGauge(document.getElementById("speedo"), {
  max: SPEED_MAX, major: 20, minor: 10, redFrom: null,
  title: "KM/H", label: (v) => v,
});

const rpmText = document.getElementById("rpm-value");
const speedText = document.getElementById("speed-value");
const gearText = document.getElementById("gear");
const shiftLight = document.getElementById("shift-light");
const fuelBox = document.querySelector(".fuel");
const fuelFill = document.getElementById("fuel-fill");
const fuelText = document.getElementById("fuel-value");

const FUEL_LOW = 15; // % — la barre passe au rouge en dessous

function setFuel(pct) {
  const p = Math.min(Math.max(pct, 0), 100);
  fuelFill.style.width = `${p}%`;
  fuelText.textContent = `${Math.round(p)} %`;
  fuelBox.classList.toggle("low", p < FUEL_LOW);
}

// ---------- Affichage ----------

const target = { rpm: 0, speed: 0, gear: "–" };
const shown = { rpm: 0, speed: 0 };
let animating = false;

function render() {
  setTacho(shown.rpm);
  setSpeedo(shown.speed);
  rpmText.textContent = Math.round(shown.rpm / 10) * 10;
  speedText.textContent = Math.round(shown.speed);
  gearText.textContent = target.gear;
  shiftLight.classList.toggle("on", shown.rpm >= RPM_RED - 300);
}

// Les aiguilles glissent vers la nouvelle valeur puis la boucle s'arrête.
let last = 0;
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now;
  const k = 1 - Math.exp(-dt * 12);
  shown.rpm += (target.rpm - shown.rpm) * k;
  shown.speed += (target.speed - shown.speed) * k;

  const done = Math.abs(target.rpm - shown.rpm) < 1 && Math.abs(target.speed - shown.speed) < 0.05;
  if (done) {
    shown.rpm = target.rpm;
    shown.speed = target.speed;
  }
  render();

  if (done) animating = false;
  else requestAnimationFrame(frame);
}

// Point d'entrée pour les données OBD (ex. via WebSocket depuis Python) :
//   window.updateDashboard({ rpm: 3200, speed: 87, gear: 4, fuel: 62 })
window.updateDashboard = (data) => {
  if (data.fuel != null) setFuel(data.fuel);
  if (data.rpm != null) target.rpm = data.rpm;
  if (data.speed != null) target.speed = data.speed;
  if (data.gear != null) target.gear = String(data.gear);
  if (!animating) {
    animating = true;
    last = performance.now();
    requestAnimationFrame(frame);
  }
};

render();
