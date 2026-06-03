import { API_BASE, UI } from "./app.js";

export const SeccionInicio = {
  init: () => {
    SeccionInicio.checkHealth();
    SeccionInicio.updateStats();
  },

  checkHealth: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      const statusEl = document.getElementById("api-status");
      if (!statusEl) return;

      if (res.ok) {
        statusEl.innerText = "En línea";
        const dot = statusEl.previousElementSibling;
        if (dot) dot.classList.replace("bg-red-500", "bg-emerald-500");
      } else throw new Error();
    } catch {
      const statusEl = document.getElementById("api-status");
      if (!statusEl) return;
      statusEl.innerText = "Desconectado";
      const dot = statusEl.previousElementSibling;
      if (dot) dot.classList.replace("bg-emerald-500", "bg-red-500");
    }
  },

  updateStats: async () => {
    const updateElement = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.innerText = value;
    };

    const headers = UI.getAuthHeader();

    // Cargar Recetas Activas
    fetch(`${API_BASE}/api/recetas`, { headers })
      .then((res) => res.json())
      .then((data) => updateElement("stat-recetas", data.length))
      .catch((e) => console.warn("Error cargando conteo de recetas", e));

    // Cargar Lotes Completados
    fetch(`${API_BASE}/api/lotes`, { headers })
      .then((res) => res.json())
      .then((data) => {
        const completados = data.filter(
          (l) => l.estado === "completado",
        ).length;
        updateElement("stat-lotes", completados);
      })
      .catch((e) => console.warn("Error cargando estadísticas de lotes", e));

    // Cargar Alertas de Inventario
    fetch(`${API_BASE}/api/inventario`, { headers })
      .then((res) => res.json())
      .then((data) => {
        const alertas = data.filter(
          (i) => i.stock <= (i.stock_minimo || 0),
        ).length;
        updateElement("stat-alertas", alertas);
      })
      .catch((e) => console.warn("Error cargando alertas de inventario", e));
  },
};

// Exponer al alcance global
window.SeccionInicio = SeccionInicio;
document.addEventListener("DOMContentLoaded", () => SeccionInicio.init());
