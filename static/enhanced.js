// Enhanced features for Legal Task Portal

// Task Search with NLP
function searchTask() {
  const query = document.getElementById("searchInput").value.trim();

  if (!query) {
    showToast("Please enter a search query", "warning");
    return;
  }

  updateSearchUI(true);

  fetch("/nlp_search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: query }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        updateSearchUI(
          false,
          `
                <div class="alert alert-success animate__animated animate__fadeIn">
                    <h5><i class="fas fa-check-circle"></i> Task Found!</h5>
                    <p>Best match: <strong>${data.task}</strong></p>
                    <p class="mb-2">Redirecting in 2 seconds...</p>
                </div>
            `
        );
        setTimeout(() => {
          window.location.href = `/task/${encodeURIComponent(data.task)}`;
        }, 2000);
      } else {
        updateSearchUI(
          false,
          `
                <div class="alert alert-warning animate__animated animate__fadeIn">
                    <h5><i class="fas fa-exclamation-triangle"></i> No Match Found</h5>
                    <p>${data.message}</p>
                    ${
                      data.suggestions
                        ? `
                        <hr>
                        <h6>Try these suggestions:</h6>
                        <div class="row">
                            ${data.suggestions
                              .map(
                                (s) => `
                                <div class="col-md-6 mb-2">
                                    <button class="btn btn-outline-primary btn-sm w-100" 
                                            onclick="selectSuggestion('${s}')">
                                        ${s}
                                    </button>
                                </div>
                            `
                              )
                              .join("")}
                        </div>
                    `
                        : ""
                    }
                </div>
            `
        );
      }
    })
    .catch((error) => {
      console.error("Search error:", error);
      updateSearchUI(
        false,
        `
            <div class="alert alert-danger animate__animated animate__fadeIn">
                <h5><i class="fas fa-exclamation-circle"></i> Search Error</h5>
                <p>Something went wrong. Please try again or contact support.</p>
                <button class="btn btn-outline-danger btn-sm" onclick="searchTask()">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `
      );
    });
}

function updateSearchUI(loading, content = "") {
  const element = document.getElementById("searchResults");
  if (!element) return;

  if (loading) {
    element.innerHTML = `
            <div class="d-flex justify-content-center align-items-center p-4 animate__animated animate__fadeIn">
                <div class="spinner-border text-primary me-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span>Processing your request...</span>
            </div>
        `;
  } else {
    element.innerHTML = content;
  }
}

function selectSuggestion(taskName) {
  document.getElementById("searchInput").value = taskName;
  searchTask();
}

// Location Services with enhanced error handling
function getCurrentLocation() {
  const statusElement = document.getElementById("locationStatus");

  if (!navigator.geolocation) {
    showLocationError("Geolocation is not supported by this browser");
    return;
  }

  statusElement.innerHTML = `
        <div class="alert alert-info animate__animated animate__fadeIn">
            <i class="fas fa-spinner fa-spin"></i> Getting your location...
        </div>
    `;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;

      statusElement.innerHTML = `
                <div class="alert alert-success animate__animated animate__fadeIn">
                    <i class="fas fa-map-marker-alt"></i> Location found!
                    <br><small>Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(
        6
      )}</small>
                </div>
            `;

      document.getElementById("latitude").value = lat;
      document.getElementById("longitude").value = lng;

      // Reverse geocoding to get city name
      reverseGeocode(lat, lng);
    },
    (error) => {
      let errorMessage = "Unable to get location";
      switch (error.code) {
        case error.PERMISSION_DENIED:
          errorMessage = "Location access denied by user";
          break;
        case error.POSITION_UNAVAILABLE:
          errorMessage = "Location information unavailable";
          break;
        case error.TIMEOUT:
          errorMessage = "Location request timed out";
          break;
      }
      showLocationError(errorMessage);
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000, // 5 minutes
    }
  );
}

function showLocationError(message) {
  const statusElement = document.getElementById("locationStatus");
  statusElement.innerHTML = `
        <div class="alert alert-danger animate__animated animate__fadeIn">
            <i class="fas fa-exclamation-triangle"></i> ${message}
            <br><small>Please enter location manually or try again</small>
        </div>
    `;
}

function reverseGeocode(lat, lng) {
  fetch(
    `https://api.opencagedata.com/geocode/v1/json?q=${lat}+${lng}&key=YOUR_OPENCAGE_API_KEY`
  )
    .then((response) => response.json())
    .then((data) => {
      if (data.results && data.results.length > 0) {
        const components = data.results[0].components;
        const city =
          components.city || components.town || components.village || "Unknown";
        const state = components.state || "";

        document.getElementById("cityDisplay").innerHTML = `
                    <small class="text-muted">
                        <i class="fas fa-map-pin"></i> ${city}, ${state}
                    </small>
                `;
      }
    })
    .catch((error) => {
      console.log("Reverse geocoding failed:", error);
    });
}

// Enhanced center finding
function findCenters() {
  const keyword = document.getElementById("centerKeyword").value.trim();
  const lat = parseFloat(document.getElementById("latitude").value);
  const lng = parseFloat(document.getElementById("longitude").value);

  if (!keyword) {
    showToast("Please enter what you're looking for", "warning");
    return;
  }

  if (!lat || !lng) {
    showToast("Please provide your location", "warning");
    return;
  }

  const resultsDiv = document.getElementById("centerResults");
  resultsDiv.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <p>Finding centers near you...</p>
        </div>
    `;

  fetch("/find_centers", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      keyword: keyword,
      latitude: lat,
      longitude: lng,
      radius: 10000, // 10km radius
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.center) {
        resultsDiv.innerHTML = `
                <div class="card border-success animate__animated animate__fadeIn">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0"><i class="fas fa-map-marker-alt"></i> Center Found</h6>
                    </div>
                    <div class="card-body">
                        <h6 class="card-title">${data.center.name}</h6>
                        <p class="card-text">
                            <i class="fas fa-map"></i> ${data.center.address}
                        </p>
                        <button class="btn btn-primary btn-sm" 
                                onclick="openInMaps('${data.center.name}', '${data.center.address}')">
                            <i class="fas fa-directions"></i> Get Directions
                        </button>
                    </div>
                </div>
            `;
      } else {
        resultsDiv.innerHTML = `
                <div class="alert alert-warning animate__animated animate__fadeIn">
                    <i class="fas fa-search"></i> ${
                      data.message || "No centers found nearby"
                    }
                    <br><small>Try different keywords or increase search radius</small>
                </div>
            `;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      resultsDiv.innerHTML = `
            <div class="alert alert-danger animate__animated animate__fadeIn">
                <i class="fas fa-exclamation-circle"></i> Error finding centers
                <br><small>Please try again later</small>
            </div>
        `;
    });
}

function openInMaps(name, address) {
  const encodedAddress = encodeURIComponent(`${name}, ${address}`);
  const mapsUrl = `https://www.google.com/maps/search/${encodedAddress}`;
  window.open(mapsUrl, "_blank");
}

// Enhanced task statistics
function showTaskStats() {
  fetch("/api/task-stats")
    .then((response) => response.json())
    .then((data) => {
      createStatsChart(data);
    })
    .catch((error) => {
      console.error("Stats error:", error);
    });
}

function createStatsChart(data) {
  const ctx = document.getElementById("statsChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: data.labels,
      datasets: [
        {
          data: data.values,
          backgroundColor: [
            "#FF6384",
            "#36A2EB",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
          ],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
}

// Keyboard shortcuts
document.addEventListener("keydown", function (e) {
  // Ctrl+K for quick search
  if (e.ctrlKey && e.key === "k") {
    e.preventDefault();
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }

  // Escape to clear search
  if (e.key === "Escape") {
    const searchInput = document.getElementById("searchInput");
    if (searchInput && document.activeElement === searchInput) {
      searchInput.value = "";
      searchInput.blur();
    }
  }
});

// Enhanced error reporting
window.addEventListener("error", function (e) {
  console.error("Global error:", e.error);
  showToast("An unexpected error occurred", "error");
});

// Add service worker for offline functionality (basic)
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("/sw.js")
      .then(function (registration) {
        console.log("ServiceWorker registration successful");
      })
      .catch(function (err) {
        console.log("ServiceWorker registration failed");
      });
  });
}
