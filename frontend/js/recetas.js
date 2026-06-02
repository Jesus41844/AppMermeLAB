import { API_BASE, AppState, UI } from "./app.js";

export const SeccionRecetas = {
  selectedReceta: null,
  init: () => SeccionRecetas.loadRecetas(),

  loadRecetas: async () => {
    try {
      const headers = UI.getAuthHeader();

      const res = await fetch(`${API_BASE}/api/recetas`, { headers });
      if (!res.ok) {
        throw new Error("No se pudo cargar las recetas");
      }

      const recetas = await res.json();
      AppState.currentRecetas = recetas;
      SeccionRecetas.updateCount(recetas.length);
      SeccionRecetas.renderCards(recetas);
      SeccionRecetas.fillSelect(recetas);
    } catch (e) {
      UI.setError("Error cargando recetas");
      SeccionRecetas.updateCount(0);
    }
  },

  updateCount: (count) => {
    const counter = document.getElementById("receta-count");
    if (counter) counter.innerText = count;
  },

  renderCards: (recetas) => {
    const container = document.getElementById("recipe-cards");
    if (!container) return;

    if (!recetas || recetas.length === 0) {
      container.innerHTML = `
        <div class="col-span-1 sm:col-span-2 lg:col-span-3 rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center text-slate-500">
          <i class="fas fa-box-open text-3xl mb-4"></i>
          <p class="font-semibold">No hay recetas registradas en la base de datos.</p>
          <p class="text-sm mt-2">Agrega una nueva receta para comenzar a trabajar con ella.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = recetas
      .map((r) => {
        // Lógica de Semáforo (Simulada basada en stock_status del backend o check local)
        // En un escenario real, el backend enviaría un flag 'disponibilidad'
        let badgeClass = "bg-emerald-100 text-emerald-700";
        let badgeText = "Stock disponible";

        if (r.insumos_faltantes > 0) {
          badgeClass = "bg-red-100 text-red-700";
          badgeText = "Insumos faltantes";
        } else if (r.stock_critico) {
          badgeClass = "bg-amber-100 text-amber-700";
          badgeText = "Stock crítico";
        }

        return `
            <div class="recipe-card bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all cursor-pointer" onclick="SeccionRecetas.selectReceta('${r.id}')">
                <div class="flex justify-between items-center mb-4">
                    <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><i class="fas fa-mortar-pestle"></i></div>
                    <span class="inline-flex items-center justify-center text-[10px] font-bold uppercase px-2 py-1 rounded-full ${badgeClass}">${badgeText}</span>
                </div>
                <h3 class="font-bold text-lg">${r.nombre}</h3>
                <p class="text-sm text-gray-500 mt-2">${r.descripcion || "Receta estándar"}</p>
                <div class="mt-4 pt-4 border-t text-sm text-gray-400 flex justify-between">
                    <span><i class="fas fa-box"></i> ${r.cantidad_frascos_base} frascos</span>
                    <span class="text-emerald-600 font-bold">Ver detalle</span>
                </div>
            </div>
        `;
      })
      .join("");
  },

  selectReceta: (id) => {
    const receta = AppState.currentRecetas.find((r) => r.id == id);
    if (!receta) return;
    SeccionRecetas.selectedReceta = receta;
    SeccionRecetas.renderPreview(receta);
  },

  renderPreview: (receta) => {
    const panel = document.getElementById("modal-preview");
    const title = document.getElementById("preview-receta-title");
    const subtitle = document.getElementById("preview-receta-subtitle");
    const content = document.getElementById("recipe-preview-content");
    if (!panel || !title || !subtitle || !content) return;

    const brixText =
      receta.brix_min != null && receta.brix_max != null
        ? `${receta.brix_min}-${receta.brix_max} °Bx`
        : "No especificado";
    const tempText =
      receta.temperatura_min != null && receta.temperatura_max != null
        ? `${receta.temperatura_min}-${receta.temperatura_max} °C`
        : "No especificado";
    const ingredientesHtml =
      receta.ingredientes && receta.ingredientes.length
        ? receta.ingredientes
            .map(
              (i) =>
                `<li class="py-3 px-4 border-b border-slate-100 flex justify-between text-sm"><span>${i.nombre}</span><span class="font-semibold">${i.cantidad} ${i.unidad || ""}</span></li>`,
            )
            .join("")
        : `<li class="py-3 px-4 text-sm text-slate-500">No hay materiales definidos.</li>`;

    title.innerText = receta.nombre;
    subtitle.innerText =
      receta.descripcion ||
      `${receta.cantidad_frascos_base} frascos de ${receta.tamano_frasco_gramos}g`;
    content.innerHTML = `
      <div class="space-y-4 mb-6">
        <div>
          <h4 class="text-xs uppercase tracking-wide text-slate-500">Brix requerido</h4>
          <p class="mt-1 text-lg font-semibold text-slate-900">${brixText}</p>
        </div>
        <div>
          <h4 class="text-xs uppercase tracking-wide text-slate-500">Tiempo de preparación</h4>
          <p class="mt-1 text-lg font-semibold text-slate-900">${receta.tiempo_preparacion_min} min</p>
        </div>
        <div>
          <h4 class="text-xs uppercase tracking-wide text-slate-500">Temperatura de cocción</h4>
          <p class="mt-1 text-lg font-semibold text-slate-900">${tempText}</p>
        </div>
        <div>
          <h4 class="text-xs uppercase tracking-wide text-slate-500">Frascos base</h4>
          <p class="mt-1 text-lg font-semibold text-slate-900">${receta.cantidad_frascos_base}</p>
        </div>
        <div>
          <h4 class="text-xs uppercase tracking-wide text-slate-500">Tamaño por frasco</h4>
          <p class="mt-1 text-lg font-semibold text-slate-900">${receta.tamano_frasco_gramos} g</p>
        </div>
      </div>
      <div class="mb-6">
        <h4 class="text-sm uppercase tracking-wide text-slate-500 mb-3">Materiales</h4>
        <ul class="rounded-3xl border border-slate-200 bg-slate-50 overflow-hidden">
          ${ingredientesHtml}
        </ul>
      </div>
      <div class="flex flex-col sm:flex-row sm:justify-end gap-3">
        <button type="button" onclick="SeccionRecetas.deleteReceta(${receta.id})" class="w-full sm:w-auto bg-red-500 text-white px-4 py-3 rounded-lg font-bold hover:bg-red-600 transition-colors">Eliminar receta</button>
        <button type="button" onclick="SeccionRecetas.selectForProduccion(${receta.id})" class="w-full sm:w-auto bg-emerald-600 text-white px-4 py-3 rounded-lg font-bold hover:bg-emerald-700 transition-colors">Ir a calcular</button>
      </div>
    `;
    panel.classList.remove("hidden");
  },

  clearPreview: () => {
    const panel = document.getElementById("modal-preview");
    const content = document.getElementById("recipe-preview-content");
    if (!panel) return;
    panel.classList.add("hidden");
    if (content) content.innerHTML = "";
    SeccionRecetas.selectedReceta = null;
  },

  selectForProduccion: (id) => {
    const receta = AppState.currentRecetas.find((r) => r.id == id);
    if (!receta) return;
    window.location.href = `produccion?receta=${encodeURIComponent(receta.nombre)}`;
  },

  deleteReceta: async (id) => {
    if (!confirm("¿Eliminar esta receta? Esta acción no se puede deshacer.")) {
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/recetas/${id}`, {
        method: "DELETE",
        headers: UI.getAuthHeader(),
      });

      if (res.ok) {
        alert("✅ Receta eliminada");
        if (SeccionRecetas.selectedReceta?.id == id) {
          SeccionRecetas.clearPreview();
        }
        SeccionRecetas.loadRecetas();
      } else {
        const err = await res.json();
        UI.setError(err.error || "No se pudo eliminar la receta");
      }
    } catch (e) {
      UI.setError("Error de conexión al eliminar la receta");
    }
  },

  fillSelect: (recetas) => {
    const select = document.getElementById("receta");
    if (!select) return;

    select.innerHTML = recetas
      .map((r) => `<option value="${r.nombre}">${r.nombre}</option>`)
      .join("");

    // Si venimos redirigidos con una receta seleccionada
    const urlParams = new URLSearchParams(window.location.search);
    const recetaParam = urlParams.get("receta");
    if (recetaParam) select.value = recetaParam;
  },

  addIngredienteInput: () => {
    const div = document.createElement("div");
    div.className = "flex gap-2 mb-2";
    div.innerHTML = `
            <input type="text" placeholder="Ingrediente" class="flex-1 p-2 border rounded text-sm ing-nombre">
            <input type="number" placeholder="Cant" class="w-20 p-2 border rounded text-sm ing-cant">
            <input type="text" placeholder="Unidad" class="w-16 p-2 border rounded text-sm ing-unid">
        `;
    document.getElementById("ingredientes-dinamicos").appendChild(div);
  },
};

// Exponer al alcance global
window.SeccionRecetas = SeccionRecetas;

// Inicialización automática y manejo del formulario
document.addEventListener("DOMContentLoaded", () => {
  if (
    document.getElementById("section-recetas") ||
    document.getElementById("recipe-cards")
  ) {
    SeccionRecetas.init();
  }

  const formReceta = document.getElementById("form-nueva-receta");
  if (formReceta) {
    formReceta.onsubmit = async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const ingredientes = [];
      document
        .querySelectorAll("#ingredientes-dinamicos > div")
        .forEach((div) => {
          const n = div.querySelector(".ing-nombre")?.value;
          const c = div.querySelector(".ing-cant")?.value;
          const u = div.querySelector(".ing-unid")?.value;
          if (n && c)
            ingredientes.push({
              nombre: n,
              cantidad: parseFloat(c),
              unidad: u,
            });
        });

      const payload = {
        nombre: formData.get("nombre"),
        cantidad_frascos_base: parseInt(
          formData.get("cantidad_frascos_base"),
          10,
        ),
        tamano_frasco: parseInt(formData.get("tamano_frasco"), 10),
        tiempo_preparacion_min: parseInt(
          formData.get("tiempo_preparacion_min") || "0",
          10,
        ),
        brix_min: parseFloat(formData.get("brix_min") || "0"),
        brix_max: parseFloat(formData.get("brix_max") || "0"),
        temperatura_min: parseFloat(formData.get("temperatura_min") || "0"),
        temperatura_max: parseFloat(formData.get("temperatura_max") || "0"),
        ingredientes: ingredientes,
      };

      try {
        const res = await fetch(`${API_BASE}/api/recetas`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...UI.getAuthHeader(),
          },
          body: JSON.stringify(payload),
        });
        if (res.ok) {
          alert("✅ Receta guardada exitosamente");
          location.reload();
        } else {
          const err = await res.json();
          UI.setError(err.error || "Error al guardar");
        }
      } catch (e) {
        UI.setError("Error de conexión al guardar receta");
      }
    };
  }
});
