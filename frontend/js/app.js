export const API_BASE = ""; // Al ser MPA, usamos rutas relativas al mismo host

// Estado Global
export const AppState = {
  get lastCalcId() {
    const rawValue = localStorage.getItem("mermelab:lastCalcId");
    if (!rawValue) return null;
    const parsed = Number(rawValue);
    return Number.isInteger(parsed) ? parsed : null;
  },
  set lastCalcId(val) {
    if (val === null || val === undefined) {
      localStorage.removeItem("mermelab:lastCalcId");
      return;
    }
    localStorage.setItem("mermelab:lastCalcId", String(val));
  },
  currentRecetas: [],
  lastCalculationData: null,
};

// Helpers de UI
export const UI = {
  showLoader: (show) =>
    document.getElementById("global-loader").classList.toggle("hidden", !show),
  setError: (msg) => {
    const el = document.getElementById("error-msg");
    el.innerText = msg || "";
    el.classList.toggle("hidden", !msg);
  },
  openModal: (id) => document.getElementById(id).classList.remove("hidden"),
  closeModal: (id) => document.getElementById(id).classList.add("hidden"),
  getAuthHeader: () => ({}),
};

export const highlightCurrentNav = () => {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  const pageKey =
    path === "/" || path === "/index" ? "inicio" : path.replace(/^\//, "");
  const activeLink = document.getElementById(`nav-${pageKey}`);
  if (activeLink) {
    activeLink.classList.add("active-link");
  }
};
// Cerrar modales con la tecla Escape
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const activeModal = document.querySelector(".modal-overlay:not(.hidden)");
  if (activeModal && activeModal.id) {
    UI.closeModal(activeModal.id);
  }
});
// Exponer al alcance global para compatibilidad con HTML inline events
window.API_BASE = API_BASE;
window.AppState = AppState;
window.UI = UI;
window.openModal = UI.openModal;
window.closeModal = UI.closeModal;
