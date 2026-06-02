import { API_BASE, UI } from "./app.js";

export const SeccionInventario = {
  state: {
    mode: "new",
    items: [],
  },

  init: () => {
    SeccionInventario.loadInventario();
    const form = document.getElementById("form-nuevo-ingrediente");
    if (form) {
      form.onsubmit = SeccionInventario.crear;
    }

    const newBtn = document.getElementById("mode-new-btn");
    const existingBtn = document.getElementById("mode-existing-btn");
    const select = document.getElementById("ing-existing");

    if (newBtn) newBtn.onclick = () => SeccionInventario.setMode("new");
    if (existingBtn)
      existingBtn.onclick = () => SeccionInventario.setMode("existing");
    if (select) select.onchange = SeccionInventario.updateExistingUnit;
  },

  openModal: (mode = "new") => {
    SeccionInventario.setMode(mode);
    UI.openModal("modal-ingrediente");
  },

  setMode: (mode) => {
    SeccionInventario.state.mode = mode;

    const blockNew = document.getElementById("block-new");
    const blockExisting = document.getElementById("block-existing");
    const title = document.getElementById("modal-ingredient-title");
    const newBtn = document.getElementById("mode-new-btn");
    const existingBtn = document.getElementById("mode-existing-btn");
    const submit = document.getElementById("submit-ingredient-btn");

    if (mode === "existing") {
      blockNew.classList.add("hidden");
      blockExisting.classList.remove("hidden");
      title.innerText = "Aumentar stock existente";
      submit.innerText = "Agregar stock";
      newBtn.classList.remove("bg-emerald-600", "text-white");
      newBtn.classList.add(
        "border-slate-300",
        "bg-slate-100",
        "text-slate-700",
      );
      existingBtn.classList.remove(
        "border-slate-300",
        "bg-slate-100",
        "text-slate-700",
      );
      existingBtn.classList.add("bg-emerald-600", "text-white");
    } else {
      blockNew.classList.remove("hidden");
      blockExisting.classList.add("hidden");
      title.innerText = "Registrar nuevo material";
      submit.innerText = "Registrar";
      existingBtn.classList.remove("bg-emerald-600", "text-white");
      existingBtn.classList.add(
        "border-slate-300",
        "bg-slate-100",
        "text-slate-700",
      );
      newBtn.classList.remove(
        "border-slate-300",
        "bg-slate-100",
        "text-slate-700",
      );
      newBtn.classList.add("bg-emerald-600", "text-white");
    }

    SeccionInventario.clearForm();
  },

  loadInventario: async () => {
    try {
      const headers = UI.getAuthHeader();

      const res = await fetch(`${API_BASE}/api/inventario`, { headers });
      const data = await res.json();
      SeccionInventario.state.items = data;
      SeccionInventario.render(data);
      SeccionInventario.populateExistingSelect(data);
    } catch (e) {
      UI.setError("Error al cargar inventario");
    }
  },

  render: (items) => {
    const tbody = document.getElementById("inventory-table");
    if (!tbody) return;

    tbody.innerHTML = items
      .map(
        (i) => `
            <tr>
                <td class="px-6 py-4 font-medium">${i.nombre}</td>
                <td class="px-6 py-4 text-center font-bold ${i.stock < 5 ? "text-red-500" : "text-emerald-600"}">${i.stock}</td>
                <td class="px-6 py-4 text-center text-gray-500">${i.unidad}</td>
                <td class="px-6 py-4 text-right">
                    <span class="px-2 py-1 rounded-full text-xs font-bold ${i.stock > 0 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}">
                        ${i.stock > 0 ? "Disponible" : "Agotado"}
                    </span>
                </td>
            </tr>
        `,
      )
      .join("");
  },

  populateExistingSelect: (items) => {
    const select = document.getElementById("ing-existing");
    const unidadInput = document.getElementById("ing-existing-unidad");
    if (!select) return;

    if (!items.length) {
      select.innerHTML = "<option value=''>No hay materiales cargados</option>";
      unidadInput.value = "";
      select.disabled = true;
      return;
    }

    select.disabled = false;
    select.innerHTML = items
      .map(
        (item) =>
          `<option value="${item.nombre}" data-unidad="${item.unidad}">${item.nombre}</option>`,
      )
      .join("");

    SeccionInventario.updateExistingUnit();
  },

  updateExistingUnit: () => {
    const select = document.getElementById("ing-existing");
    const unidadInput = document.getElementById("ing-existing-unidad");
    if (!select || !unidadInput) return;

    const selectedOption = select.options[select.selectedIndex];
    unidadInput.value = selectedOption?.dataset?.unidad || "";
  },

  clearForm: () => {
    const nombre = document.getElementById("ing-nombre");
    const stock = document.getElementById("ing-stock");
    const stockMinimo = document.getElementById("ing-stock-minimo");
    const unidad = document.getElementById("ing-unidad");
    const existingAmount = document.getElementById("ing-stock-amount");

    if (nombre) nombre.value = "";
    if (stock) stock.value = "0";
    if (stockMinimo) stockMinimo.value = "0";
    if (unidad) unidad.value = "";
    if (existingAmount) existingAmount.value = "0";

    const select = document.getElementById("ing-existing");
    if (select && select.options.length) select.selectedIndex = 0;
    SeccionInventario.updateExistingUnit();
  },

  crear: async (e) => {
    e.preventDefault();
    const mode = SeccionInventario.state.mode;
    let payload;

    if (mode === "existing") {
      const select = document.getElementById("ing-existing");
      const cantidad = parseFloat(
        document.getElementById("ing-stock-amount").value,
      );
      const unidad = document.getElementById("ing-existing-unidad").value;
      payload = {
        nombre: select?.value || "",
        stock: cantidad,
        unidad,
      };
    } else {
      payload = {
        nombre: document.getElementById("ing-nombre").value,
        stock: parseFloat(document.getElementById("ing-stock").value),
        unidad: document.getElementById("ing-unidad").value,
        stock_minimo: parseFloat(
          document.getElementById("ing-stock-minimo").value,
        ),
      };
    }

    try {
      const res = await fetch(`${API_BASE}/api/ingredientes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...UI.getAuthHeader(),
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        UI.closeModal("modal-ingrediente");
        SeccionInventario.loadInventario();
      } else {
        const err = await res.json();
        UI.setError(err.error || "Error al guardar material");
      }
    } catch (e) {
      UI.setError("Error al guardar material");
    }
  },
};

window.SeccionInventario = SeccionInventario;

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("inventory-table")) {
    SeccionInventario.init();
  }
});
