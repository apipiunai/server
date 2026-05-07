from flask import Flask, jsonify, request
import os
from flask_cors import CORS 
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})





SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



@app.route('/')
def home():
    return {"status": "conectado", "mensaje": "Servicio activo 07-06-2024"}, 200



# ==========================================
# USUARIOS / AUTENTICACIÓN
# ==========================================

def sanitize_user(user):
    if not isinstance(user, dict):
        return user
    sanitized = dict(user)
    sanitized.pop("password", None)
    return sanitized

@app.route('/venus/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "Faltan datos (email o password)"}), 400

    try:
        response = supabase.table("usuarios") \
            .select("*") \
            .eq("email", email) \
            .execute()

        if not response.data or len(response.data) == 0:
            return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401

        user = response.data[0]
        stored_password = user.get("password")

        if not stored_password or not check_password_hash(stored_password, password):
            return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401

        return jsonify({
            "status": "success",
            "message": "Login correcto",
            "data": sanitize_user(user)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password:
         return jsonify({"status": "error", "message": "Faltan datos (username o password)"}), 400

    hashed_password = generate_password_hash(password)
    user = {
        "username": username,
        "password": hashed_password,
        "email": email,
    }

    try:
        response = supabase.table("usuarios").insert(user).execute()
        inserted = response.data[0] if response.data else {}
        return jsonify({"status": "success", "message": "Usuario registrado correctamente", "data": sanitize_user(inserted)}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/getUser', methods=['POST'])
def getUser():
    data = request.get_json()
    id_buscado = data.get("id")

    if not id_buscado:
        return jsonify({"status": "error", "message": "Falta el id del usuario"}), 400

    try:
        response = supabase.table("usuarios").select("*").eq("id", id_buscado).execute()
        
        if response.data:
            return jsonify({"status": "success", "data": sanitize_user(response.data[0])}), 200
        else:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
            
    except Exception as e:
         return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/checkUser', methods=['POST'])
def checkUser():
    data = request.get_json()
    id_buscado = data.get("id")
    username = data.get("username")

    try:
        response = supabase.table("usuarios") \
            .select("*") \
            .eq("id", id_buscado) \
            .eq("username", username) \
            .execute()
        
        if response.data:
            return jsonify({"status": "success", "data": sanitize_user(response.data[0])}), 200
        else:
            return jsonify({"status": "error", "message": "Credenciales no válidas"}), 404
            
    except Exception as e:
         return jsonify({"status": "error", "message": str(e)}), 400



@app.route('/venus/addEjercicio', methods=['POST'])
def addEjercicio():
    data = request.get_json()
    user_id = data.get("user_id") 
    ejercicios = data.get("ejercicios") 

    try:
        # Change "users" to "usuarios"
        response = supabase.table("usuarios").update({
            "ejercicios": ejercicios 
        }).eq("id", user_id).execute()

        return jsonify({
            "status": "success", 
            "message": "Lista de ejercicios actualizada", 
            "data": response.data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/editProfile', methods=['POST'])
def editProfile():
    data = request.get_json()
  
    id_buscado = data.pop("id", None) 
    
    if not id_buscado:
        return jsonify({"status": "error", "message": "Falta el ID del usuario"}), 400

    try:
        response = supabase.table("usuarios").update(data).eq("id", id_buscado).execute()
        
        if not response.data:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

        return jsonify({
            "status": "success", 
            "message": "Perfil actualizado correctamente", 
            "data": response.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400



@app.route('/venus/clearEjercicio', methods=['POST'])
def clearEjercicio():
    data = request.get_json()
    user_id = data.get("user_id") 
    ejercicios = data.get("ejercicios") 

    try:
        # Change "users" to "usuarios"
        response = supabase.table("usuarios").update({
            "ejercicios": ejercicios 
        }).eq("id", user_id).execute()

        return jsonify({
            "status": "success", 
            "message": "Lista de ejercicios actualizada", 
            "data": response.data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/clearLesion', methods=['POST'])
def clearLesion():
    data = request.get_json()
    user_id = data.get("user_id") 
    lesiones = data.get("lesiones") 

    try:
        # Change "users" to "usuarios"
        response = supabase.table("usuarios").update({
            "lesiones": lesiones 
        }).eq("id", user_id).execute()

        return jsonify({
            "status": "success", 
            "message": "Lista de lesiones actualizada", 
            "data": response.data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/addLesion', methods=['POST'])
def addLesion():
    data = request.get_json()
    user_id = data.get("user_id") 
    lesiones = data.get("lesiones") 

    try:
        # Change "users" to "usuarios"
        response = supabase.table("usuarios").update({
            "lesiones": lesiones 
        }).eq("id", user_id).execute()

        return jsonify({
            "status": "success", 
            "message": "Lista de lesiones actualizada", 
            "data": response.data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ==========================================
# EJERCICIOS
# ==========================================

@app.route('/venus/getEjercicios', methods=['POST'])
def getEjercicios():
    data = request.get_json()
    id_usuario = data.get("id_usuario")

    if not id_usuario:
        return jsonify({"status": "error", "message": "Falta el id_usuario"}), 400

    try:
        response = supabase.table("ejercicios").select("*").eq("id_usuario", id_usuario).execute()
        return jsonify({"status": "success", "message": "Ejercicios obtenidos", "data": response.data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/insertEjercicio', methods=['POST'])
def insertEjercicio():
    data = request.get_json()
    
    try:
        response = supabase.table("ejercicios").insert(data).execute()
        return jsonify({"status": "success", "message": "Ejercicio insertado", "data": response.data}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400




@app.route('/venus/updateEjercicio', methods=['POST'])
def updateEjercicio():
    data = request.get_json()
    ejercicio_id = data.get("id")
    try:
        response = supabase.table("ejercicios").update(data).eq("id", ejercicio_id).execute()
        return jsonify({"status": "success", "message": "Ejercicio actualizado", "data": response.data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/deleteEjercicio', methods=['POST'])
def deleteEjercicio():
    data = request.get_json()
    ejercicio_id = data.get("id")

    try:
        response = supabase.table("ejercicios").delete().eq("id", ejercicio_id).execute()
        return jsonify({"status": "success", "message": "Ejercicio eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ==========================================
# DIETAS
# ==========================================

@app.route('/venus/getDietas', methods=['POST'])
def getDietas():
    data = request.get_json()
    id_usuario = data.get("id_usuario")

    if not id_usuario:
        return jsonify({"status": "error", "message": "Falta el id_usuario"}), 400

    try:
        response = supabase.table("dietas").select("*").eq("id_usuario", id_usuario).execute()
        return jsonify({"status": "success", "message": "Dietas obtenidas", "data": response.data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/insertDieta', methods=['POST'])
def insertDieta():
    data = request.get_json()
    
    try:
        response = supabase.table("dietas").insert(data).execute()
        return jsonify({"status": "success", "message": "Dieta insertada", "data": response.data}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400



@app.route('/venus/updateDieta', methods=['POST'])
def updateDieta():
    data = request.get_json()
    dieta_id = data.get("id")
    try:
        response = supabase.table("dietas").update(data).eq("id", dieta_id).execute()
        return jsonify({"status": "success", "message": "Dieta actualizada", "data": response.data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/deleteDieta', methods=['POST'])
def deleteDieta():
    data = request.get_json()
    dieta_id = data.get("id")

    try:
        response = supabase.table("dietas").delete().eq("id", dieta_id).execute()
        return jsonify({"status": "success", "message": "Dieta eliminada correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400




# ==========================================
# COACH
# ==========================================




@app.route('/venus/getAlumnos', methods=['POST'])
def getAlumnos():
    data = request.get_json()  
    coach_id = data.get("coach_id")

    if not coach_id:
        return jsonify({"status": "error", "message": "Falta el ID del coach"}), 400

    try:
        response = supabase.table("alumno_coach") \
            .select("email_alumno") \
            .eq("id_coach", coach_id) \
            .execute()

        alumno_emails = [item["email_alumno"] for item in response.data]
        
        if not alumno_emails:
            return jsonify({
                "status": "success", 
                "message": "No se encontraron alumnos", 
                "data": []
            }), 200
        
        alumnos_response = supabase.table("usuarios") \
            .select("*") \
            .in_("email", alumno_emails) \
            .execute()

        alumnos = [sanitize_user(item) for item in alumnos_response.data or []]
        
        # Respuesta exitosa
        return jsonify({
            "status": "success", 
            "message": f"Se encontraron {len(alumnos)} alumnos", 
            "data": alumnos
        }), 200

    except Exception as e:
        # Captura de errores (Base de datos, conexión, etc.)
        return jsonify({
            "status": "error", 
            "message": f"Error en el servidor: {str(e)}"
        }), 500
    

@app.route('/venus/deleteAlumno', methods=['POST'])
def deleteAlumno():
    data = request.get_json()
    id_coach = data.get("id_coach")
    email_alumno = data.get("email_alumno")

    print("ID Coach:", id_coach)
    print("Email Alumno:", email_alumno)
    
    try:
        response = supabase.table("alumno_coach").delete()\
            .eq("id_coach", id_coach)\
            .eq("email_alumno", email_alumno)\
            .execute()
        return jsonify({"status": "success", "message": "Alumno eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/getAlumno', methods=['POST'])
def getAlumno():
    data = request.get_json()
    email_alumno = data.get("email_alumno")

    if not email_alumno:
        return jsonify({"status": "error", "message": "Falta el email_alumno"}), 400

    try:
        response = supabase.table("usuarios").select("*").eq("email", email_alumno).execute()
        alumno = response.data[0] if response.data else None
        return jsonify({"status": "success", "message": "Alumno obtenido", "data": sanitize_user(alumno) if alumno else None}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400



@app.route('/venus/invitarAlumno', methods=['POST'])
def invitarAlumno():
    data = request.get_json()
    id_coach = data.get("id_coach")
    email = data.get("email")

    if not email:
         return jsonify({"status": "error", "message": "Falta el email"}), 400



    try:

        already_invited = supabase.table("invitaciones").select("*").eq("email_alumno", email).eq("id_coach", id_coach).execute()

        if already_invited.data:
            return jsonify({"status": "error", "message": "El alumno ya ha sido invitado por este coach"}), 400
        
        already_coached = supabase.table("alumno_coach").select("*").eq("email_alumno", email).eq("id_coach", id_coach).execute()
        
        if already_coached.data:
            return jsonify({"status": "error", "message": "Ya es alumno de este coach"}), 400
        
        existing_user = supabase.table("usuarios").select("*").eq("email", email).execute()

        if not existing_user.data:
            return jsonify({"status": "error", "message": "No existe un usuario registrado con ese email"}), 400

        response = supabase.table("invitaciones").insert({"id_coach": id_coach, "email_alumno": email}).execute()
        inserted = response.data[0] if response.data else {}
        return jsonify({"status": "success", "message": "Alumno invitado correctamente", "data": sanitize_user(inserted)}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/aceptarInvitacion', methods=['POST'])
def aceptarInvitacion():
    data = request.get_json()
    id_coach = data.get("id_coach")
    email_alumno = data.get("email_alumno")

    if not email_alumno:
         return jsonify({"status": "error", "message": "Falta el email_alumno"}), 400

    try:

        response = supabase.table("alumno_coach").insert({"id_coach": id_coach, "email_alumno": email_alumno}).execute()
        inserted = response.data[0] if response.data else {}

        if(inserted):
            supabase.table("invitaciones").delete()\
                .eq("id_coach", id_coach)\
                .eq("email_alumno", email_alumno)\
                .execute()
        


        return jsonify({"status": "success", "message": "Relacion coach alumno aceptada correctamente", "data": inserted}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


    
@app.route('/venus/getInvitaciones', methods=['POST'])
def get_invitaciones():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"status": "error", "message": "Falta el email"}), 400

    try:
        invitations = supabase.table("invitaciones") \
            .select("*") \
            .eq("email_alumno", email) \
            .execute()

        if not invitations.data:
            return jsonify({"status": "success", "data": []}), 200

        result = []
        for invitation in invitations.data:
            coach_response = supabase.table("usuarios") \
                .select("email") \
                .eq("id", invitation.get("id_coach")) \
                .execute()
            
            if coach_response.data:
                result.append({
                    "id_invitacion": invitation.get("id_invitacion"),
                    "id_coach": invitation.get("id_coach"),
                    "coach_email": coach_response.data[0].get("email"),
                })

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
