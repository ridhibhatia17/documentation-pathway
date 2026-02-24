// Enhanced functionality for Legal Task Portal

document.addEventListener("DOMContentLoaded", function () {
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });

  // Search functionality with autocomplete
  const searchInput = document.querySelector('input[name="task_name"]');
  if (searchInput) {
    // Add search suggestions
    const taskCards = document.querySelectorAll(".task-card");
    const taskNames = Array.from(taskCards).map((card) =>
      card.querySelector(".card-title").textContent.trim()
    );

    searchInput.addEventListener("input", function () {
      const value = this.value.toLowerCase();
      if (value.length > 0) {
        showSuggestions(value, taskNames);
      } else {
        hideSuggestions();
      }
    });

    // Filter task cards in real-time
    searchInput.addEventListener("input", function () {
      const value = this.value.toLowerCase();
      taskCards.forEach((card) => {
        const title = card
          .querySelector(".card-title")
          .textContent.toLowerCase();
        if (title.includes(value) || value === "") {
          card.closest(".col-md-6, .col-lg-4").style.display = "block";
        } else {
          card.closest(".col-md-6, .col-lg-4").style.display = "none";
        }
      });
    });
  }

  // Add loading animation to form submission (DISABLED - handled in index.html)
  /*
  const searchForm = document.querySelector('form[action="/task"]');
  if (searchForm) {
    searchForm.addEventListener("submit", function () {
      const submitBtn = this.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<span class="loading"></span> Searching...';
      submitBtn.disabled = true;

      // Re-enable after 3 seconds in case of errors
      setTimeout(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
      }, 3000);
    });
  }
  */

  // Add fade-in animation to cards
  const cards = document.querySelectorAll(".task-card, .info-card");
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add("fade-in");
    }, index * 100);
  });

  // Keyboard navigation for task cards (only if taskCards is defined)
  const taskCardsGlobal = document.querySelectorAll(".task-card");
  if (taskCardsGlobal && taskCardsGlobal.length > 0) {
    taskCardsGlobal.forEach((card, index) => {
      card.setAttribute("tabindex", "0");
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          card.click();
        }
      });
    });
  }

  // Copy functionality for important information
  const copyButtons = document.querySelectorAll(".copy-btn");
  copyButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const textToCopy = this.getAttribute("data-copy");
      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
          this.innerHTML = originalText;
        }, 2000);
      });
    });
  });
});

function showSuggestions(query, taskNames) {
  const suggestions = taskNames
    .filter((name) => name.toLowerCase().includes(query))
    .slice(0, 5);

  let suggestionBox = document.querySelector(".suggestion-box");
  if (!suggestionBox) {
    suggestionBox = document.createElement("div");
    suggestionBox.className =
      "suggestion-box position-absolute bg-white border rounded shadow-sm w-100";
    suggestionBox.style.zIndex = "1000";
    suggestionBox.style.top = "100%";
    suggestionBox.style.left = "0";

    const searchContainer = document.querySelector(
      'input[name="task_name"]'
    ).parentElement;
    searchContainer.style.position = "relative";
    searchContainer.appendChild(suggestionBox);
  }

  if (suggestions.length > 0) {
    suggestionBox.innerHTML = suggestions
      .map(
        (suggestion) =>
          `<div class="suggestion-item p-2 border-bottom cursor-pointer" onclick="selectSuggestion('${suggestion}')">
                ${suggestion}
            </div>`
      )
      .join("");
    suggestionBox.style.display = "block";
  } else {
    suggestionBox.style.display = "none";
  }
}

function hideSuggestions() {
  const suggestionBox = document.querySelector(".suggestion-box");
  if (suggestionBox) {
    suggestionBox.style.display = "none";
  }
}

function selectSuggestion(taskName) {
  document.querySelector('input[name="task_name"]').value = taskName;
  hideSuggestions();
  document.querySelector('form[action="/task"]').submit();
}

// Theme toggle functionality (bonus feature)
function toggleTheme() {
  const body = document.body;
  const isDark = body.classList.contains("dark-theme");

  if (isDark) {
    body.classList.remove("dark-theme");
    localStorage.setItem("theme", "light");
  } else {
    body.classList.add("dark-theme");
    localStorage.setItem("theme", "dark");
  }
}

// Load saved theme
document.addEventListener("DOMContentLoaded", function () {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark-theme");
  }
});

// Utility function for showing toast notifications
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast-notification toast-${type} position-fixed`;
  toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;

  const colors = {
    info: "#3498db",
    success: "#2ecc71",
    warning: "#f39c12",
    error: "#e74c3c",
  };

  toast.style.background = colors[type] || colors.info;
  toast.textContent = message;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.transform = "translateX(0)";
  }, 100);

  setTimeout(() => {
    toast.style.transform = "translateX(100%)";
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 3000);
}
