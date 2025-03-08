import json
from datetime import datetime, timedelta

def shift_cost(shift_type, role):
    """
    Berechnet die Schichtdauer basierend auf einem Mapping:
      - normal: Vorführer = 3 Std, Bistro = 2 Std.
      - sv: Bistro = 5 Std.
    """
    kosten = {
        "normal": {"Vorfuehrer": 3, "Bistro": 2},
        "sv": {"Bistro": 5}
    }
    return kosten.get(shift_type, {}).get(role, 0)

def is_weekend(date_str):
    """Prüft, ob ein Datum (Format YYYY-MM-DD) ein Wochenendtag ist."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.weekday() >= 5  # Samstag (5) oder Sonntag (6)

def generate_initial_plan(draft_path, max_iterations=10):
    """
    Liest den Draft aus der JSON-Datei unter draft_path ein und erzeugt
    einen initialen, fairen Schichtplan.
    
    Fairheit bedeutet, dass unter Berücksichtigung der Verfügbarkeiten
    die Gesamtstunden möglichst gleich verteilt werden (d.h. die Standardabweichung
    der Stunden soll möglichst klein sein).
    
    Vorgaben:
      - Bei normalen Schichten: genau 1 Vorführer und 2 Bistro-Mitarbeiter.
      - Bei sv-Schichten: nur Mitarbeiter mit Bistro-Rolle (2 pro Schicht).
      - Zusatzvorgabe für Wochenendtage: An jedem Wochenendtag soll, falls möglich,
        über alle aktiven Schichten hinweg ein konsistenter Team-Stack (d.h. dieselben
        Personen pro Rolle) eingesetzt werden. Nur wenn für einen Rolleneinsatz kein
        konsistenter Stack gefunden werden kann, erfolgt die Zuweisung schichtweise auf
        Fairnessbasis.
      - Eine Person darf in einem Shift nicht mehrfach eingesetzt werden.
    """
    print("[INFO] Lade Draft von:", draft_path)
    with open(draft_path, 'r') as f:
        draft = json.load(f)
    print("[INFO] Draft geladen.")

    days = draft.get("days", {})
    plan = {"assignments": {}, "total_hours": {}}

    # Alle beteiligten Personen ermitteln
    all_persons = set()
    for day, info in days.items():
        for avail in info.get("availability", []):
            all_persons.add(avail["name"])
    plan["total_hours"] = {person: 0 for person in all_persons}

    sorted_days = sorted(days.keys())
    for date in sorted_days:
        day_info = days[date]
        plan["assignments"][date] = {}
        shifts = day_info.get("shifts", {})
        availability = day_info.get("availability", [])
        # Schneller Lookup: name -> Verfügbarkeitsinfo
        day_avail = { person["name"]: person for person in availability }

        # Prüfe, ob der Tag ein Wochenendtag ist
        weekend_day = is_weekend(date)

        # Falls Wochenendtag: Versuche für jede Rolle über alle aktiven Schichten hinweg
        # einen konsistenten Team-Stack zu ermitteln.
        consistent_team = {}  # z.B. "Vorfuehrer": [<Name>] oder "Bistro": [<Name1>, <Name2>]
        if weekend_day:
            # Ermittlung, welche Rollen an diesem Tag benötigt werden und in welchem Umfang.
            roles_needed = {}  # role -> max. benötigte Anzahl (über alle Schichten)
            for shift_name, shift_info in shifts.items():
                if not shift_info.get("active", False):
                    continue
                shift_type = shift_info.get("type", "normal")
                if shift_type == "normal":
                    req = {"Vorfuehrer": 1, "Bistro": 2}
                elif shift_type == "sv":
                    req = {"Bistro": 2}
                else:
                    req = {}
                for role, count in req.items():
                    roles_needed[role] = max(roles_needed.get(role, 0), count)
            # Für jede benötigte Rolle: Ermittle Kandidat:innen, die in jeder aktiven Schicht
            # (bei der diese Rolle gefordert ist) verfügbar und qualifiziert sind.
            for role, req_count in roles_needed.items():
                common_candidates = []
                for person in availability:
                    if role not in person.get("roles", []):
                        continue
                    # Der Kandidat muss in allen aktiven Schichten, in denen diese Rolle benötigt wird,
                    # in seiner Liste der "available_shifts" stehen.
                    ok = True
                    for shift_name, shift_info in shifts.items():
                        if not shift_info.get("active", False):
                            continue
                        if shift_name not in person.get("available_shifts", []):
                            ok = False
                            break
                    if ok:
                        common_candidates.append(person["name"])
                # Falls genügend Kandidat:innen vorhanden sind, wähle die mit den wenigsten Stunden.
                if len(common_candidates) >= req_count:
                    sorted_common = sorted(common_candidates, key=lambda n: plan["total_hours"].get(n, 0))
                    consistent_team[role] = sorted_common[:req_count]
                else:
                    consistent_team[role] = None  # Kein konsistenter Stack möglich für diese Rolle

        # Bearbeite alle Schichten des Tages (jeweils pro Schicht wird der Plan gefüllt)
        for shift_name, shift_info in shifts.items():
            if not shift_info.get("active", False):
                continue
            shift_type = shift_info.get("type", "normal")
            plan["assignments"][date].setdefault(shift_name, {})
            if shift_type == "normal":
                required = {"Vorfuehrer": 1, "Bistro": 2}
            elif shift_type == "sv":
                required = {"Bistro": 2}
            else:
                required = {}
            # Initialisiere die Zuweisungen
            for role in required:
                if role == "Bistro":
                    plan["assignments"][date][shift_name][role] = []
                else:
                    plan["assignments"][date][shift_name][role] = ""
            
            # Hier wird festgehalten, welche Personen in diesem Shift bereits zugewiesen wurden,
            # um Dopplungen zu vermeiden.
            assigned_in_shift = set()
            
            # Für jede geforderte Rolle die Kandidat:innen auswählen
            for role, count in required.items():
                selected = []
                # Falls Wochenendtag und konsistentes Team vorhanden, versuche zuerst,
                # die Personen zu verwenden, sofern sie noch nicht in einem anderen Rolleneinsatz in diesem Shift sind.
                if weekend_day and consistent_team.get(role) is not None:
                    filtered = [p for p in consistent_team[role] if p not in assigned_in_shift]
                    if len(filtered) >= count:
                        selected = filtered[:count]
                    else:
                        selected = filtered.copy()
                # Falls noch nicht genügend Personen vorhanden, ergänze auf Fairnessbasis.
                while len(selected) < count:
                    eligible = []
                    for name, cand_info in day_avail.items():
                        if name in assigned_in_shift or name in selected:
                            continue
                        if role not in cand_info.get("roles", []):
                            continue
                        if shift_name not in cand_info.get("available_shifts", []):
                            continue
                        eligible.append(name)
                    if not eligible:
                        break
                    eligible_sorted = sorted(eligible, key=lambda n: plan["total_hours"].get(n, 0))
                    chosen = eligible_sorted[0]
                    selected.append(chosen)
                    assigned_in_shift.add(chosen)
                # Aktualisiere die Zuweisung und die Gesamtstunden.
                if role == "Bistro":
                    plan["assignments"][date][shift_name][role] = selected
                else:
                    plan["assignments"][date][shift_name][role] = selected[0] if selected else ""
                for candidate in selected:
                    assigned_in_shift.add(candidate)
                    plan["total_hours"][candidate] += shift_cost(shift_type, role)
    
    return plan["assignments"], plan["total_hours"], draft

# Beispielaufruf:
# plan, total_hours, draft = generate_initial_plan("pfad_zum_draft.json")
# print(json.dumps(plan, indent=2, ensure_ascii=False))
