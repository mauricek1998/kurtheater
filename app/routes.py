import os
import json
import calendar
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .scheduler import generate_initial_plan
from .auth import verify_password, get_user, load_users, add_user, save_users, hash_password

bp = Blueprint('main', __name__)

# Pfad zum Datenverzeichnis (sicherstellen, dass der Ordner /data existiert)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_password(username, password):
            user = get_user(username)
            login_user(user)
            flash('Erfolgreich angemeldet!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Ungültige Anmeldedaten.', 'error')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('main.login'))

@bp.route('/')
@login_required
def index():
    if current_user.is_supervisor:
        return redirect(url_for('main.supervisor'))
    return redirect(url_for('main.employee_drafts'))

# ==========================
# Supervisor-Bereich
# ==========================

@bp.route('/supervisor', methods=['GET', 'POST'])
@login_required
def supervisor():
    if not current_user.is_supervisor:
        flash('Sie haben keine Berechtigung für diese Seite.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        month = request.form.get('month')
        year = request.form.get('year')
        if not (month and year):
            flash("Bitte Monat und Jahr angeben.", "error")
            return redirect(url_for('main.supervisor'))
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            flash("Ungültige Eingabe.", "error")
            return redirect(url_for('main.supervisor'))
        
        draft = {
            "month": month,
            "year": year,
            "days": {},
            "status": "draft"  # Mögliche Status: draft, open, final
        }
        num_days = calendar.monthrange(year, month)[1]
        for day in range(1, num_days+1):
            date_obj = datetime(year, month, day)
            date_str = date_obj.strftime('%Y-%m-%d')
            weekday = date_obj.weekday()
            if weekday < 5:
                shifts = {
                    "abends": {"active": True, "type": "normal"}
                }
            else:
                shifts = {
                    "mittags": {"active": True, "type": "normal"},
                    "nachmittags": {"active": True, "type": "normal"},
                    "abends": {"active": True, "type": "normal"}
                }
            draft["days"][date_str] = {
                "shifts": shifts,
                "availability": []
            }
        draft_filename = f"draft_{year}-{month:02d}.json"
        draft_path = os.path.join(DATA_DIR, draft_filename)
        with open(draft_path, 'w') as f:
            json.dump(draft, f, indent=4)
        flash(f"Plan für {month}/{year} wurde erstellt.", "success")
        return redirect(url_for('main.supervisor'))
    
    # Lade alle Benutzer
    users_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'users.json')
    with open(users_file, 'r') as f:
        users_data = json.load(f)
    all_users = [
        {"username": username, "name": data["name"]}
        for username, data in users_data["users"].items()
    ]
    
    drafts = []
    open_drafts = []
    final_plans = []
    
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            status = data.get('status', 'draft')
            month = data.get('month')
            year = data.get('year')
            display_name = f"{month}/{year}"
            
            if status == 'draft':
                drafts.append({'filename': filename, 'display_name': display_name})
            elif status == 'open':
                # Sammle Verfügbarkeitsinformationen
                availability_status = {}
                for user in all_users:
                    has_availability = False
                    for day_info in data["days"].values():
                        for avail in day_info.get("availability", []):
                            if avail.get("name") == user["name"]:
                                has_availability = True
                                break
                        if has_availability:
                            break
                    availability_status[user["name"]] = has_availability
                
                open_drafts.append({
                    'filename': filename, 
                    'display_name': display_name,
                    'availability_status': availability_status
                })
            elif status == 'final':
                final_plans.append({'filename': filename, 'display_name': display_name})
    
    return render_template('supervisor.html', 
                         drafts=sorted(drafts, key=lambda x: x['display_name']),
                         open_drafts=sorted(open_drafts, key=lambda x: x['display_name']),
                         final_plans=sorted(final_plans, key=lambda x: x['display_name']),
                         all_users=sorted(all_users, key=lambda x: x["name"]))

@bp.route('/supervisor/release_draft/<draft_filename>', methods=['POST'])
@login_required
def release_draft(draft_filename):
    if not current_user.is_supervisor:
        flash('Sie haben keine Berechtigung für diese Aktion.', 'error')
        return redirect(url_for('main.index'))
    
    draft_path = os.path.join(DATA_DIR, draft_filename)
    if not os.path.exists(draft_path):
        flash("Plan nicht gefunden.", "error")
        return redirect(url_for('main.supervisor'))
    
    with open(draft_path, 'r') as f:
        draft = json.load(f)
    
    draft['status'] = 'open'
    
    with open(draft_path, 'w') as f:
        json.dump(draft, f, indent=4)
    
    flash("Plan wurde für Mitarbeiter freigegeben.", "success")
    return redirect(url_for('main.supervisor'))

@bp.route('/supervisor/create_final_plan/<draft_filename>', methods=['POST'])
@login_required
def create_final_plan(draft_filename):
    if not current_user.is_supervisor:
        flash('Sie haben keine Berechtigung für diese Aktion.', 'error')
        return redirect(url_for('main.index'))
    
    draft_path = os.path.join(DATA_DIR, draft_filename)
    if not os.path.exists(draft_path):
        flash("Plan nicht gefunden.", "error")
        return redirect(url_for('main.supervisor'))
    
    try:
        with open(draft_path, 'r') as f:
            draft = json.load(f)
        
        # Generiere den finalen Plan
        assignments, total_hours, _ = generate_initial_plan(draft_path)
        
        # Aktualisiere den Status und füge die Zuweisungen hinzu
        draft['status'] = 'final'
        draft['assignments'] = assignments
        draft['total_hours'] = total_hours
        
        with open(draft_path, 'w') as f:
            json.dump(draft, f, indent=4)
        
        flash("Finaler Plan wurde erstellt.", "success")
    except Exception as e:
        flash(f"Fehler beim Erstellen des Plans: {str(e)}", "error")
    
    return redirect(url_for('main.supervisor'))

@bp.route('/supervisor/delete_draft/<draft_filename>', methods=['POST'])
@login_required
def delete_draft(draft_filename):
    if not current_user.is_supervisor:
        flash('Sie haben keine Berechtigung für diese Aktion.', 'error')
        return redirect(url_for('main.index'))
    
    draft_path = os.path.join(DATA_DIR, draft_filename)
    if os.path.exists(draft_path):
        os.remove(draft_path)
        flash(f"Plan wurde gelöscht.", "success")
    else:
        flash("Plan nicht gefunden.", "error")
    return redirect(url_for('main.supervisor'))

@bp.route('/supervisor/edit_draft/<draft_filename>', methods=['GET', 'POST'])
@login_required
def edit_draft(draft_filename):
    if not current_user.is_supervisor:
        flash('Sie haben keine Berechtigung für diese Seite.', 'error')
        return redirect(url_for('main.index'))
    
    draft_path = os.path.join(DATA_DIR, draft_filename)
    if not os.path.exists(draft_path):
        flash("Plan nicht gefunden.", "error")
        return redirect(url_for('main.supervisor'))
    
    if request.method == 'POST':
        draft_data = request.form.get('draft_data')
        if draft_data:
            try:
                updated_draft = json.loads(draft_data)
                with open(draft_path, 'w') as f:
                    json.dump(updated_draft, f, indent=4)
                flash("Plan wurde aktualisiert.", "success")
            except Exception as e:
                flash("Fehler beim Aktualisieren des Plans.", "error")
        else:
            flash("Keine Daten zum Speichern erhalten.", "error")
        return redirect(url_for('main.edit_draft', draft_filename=draft_filename))
    
    with open(draft_path, 'r') as f:
        draft = json.load(f)
    return render_template('edit_draft.html', draft=draft, draft_filename=draft_filename)

# ==========================
# Mitarbeiter-Bereich
# ==========================
@bp.route('/employee/drafts')
@login_required
def employee_drafts():
    drafts = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(DATA_DIR, filename), 'r') as f:
                data = json.load(f)
                if data.get('status') in ['open', 'final']:
                    month = data.get('month')
                    year = data.get('year')
                    drafts.append({
                        'filename': filename,
                        'display_name': f"{month}/{year}",
                        'status': data.get('status')
                    })
    return render_template('employee_drafts.html', drafts=drafts)

@bp.route('/employee/draft/<draft_filename>', methods=['GET', 'POST'])
@login_required
def employee_edit(draft_filename):
    draft_path = os.path.join(DATA_DIR, draft_filename)
    if not os.path.exists(draft_path):
        flash("Draft not found.", "error")
        return redirect(url_for('main.employee_drafts'))
    
    if request.method == 'POST':
        employee_data = request.form.get('employee_data')
        try:
            availability = json.loads(employee_data)
        except Exception:
            flash("Error processing availability data.", "error")
            return redirect(url_for('main.employee_edit', draft_filename=draft_filename))
        
        with open(draft_path, 'r') as f:
            draft = json.load(f)
        
        for day in draft["days"]:
            draft["days"][day]["availability"] = [
                avail for avail in draft["days"][day]["availability"]
                if avail.get("name") != current_user.name
            ]
            if day in availability and len(availability[day]) > 0:
                draft["days"][day]["availability"].append({
                    "name": current_user.name,
                    "available_shifts": availability[day],
                    "roles": current_user.roles
                })
        with open(draft_path, 'w') as f:
            json.dump(draft, f, indent=4)
        flash("Availability saved.", "success")
        return redirect(url_for('main.employee_drafts'))
    
    with open(draft_path, 'r') as f:
        draft = json.load(f)
    return render_template('employee_edit.html', draft=draft, draft_filename=draft_filename)

# ==========================
# Finaler Plan anzeigen
# ==========================
@bp.route('/plan_view')
def plan_view():
    plan_filename = request.args.get('plan_filename')
    if not plan_filename:
        flash("Kein Plan ausgewählt.", "error")
        return redirect(url_for('main.plan_list'))
    plan_path = os.path.join(DATA_DIR, plan_filename)
    if not os.path.exists(plan_path):
        flash("Plan nicht gefunden.", "error")
        return redirect(url_for('main.index'))
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    return render_template('plan_view.html', 
                         plan=plan, 
                         is_supervisor=current_user.is_supervisor if current_user.is_authenticated else False)

@bp.route('/update_plan_name', methods=['POST'])
@login_required
def update_plan_name():
    if not current_user.is_supervisor:
        return {"success": False, "error": "Keine Berechtigung"}, 403
    
    data = request.get_json()
    plan_filename = data.get('plan_filename')
    old_name = data.get('old_name')
    new_name = data.get('new_name')
    date = data.get('date')
    shift = data.get('shift')
    role = data.get('role')
    
    if not all([plan_filename, old_name, new_name, date, shift, role]):
        return {"success": False, "error": "Fehlende Parameter"}, 400
    
    plan_path = os.path.join(DATA_DIR, plan_filename)
    if not os.path.exists(plan_path):
        return {"success": False, "error": "Plan nicht gefunden"}, 404
    
    try:
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        # Aktualisiere nur die spezifische Schicht
        if role == 'Vorfuehrer':
            if plan['assignments'][date][shift]['Vorfuehrer'] == old_name:
                plan['assignments'][date][shift]['Vorfuehrer'] = new_name
        elif role == 'Bistro':
            bistro = plan['assignments'][date][shift]['Bistro']
            if isinstance(bistro, list):
                plan['assignments'][date][shift]['Bistro'] = [
                    new_name if name == old_name else name 
                    for name in bistro
                ]
            elif bistro == old_name:
                plan['assignments'][date][shift]['Bistro'] = new_name
        
        # Aktualisiere die Gesamtstunden
        # Berechne die Stunden für diese spezifische Schicht
        shift_type = plan['assignments'][date][shift].get('type', 'normal')
        if role == 'Vorfuehrer':
            hours = 3 if shift_type == 'normal' else 0
        else:  # Bistro
            hours = 2 if shift_type == 'normal' else 5
        
        # Ziehe die Stunden vom alten Namen ab und füge sie dem neuen Namen hinzu
        plan['total_hours'][old_name] = plan['total_hours'].get(old_name, 0) - hours
        plan['total_hours'][new_name] = plan['total_hours'].get(new_name, 0) + hours
        
        # Entferne den alten Namen aus total_hours wenn keine Stunden mehr vorhanden
        if plan['total_hours'][old_name] <= 0:
            del plan['total_hours'][old_name]
        
        with open(plan_path, 'w') as f:
            json.dump(plan, f, indent=4)
        
        return {"success": True}, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@bp.route('/plan_list')
@login_required
def plan_list():
    final_plans = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(DATA_DIR, filename), 'r') as f:
                data = json.load(f)
                if data.get('status') == 'final':
                    month = data.get('month')
                    year = data.get('year')
                    final_plans.append({
                        'filename': filename,
                        'display_name': f"{month}/{year}"
                    })
    return render_template('plan_list.html', plan_files=sorted(final_plans, key=lambda x: x['display_name']))

@bp.route('/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    # Nur Supervisoren dürfen auf die Benutzerverwaltung zugreifen
    if not current_user.is_supervisor:
        flash('Sie haben keine Berechtigung für diese Seite.', 'error')
        return redirect(url_for('main.index'))
    
    users_data = load_users()
    all_users = []
    
    for username, user_data in users_data.items():
        all_users.append({
            'username': username,
            'name': user_data['name'],
            'roles': user_data['roles'],
            'is_supervisor': user_data['is_supervisor']
        })
    
    # Sortiere Benutzer nach Namen
    all_users.sort(key=lambda x: x['name'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Neuen Benutzer anlegen
        if action == 'create':
            username = request.form.get('username')
            name = request.form.get('name')
            password = request.form.get('password')
            roles = request.form.getlist('roles')
            is_supervisor = 'is_supervisor' in request.form
            
            if not username or not name or not password:
                flash('Bitte füllen Sie alle Pflichtfelder aus.', 'error')
            elif username in users_data:
                flash(f'Der Benutzername {username} existiert bereits.', 'error')
            else:
                success, message = add_user(username, password, name, roles, is_supervisor)
                if success:
                    flash(message, 'success')
                    return redirect(url_for('main.user_management'))
                else:
                    flash(message, 'error')
        
        # Benutzer aktualisieren
        elif action == 'update':
            username = request.form.get('username')
            name = request.form.get('name')
            password = request.form.get('password')
            roles = request.form.getlist('roles')
            is_supervisor = 'is_supervisor' in request.form
            
            if username not in users_data:
                flash(f'Der Benutzer {username} existiert nicht.', 'error')
            else:
                users_data[username]['name'] = name
                users_data[username]['roles'] = roles
                users_data[username]['is_supervisor'] = is_supervisor
                
                # Passwort nur aktualisieren, wenn eines eingegeben wurde
                if password:
                    users_data[username]['password'] = hash_password(password)
                
                save_users(users_data)
                flash(f'Benutzer {username} wurde aktualisiert.', 'success')
                return redirect(url_for('main.user_management'))
        
        # Benutzer löschen
        elif action == 'delete':
            username = request.form.get('username')
            
            if username not in users_data:
                flash(f'Der Benutzer {username} existiert nicht.', 'error')
            else:
                del users_data[username]
                save_users(users_data)
                flash(f'Benutzer {username} wurde gelöscht.', 'success')
                return redirect(url_for('main.user_management'))
    
    return render_template('user_management.html', users=all_users)

# API-Route für die automatische Planerstellung
@bp.route('/api/create_all_plans', methods=['POST'])
@login_required
def create_all_plans():
    if not current_user.is_supervisor:
        return jsonify({'success': False, 'error': 'Keine Berechtigung'}), 403
    
    try:
        # Finde alle freigegebenen Pläne
        open_drafts = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.json'):
                draft_path = os.path.join(DATA_DIR, filename)
                try:
                    with open(draft_path, 'r') as f:
                        draft = json.load(f)
                    if draft.get('status') == 'open':
                        open_drafts.append(filename)
                except Exception as e:
                    continue
        
        # Erstelle finale Pläne für alle freigegebenen Entwürfe
        created_plans = []
        for draft_filename in open_drafts:
            draft_path = os.path.join(DATA_DIR, draft_filename)
            try:
                with open(draft_path, 'r') as f:
                    draft = json.load(f)
                
                # Generiere den finalen Plan
                assignments, total_hours, _ = generate_initial_plan(draft_path)
                
                # Aktualisiere den Status und füge die Zuweisungen hinzu
                draft['status'] = 'final'
                draft['assignments'] = assignments
                draft['total_hours'] = total_hours
                draft['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Speichere den finalen Plan
                with open(draft_path, 'w') as f:
                    json.dump(draft, f, indent=4)
                
                created_plans.append(draft_filename)
            except Exception as e:
                continue
        
        return jsonify({
            'success': True, 
            'message': f'{len(created_plans)} Pläne wurden erfolgreich erstellt', 
            'created_plans': created_plans
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
