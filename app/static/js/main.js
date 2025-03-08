(function() {
    // Alle Funktionen in einem IIFE gekapselt, um globale Duplikate zu vermeiden
  
    // Supervisor-Kalenderfunktionen (unverändert)
    window.renderSupervisorCalendar = function(draft) {
      var calendarDiv = document.getElementById("calendar");
      calendarDiv.innerHTML = ""; // Vorherigen Inhalt löschen
      var days = Object.keys(draft.days).sort();
      days.forEach(function(dateStr) {
        var dayData = draft.days[dateStr];
        var dayDiv = document.createElement("div");
        dayDiv.className = "calendar-day";
        
        // Header mit Datum
        var header = document.createElement("h3");
        header.textContent = dateStr;
        dayDiv.appendChild(header);
        
        // Container für bereits vorhandene Schichten
        var shiftsContainer = document.createElement("div");
        shiftsContainer.className = "shifts-container";
        
        // Für jede existierende Schicht an diesem Tag
        var shifts = dayData.shifts;
        for (var shiftName in shifts) {
          if (shifts.hasOwnProperty(shiftName)) {
            var shiftData = shifts[shiftName];
            var shiftContainer = document.createElement("div");
            shiftContainer.className = "shift-container";
            
            var shiftBtn = document.createElement("button");
            shiftBtn.setAttribute("type", "button");
            shiftBtn.className = "shift-btn";
            shiftBtn.textContent = shiftName;
            shiftBtn.dataset.day = dateStr;
            shiftBtn.dataset.shift = shiftName;
            
            // Klassen setzen: aktiv/inaktiv und ggf. SV
            if (shiftData.active) {
              shiftBtn.classList.add("active");
            } else {
              shiftBtn.classList.add("inactive");
            }
            if (shiftData.type === "sv") {
              shiftBtn.classList.add("sv");
            }
            
            // Klick: aktiven Zustand umschalten
            shiftBtn.addEventListener("click", function() {
              var day = this.dataset.day;
              var shift = this.dataset.shift;
              var currentState = draft.days[day].shifts[shift].active;
              draft.days[day].shifts[shift].active = !currentState;
              if (draft.days[day].shifts[shift].active) {
                this.classList.remove("inactive");
                this.classList.add("active");
              } else {
                this.classList.remove("active");
                this.classList.add("inactive");
              }
            });
            
            // Button zum Umschalten des Schichttyps (normal ↔ sv)
            var typeToggle = document.createElement("button");
            typeToggle.setAttribute("type", "button");
            typeToggle.className = "type-toggle";
            typeToggle.textContent = "Toggle Type";
            typeToggle.dataset.day = dateStr;
            typeToggle.dataset.shift = shiftName;
            typeToggle.addEventListener("click", function(e) {
              e.stopPropagation();
              var day = this.dataset.day;
              var shift = this.dataset.shift;
              var currentType = draft.days[day].shifts[shift].type;
              draft.days[day].shifts[shift].type = (currentType === "normal") ? "sv" : "normal";
              var parentDiv = this.parentElement;
              var shiftButton = parentDiv.querySelector("button.shift-btn[data-shift='" + shift + "']");
              if (draft.days[day].shifts[shift].type === "sv") {
                shiftButton.classList.add("sv");
              } else {
                shiftButton.classList.remove("sv");
              }
            });
            
            shiftContainer.appendChild(shiftBtn);
            shiftContainer.appendChild(typeToggle);
            shiftsContainer.appendChild(shiftContainer);
          }
        }
        
        // Anzeige von vordefinierten Schichtoptionen (z. B. "mittags", "nachmittags", "abends"),
        // die noch nicht vorhanden sind – durch Anklicken werden sie dem Entwurf hinzugefügt.
        var allowedShifts = ["mittags", "nachmittags", "abends"];
        var optionsContainer = document.createElement("div");
        optionsContainer.className = "shift-options";
        allowedShifts.forEach(function(shiftOption) {
          if (!(shiftOption in dayData.shifts)) {
            var optionBtn = document.createElement("button");
            optionBtn.setAttribute("type", "button");
            optionBtn.className = "shift-option-btn";
            optionBtn.textContent = shiftOption;
            optionBtn.dataset.day = dateStr;
            optionBtn.dataset.shift = shiftOption;
            optionBtn.addEventListener("click", function() {
              var day = this.dataset.day;
              var shift = this.dataset.shift;
              // Neuen Schichteintrag mit Standardwerten hinzufügen
              draft.days[day].shifts[shift] = { active: true, type: "normal" };
              // Neu rendern, damit die Änderung sichtbar wird
              renderSupervisorCalendar(draft);
            });
            optionsContainer.appendChild(optionBtn);
          }
        });
        
        dayDiv.appendChild(shiftsContainer);
        if (optionsContainer.childElementCount > 0) {
          dayDiv.appendChild(optionsContainer);
        }
        calendarDiv.appendChild(dayDiv);
      });
    };
  
    window.saveDraft = function() {
      // Wir nehmen an, dass der globale Entwurf in window.draftGlobal gespeichert wurde
      var draftField = document.getElementById("draft_data");
      draftField.value = JSON.stringify(window.draftGlobal);
      document.getElementById("draftForm").submit();
    };
  
    // Mitarbeiter-Kalenderfunktionen – einheitlicher, tabellarischer Kalender
    if (typeof window.employeeAvailability === 'undefined') {
      window.employeeAvailability = {};
    }
  
    window.renderEmployeeCalendarUnified = function(draft) {
      var calendarDiv = document.getElementById("employeeCalendar");
      calendarDiv.innerHTML = "";
      
      // Erlaubte Schichten (ohne "morgens")
      var allowedShifts = ["mittags", "nachmittags", "abends"];
      
      // Bestimme den Verbund aller im Draft vorhandenen Schichten (nur aus allowedShifts)
      var unionShifts = [];
      Object.keys(draft.days).forEach(function(dateStr) {
        var dayShifts = draft.days[dateStr].shifts;
        allowedShifts.forEach(function(shift) {
          if (dayShifts.hasOwnProperty(shift) && unionShifts.indexOf(shift) === -1) {
            unionShifts.push(shift);
          }
        });
      });
      // Sortiere unionShifts in der Reihenfolge wie in allowedShifts
      unionShifts.sort(function(a, b) {
        return allowedShifts.indexOf(a) - allowedShifts.indexOf(b);
      });
      
      // Erstelle die Tabelle
      var table = document.createElement("table");
      table.className = "availability-table"; // Für CSS-Styling
  
      // Tabellenkopf: Datum und Spalten pro Schicht (nur die unionShifts)
      var headerRow = document.createElement("tr");
      var dateHeader = document.createElement("th");
      dateHeader.textContent = "Datum";
      headerRow.appendChild(dateHeader);
      
      unionShifts.forEach(function(shift) {
        var th = document.createElement("th");
        th.textContent = shift;
        headerRow.appendChild(th);
      });
      // Spalte für "Clear" pro Tag
      var clearTh = document.createElement("th");
      clearTh.textContent = "Clear";
      headerRow.appendChild(clearTh);
      
      table.appendChild(headerRow);
      
      // Für jeden Tag (sortiert)
      var days = Object.keys(draft.days).sort();
      days.forEach(function(dateStr) {
        var row = document.createElement("tr");
        
        // Datumsspalte
        var dateCell = document.createElement("td");
        dateCell.textContent = dateStr;
        row.appendChild(dateCell);
        
        // Initialisiere availability für den Tag, falls noch nicht vorhanden, aber nur für definierte Schichten!
        if (!window.employeeAvailability[dateStr]) {
          var activeShifts = [];
          var dayShifts = draft.days[dateStr].shifts;
          unionShifts.forEach(function(shift) {
            if (dayShifts.hasOwnProperty(shift) && dayShifts[shift].active) {
              activeShifts.push(shift);
            }
          });
          window.employeeAvailability[dateStr] = activeShifts;
        }
        
        // Für jede Spalte (Schicht aus unionShifts)
        unionShifts.forEach(function(shift) {
          var cell = document.createElement("td");
          // Falls der Draft diesen Tag und diese Schicht definiert hat, rendere den Button
          if (draft.days[dateStr].shifts.hasOwnProperty(shift)) {
            var btn = document.createElement("button");
            btn.setAttribute("type", "button");
            btn.className = "emp-shift-btn";
            btn.textContent = shift;
            btn.dataset.day = dateStr;
            btn.dataset.shift = shift;
            if (window.employeeAvailability[dateStr].indexOf(shift) !== -1) {
              btn.classList.add("selected");
            }
            btn.addEventListener("click", function() {
              var day = this.dataset.day;
              var shift = this.dataset.shift;
              var index = window.employeeAvailability[day].indexOf(shift);
              if (index === -1) {
                window.employeeAvailability[day].push(shift);
                this.classList.add("selected");
              } else {
                window.employeeAvailability[day].splice(index, 1);
                this.classList.remove("selected");
              }
            });
            cell.appendChild(btn);
          }
          row.appendChild(cell);
        });
        
        // Clear-Button pro Tag: deselectet alle Schichten dieses Tages
        var clearCell = document.createElement("td");
        var clearBtn = document.createElement("button");
        clearBtn.setAttribute("type", "button");
        clearBtn.className = "clear-day-btn";
        clearBtn.textContent = "Clear";
        clearBtn.dataset.day = dateStr;
        clearBtn.addEventListener("click", function() {
          var day = this.dataset.day;
          window.employeeAvailability[day] = [];
          // Alle Buttons in dieser Zeile aktualisieren
          var row = this.parentElement.parentElement;
          var buttons = row.querySelectorAll("button.emp-shift-btn");
          buttons.forEach(function(btn) {
            btn.classList.remove("selected");
          });
        });
        clearCell.appendChild(clearBtn);
        row.appendChild(clearCell);
        
        table.appendChild(row);
      });
      
      // Globaler Clear-All Button (deselektiert alle Schichten aller Tage)
      var globalClearBtn = document.createElement("button");
      globalClearBtn.setAttribute("type", "button");
      globalClearBtn.className = "clear-all-btn";
      globalClearBtn.textContent = "Alle Schichten deselecten";
      globalClearBtn.addEventListener("click", function() {
        Object.keys(window.employeeAvailability).forEach(function(day) {
          window.employeeAvailability[day] = [];
        });
        // Neu rendern, um die UI zu aktualisieren
        renderEmployeeCalendarUnified(draft);
      });
      
      calendarDiv.appendChild(table);
      calendarDiv.appendChild(globalClearBtn);
    };
  
    window.saveEmployeeAvailability = function() {
      var empDataField = document.getElementById("employee_data");
      empDataField.value = JSON.stringify(window.employeeAvailability);
      document.getElementById("employeeForm").submit();
    };
  
    // Falls Du den bisherigen Kalender nicht mehr benötigst, kannst Du renderEmployeeCalendar ersetzen:
    // window.renderEmployeeCalendar = renderEmployeeCalendarUnified;
  
  })();
  