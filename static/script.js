let isDark = false;

function toggleTheme() {
  isDark = !isDark;
  document.body.className = isDark ? "dark" : "";
}

function getTodayDate() {
  const now = new Date();
  const ist = new Date(now.getTime() + 5.5 * 60 * 60 * 1000);
  return ist.toISOString().split("T")[0];
}

function applyFilter() {
  const dateVal = document.getElementById("date").value || getTodayDate();
  fetchEvents(dateVal);
}

async function fetchEvents(date) {
  try {
    let url = "/latest";
    if (date) {
      url += `?date=${date}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    const container = document.getElementById("events");
    container.innerHTML = "";

    data.forEach(event => {
      const div = document.createElement("div");
      div.className = `event ${event.action}`;

      let content = "";
      if (event.action === "push") {
        content = `<strong>${event.author}</strong> pushed to <strong>${event.to_branch}</strong>`;
      } else if (event.action === "pull_request") {
        content = `<strong>${event.author}</strong> submitted a pull request from <strong>${event.from_branch}</strong> to <strong>${event.to_branch}</strong>`;
      } else if (event.action === "merge") {
        content = `<strong>${event.author}</strong> merged branch <strong>${event.from_branch}</strong> to <strong>${event.to_branch}</strong>`;
      }

      div.innerHTML = `
        <div>${content}</div>
        <div class="timestamp">${event.timeago} (${event.timestamp})</div>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    console.error("Fetch failed:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // theme btn
  const themeBtn = document.getElementById("themeToggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", toggleTheme);
  }

  // filter btn
  const applyBtn = document.getElementById("applyBtn");
  if (applyBtn) {
    applyBtn.addEventListener("click", applyFilter);
  }

  // default date 
  const dateInput = document.getElementById("date");
  if (dateInput) {
    dateInput.value = getTodayDate();
  }
  applyFilter();

  // refresh 15s
  setInterval(applyFilter, 15000);
});
