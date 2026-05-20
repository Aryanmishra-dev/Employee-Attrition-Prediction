(function () {
  const chartRegistry = new Map();

  function renderChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") {
      return null;
    }

    const existing = chartRegistry.get(canvasId);
    if (existing) {
      existing.destroy();
    }

    const chart = new Chart(canvas, config);
    chartRegistry.set(canvasId, chart);
    return chart;
  }

  function closeModal() {
    const container = document.getElementById("modal-container");
    if (container) {
      container.innerHTML = "";
    }
  }

  function toggleSidebar() {
    const drawer = document.getElementById("mobile-sidebar");
    if (!drawer) {
      return;
    }
    drawer.classList.toggle("hidden");
  }

  function getTargetFromRequest(event) {
    const element = event.detail.requestConfig?.elt;
    if (!element) {
      return null;
    }

    const selector = element.getAttribute("hx-target");
    if (selector) {
      return document.querySelector(selector);
    }
    return element;
  }

  function compareValues(a, b) {
    const aNumber = Number(a);
    const bNumber = Number(b);
    if (!Number.isNaN(aNumber) && !Number.isNaN(bNumber)) {
      return aNumber - bNumber;
    }
    return String(a).localeCompare(String(b));
  }

  function enhanceTableShell(shell) {
    if (!shell || shell.dataset.enhanced === "true") {
      return;
    }
    shell.dataset.enhanced = "true";

    const filterInput = shell.querySelector("[data-table-filter]");
    const table = shell.querySelector("[data-sortable-table]");
    if (!table) {
      return;
    }

    const body = table.querySelector("tbody");
    const headers = table.querySelectorAll("[data-sort-key]");
    if (!body) {
      return;
    }

    const applyFilter = () => {
      const query = (filterInput?.value || "").trim().toLowerCase();
      body.querySelectorAll("tr").forEach((row) => {
        const haystack = row.innerText.toLowerCase();
        row.classList.toggle("hidden", query !== "" && !haystack.includes(query));
      });
    };

    headers.forEach((header) => {
      header.addEventListener("click", () => {
        const key = header.dataset.sortKey;
        const currentDirection = header.dataset.sortDirection === "asc" ? "desc" : "asc";
        headers.forEach((item) => {
          item.dataset.sortDirection = "";
        });
        header.dataset.sortDirection = currentDirection;

        const rows = Array.from(body.querySelectorAll("tr"));
        rows.sort((left, right) => {
          const leftCell = left.querySelector(`[data-cell-key="${key}"]`);
          const rightCell = right.querySelector(`[data-cell-key="${key}"]`);
          const leftValue = leftCell?.dataset.sortValue || leftCell?.innerText || "";
          const rightValue = rightCell?.dataset.sortValue || rightCell?.innerText || "";
          const comparison = compareValues(leftValue, rightValue);
          return currentDirection === "asc" ? comparison : -comparison;
        });
        rows.forEach((row) => body.appendChild(row));
      });
    });

    if (filterInput) {
      filterInput.addEventListener("input", applyFilter);
    }
  }

  function initInteractiveTables(scope) {
    const root = scope instanceof Element ? scope : document;
    root.querySelectorAll("[data-table-shell]").forEach(enhanceTableShell);
  }

  document.addEventListener("DOMContentLoaded", () => {
    initInteractiveTables(document);
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    initInteractiveTables(event.target);
  });

  document.body.addEventListener("htmx:responseError", (event) => {
    let payload = null;
    try {
      payload = JSON.parse(event.detail.xhr.responseText);
    } catch (error) {
      payload = null;
    }

    if (!payload) {
      return;
    }

    const target = getTargetFromRequest(event);
    if (target) {
      target.innerHTML = `
        <div class="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          <p class="font-semibold">${payload.error || "Request Error"}</p>
          <p class="mt-1 leading-6">${payload.detail || "Something went wrong."}</p>
        </div>
      `;
      event.preventDefault();
    }
  });

  document.addEventListener("click", (event) => {
    const closeTrigger = event.target.closest("[data-modal-close]");
    if (closeTrigger) {
      closeModal();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeModal();
    }
  });

  window.AttritionApp = {
    closeModal,
    initInteractiveTables,
    renderChart,
    toggleSidebar,
  };
})();
