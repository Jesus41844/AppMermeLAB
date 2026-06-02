import { API_BASE, AppState, UI } from "./app.js";
import { SeccionRecetas } from "./recetas.js";

export const SeccionProduccion = {
  calcular: async () => {
    const frascos = parseInt(document.getElementById("frascos_deseados").value);

    if (!frascos || frascos <= 0) {
      UI.setError("Por favor, ingresa una cantidad de frascos válida.");
      return;
    }

    UI.showLoader(true);
    UI.setError(null);

    const payload = {
      receta: document.getElementById("receta").value,
      frascos_deseados: frascos,
    };

    try {
      const res = await fetch(`${API_BASE}/api/calcular`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...UI.getAuthHeader(),
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Error al realizar el cálculo");
      }

      AppState.lastCalcId = data.id_produccion;
      AppState.lastCalculationData = data;
      SeccionProduccion.renderResultados(data);
    } catch (e) {
      UI.setError(e.message || "Error en el cálculo");
    } finally {
      UI.showLoader(false);
    }
  },

  renderResultados: (data) => {
    const resPanel = document.getElementById("resultados");
    const formPanel = document.getElementById("form-panel");
    const container = document.getElementById("produccion-container");
    const wrapper = document.getElementById("layout-wrapper");

    if (container && wrapper) {
      container.classList.remove("max-w-3xl");
      container.classList.add("max-w-6xl");
      wrapper.classList.remove("space-y-8");
      wrapper.classList.add(
        "grid",
        "grid-cols-1",
        "lg:grid-cols-2",
        "gap-10",
        "items-start",
      );
    }

    resPanel.classList.remove("hidden");
    resPanel.classList.add("lg:col-start-2", "w-full");

    if (formPanel) {
      formPanel.classList.add("transition-all", "duration-500", "ease-in-out");
      formPanel.classList.remove(
        "lg:col-start-2",
        "mx-auto",
        "max-w-md",
        "max-w-lg",
      );
      formPanel.classList.add("lg:col-start-1", "w-full");
    }

    document.getElementById("res-producto").innerText = data.producto;
    document.getElementById("res-lote").innerText = data.lote_id;
    document.getElementById("res-brix").innerText =
      data.controles_calidad.brix_requerido;
    document.getElementById("res-temp").innerText =
      data.controles_calidad.temperatura_coccion;
    document.getElementById("print-date").innerText =
      `Reporte generado: ${new Date().toLocaleString()}`;

    const lista = document.getElementById("lista-ingredientes");
    let htmlContent = `<li class="p-3 bg-emerald-50 rounded-lg font-bold flex justify-between"><span>Fruta Equivalente</span><span>${data.fruta_libras_calculada} lb</span></li>`;

    data.ingredientes_adicionales.forEach((ing) => {
      htmlContent += `<li class="flex justify-between py-2 border-b text-sm"><span>${ing.nombre}</span><span>${ing.cantidad} ${ing.unidad}</span></li>`;
    });

    lista.innerHTML = htmlContent;
  },

  previsualizarReporte: () => {
    const data = AppState.lastCalculationData;
    if (!data) {
      UI.setError("No hay datos de producción para imprimir.");
      return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const margin = 20;
    const pageWidth = doc.internal.pageSize.getWidth();
    let currentY = 30;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(5, 150, 105);
    doc.text(data.producto.toUpperCase(), margin, currentY);

    currentY += 12;
    doc.setFontSize(12);
    doc.setTextColor(71, 85, 105);
    doc.setFont("helvetica", "normal");
    doc.text(`Rendimiento: ${data.rendimiento_estimado}`, margin, currentY);

    currentY += 6;
    doc.setDrawColor(200);
    doc.line(margin, currentY, pageWidth - margin, currentY);

    currentY += 15;
    doc.setFontSize(16);
    doc.setTextColor(0);
    doc.setFont("helvetica", "bold");
    doc.text("Materiales / Ingredientes:", margin, currentY);

    currentY += 10;
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);

    const ingredientes = [
      {
        nombre: "Fruta Equivalente",
        cantidad: `${data.fruta_libras_calculada} lb`,
      },
      ...data.ingredientes_adicionales.map((i) => ({
        nombre: i.nombre,
        cantidad: `${i.cantidad} ${i.unidad}`,
      })),
    ];

    ingredientes.forEach((ing) => {
      const dots = ".".repeat(60);
      const lineText = `${ing.nombre} ${dots.substring(ing.nombre.length + ing.cantidad.length)} ${ing.cantidad}`;
      doc.text(lineText, margin, currentY);
      currentY += 8;
    });

    const blobUrl = doc.output("bloburl");
    const frame = document.getElementById("pdf-frame");
    frame.src = blobUrl;
    UI.openModal("modal-preview");
  },

  confirmar: async () => {
    const idProduccion = AppState.lastCalcId;
    if (!Number.isInteger(idProduccion)) {
      UI.setError("No se ha generado una producción válida para confirmar.");
      return;
    }

    const btn = document.getElementById("btn-confirmar-lote");
    btn.disabled = true;
    UI.showLoader(true);

    const brixReal = document.getElementById("brix-real").value;
    const tempReal = document.getElementById("temp-real").value;
    const parsedBrix = brixReal !== "" ? Number(brixReal) : null;
    const parsedTemp = tempReal !== "" ? Number(tempReal) : null;

    try {
      const res = await fetch(`${API_BASE}/api/produccion/confirmar`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...UI.getAuthHeader(),
        },
        body: JSON.stringify({
          id_produccion: idProduccion,
          brix_real: Number.isFinite(parsedBrix) ? parsedBrix : null,
          temp_real: Number.isFinite(parsedTemp) ? parsedTemp : null,
        }),
      });

      const data = await res.json();
      if (res.ok) {
        alert("✅ Stock actualizado correctamente.");
        btn.classList.add("opacity-50", "cursor-not-allowed");
      } else {
        alert("❌ " + data.error);
        btn.disabled = false;
      }
    } catch (e) {
      alert("Error al confirmar");
      btn.disabled = false;
    } finally {
      UI.showLoader(false);
    }
  },
};

window.SeccionProduccion = SeccionProduccion;

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("section-produccion")) {
    SeccionRecetas.loadRecetas();
    document.getElementById("btn-calcular").onclick =
      SeccionProduccion.calcular;
    document.getElementById("btn-confirmar-lote").onclick =
      SeccionProduccion.confirmar;
  }
});
