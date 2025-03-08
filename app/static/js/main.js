(function() {
    // Alle Funktionen in einem IIFE gekapselt, um globale Duplikate zu vermeiden
  
    // Supervisor-Kalenderfunktionen (angepasst für tabellarischen Kalender)
    window.renderSupervisorCalendar = function(draft) {
      var calendarDiv = document.getElementById("calendar");
      calendarDiv.innerHTML = ""; // Vorherigen Inhalt löschen
      
      // Sortiere die Tage nach Datum
      var days = Object.keys(draft.days).sort();
      
      // Extrahiere Monat und Jahr aus dem ersten Datum (Format: "YYYY-MM-DD")
      if (days.length === 0) return;
      
      var firstDate = new Date(days[0]);
      var year = firstDate.getFullYear();
      var month = firstDate.getMonth();
      
      // Erstelle einen Kalender für den Monat
      var firstDayOfMonth = new Date(year, month, 1);
      var lastDayOfMonth = new Date(year, month + 1, 0);
      
      // Bestimme den Wochentag des ersten Tags im Monat (0 = Sonntag, 1 = Montag, ...)
      var firstDayWeekday = firstDayOfMonth.getDay();
      
      // Erstelle den Header mit den Wochentagen
      var headerRow = document.createElement("div");
      headerRow.className = "header-row";
      
      var weekdays = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];
      weekdays.forEach(function(day) {
        var headerCell = document.createElement("div");
        headerCell.className = "header-cell";
        headerCell.textContent = day;
        headerRow.appendChild(headerCell);
      });
      
      calendarDiv.appendChild(headerRow);
      
      // Erstelle die Kalenderwochen
      var currentDate = new Date(firstDayOfMonth);
      // Gehe zum ersten Tag der Woche (Sonntag), in der der Monat beginnt
      currentDate.setDate(currentDate.getDate() - firstDayWeekday);
      
      // Erstelle 6 Wochen (max. Anzahl Wochen, die ein Monat haben kann)
      for (var week = 0; week < 6; week++) {
        var weekRow = document.createElement("div");
        weekRow.className = "row";
        
        // Erstelle 7 Tage pro Woche
        for (var dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {
          var dateStr = currentDate.toISOString().split('T')[0]; // Format: "YYYY-MM-DD"
          var dayCell = document.createElement("div");
          dayCell.className = "day-cell";
          
          // Markiere Tage außerhalb des aktuellen Monats
          if (currentDate.getMonth() !== month) {
            dayCell.classList.add("empty-cell");
          }
          
          // Markiere Wochenenden
          if (dayOfWeek === 0 || dayOfWeek === 6) {
            dayCell.classList.add("weekend");
          }
          
          // Füge das Datum hinzu
          var dateDisplay = document.createElement("div");
          dateDisplay.className = "date-display";
          dateDisplay.textContent = currentDate.getDate();
          dayCell.appendChild(dateDisplay);
          
          // Füge Schichten hinzu, wenn der Tag im Draft existiert
          if (draft.days[dateStr]) {
            var dayData = draft.days[dateStr];
            var shiftsContainer = document.createElement("div");
            shiftsContainer.className = "shifts-container";
            
            // Definiere die Reihenfolge der Schichten
            var orderedShifts = ["mittags", "nachmittags", "abends"];
            
            // Für jede Schicht in der definierten Reihenfolge
            orderedShifts.forEach(function(shiftName) {
              // Prüfe, ob die Schicht für diesen Tag existiert
              if (dayData.shifts.hasOwnProperty(shiftName)) {
                var shiftData = dayData.shifts[shiftName];
                var shiftContainer = document.createElement("div");
                shiftContainer.className = "shift-container";
                
                var shiftBtn = document.createElement("button");
                shiftBtn.setAttribute("type", "button");
                shiftBtn.className = "shift-btn";
                shiftBtn.textContent = shiftName;
                shiftBtn.dataset.day = dateStr;
                shiftBtn.dataset.shift = shiftName;
                
                // Neue Darstellung: Aktiv = grün, Inaktiv = gestrichelt, SV = golden
                if (shiftData.active) {
                  if (shiftData.type === "sv") {
                    shiftBtn.classList.add("sv-active");
                  } else {
                    shiftBtn.classList.add("active");
                  }
                } else {
                  shiftBtn.classList.add("inactive");
                }
                
                // Klick: aktiven Zustand umschalten
                shiftBtn.addEventListener("click", function() {
                  var day = this.dataset.day;
                  var shift = this.dataset.shift;
                  var currentState = draft.days[day].shifts[shift].active;
                  var currentType = draft.days[day].shifts[shift].type;
                  draft.days[day].shifts[shift].active = !currentState;
                  
                  // Finde den Toggle-Button für diese Schicht
                  var parentDiv = this.parentElement;
                  var toggleButton = parentDiv.querySelector(".type-toggle");
                  
                  if (draft.days[day].shifts[shift].active) {
                    this.classList.remove("inactive");
                    if (currentType === "sv") {
                      this.classList.add("sv-active");
                    } else {
                      this.classList.add("active");
                    }
                    
                    // Zeige den Toggle-Button an, wenn die Schicht aktiv ist
                    if (toggleButton) {
                      toggleButton.style.display = "block";
                    }
                  } else {
                    this.classList.remove("active", "sv-active");
                    this.classList.add("inactive");
                    
                    // Verstecke den Toggle-Button, wenn die Schicht inaktiv ist
                    if (toggleButton) {
                      toggleButton.style.display = "none";
                    }
                  }
                });
                
                // Button zum Umschalten des Schichttyps (normal ↔ sv)
                var typeToggle = document.createElement("button");
                typeToggle.setAttribute("type", "button");
                typeToggle.className = "type-toggle";
                typeToggle.textContent = "In SV umwandeln";
                typeToggle.dataset.day = dateStr;
                typeToggle.dataset.shift = shiftName;
                
                // Verstecke den Toggle-Button, wenn die Schicht inaktiv ist
                if (!shiftData.active) {
                  typeToggle.style.display = "none";
                }
                
                typeToggle.addEventListener("click", function(e) {
                  e.stopPropagation();
                  var day = this.dataset.day;
                  var shift = this.dataset.shift;
                  var currentType = draft.days[day].shifts[shift].type;
                  var isActive = draft.days[day].shifts[shift].active;
                  draft.days[day].shifts[shift].type = (currentType === "normal") ? "sv" : "normal";
                  
                  var parentDiv = this.parentElement;
                  var shiftButton = parentDiv.querySelector("button.shift-btn[data-shift='" + shift + "']");
                  
                  if (draft.days[day].shifts[shift].type === "sv") {
                    if (isActive) {
                      shiftButton.classList.remove("active");
                      shiftButton.classList.add("sv-active");
                    }
                  } else {
                    shiftButton.classList.remove("sv-active");
                    if (isActive) {
                      shiftButton.classList.add("active");
                    }
                  }
                });
                
                shiftContainer.appendChild(shiftBtn);
                shiftContainer.appendChild(typeToggle);
                shiftsContainer.appendChild(shiftContainer);
              } else {
                // Schicht existiert noch nicht, füge sie als gestrichelte Option hinzu
                var shiftContainer = document.createElement("div");
                shiftContainer.className = "shift-container dashed";
                
                var optionBtn = document.createElement("button");
                optionBtn.setAttribute("type", "button");
                optionBtn.className = "shift-btn dashed";
                optionBtn.textContent = shiftName;
                optionBtn.dataset.day = dateStr;
                optionBtn.dataset.shift = shiftName;
                
                optionBtn.addEventListener("click", function() {
                  var day = this.dataset.day;
                  var shift = this.dataset.shift;
                  // Neuen Schichteintrag mit Standardwerten hinzufügen
                  draft.days[day].shifts[shift] = { active: true, type: "normal" };
                  // Neu rendern, damit die Änderung sichtbar wird
                  renderSupervisorCalendar(draft);
                });
                
                shiftContainer.appendChild(optionBtn);
                shiftsContainer.appendChild(shiftContainer);
              }
            });
            
            dayCell.appendChild(shiftsContainer);
          } else {
            // Für Tage, die nicht im Draft existieren, zeige trotzdem die möglichen Schichten an
            var shiftsContainer = document.createElement("div");
            shiftsContainer.className = "shifts-container";
            
            // Definiere die Reihenfolge der Schichten
            var orderedShifts = ["mittags", "nachmittags", "abends"];
            
            // Für jede Schicht in der definierten Reihenfolge
            orderedShifts.forEach(function(shiftName) {
              // Schicht existiert noch nicht, füge sie als gestrichelte Option hinzu
              var shiftContainer = document.createElement("div");
              shiftContainer.className = "shift-container dashed";
              
              var optionBtn = document.createElement("button");
              optionBtn.setAttribute("type", "button");
              optionBtn.className = "shift-btn dashed disabled";
              optionBtn.textContent = shiftName;
              optionBtn.dataset.day = dateStr;
              optionBtn.dataset.shift = shiftName;
              
              shiftContainer.appendChild(optionBtn);
              shiftsContainer.appendChild(shiftContainer);
            });
            
            dayCell.appendChild(shiftsContainer);
          }
          
          weekRow.appendChild(dayCell);
          
          // Gehe zum nächsten Tag
          currentDate.setDate(currentDate.getDate() + 1);
        }
        
        calendarDiv.appendChild(weekRow);
        
        // Wenn wir den letzten Tag des Monats überschritten haben und die Woche beendet ist,
        // können wir aufhören (es sei denn, wir sind noch in der ersten Woche des nächsten Monats)
        if (currentDate > lastDayOfMonth && currentDate.getDay() === 0) {
          break;
        }
      }
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
      
      calendarDiv.appendChild(table);
    };
  
    window.saveEmployeeAvailability = function() {
      var dataField = document.getElementById("employee_data");
      dataField.value = JSON.stringify(window.employeeAvailability);
      document.getElementById("employeeForm").submit();
    };
  
  })();
  