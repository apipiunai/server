from flask import Flask, jsonify, request, send_file, after_this_request, render_template
import os
from flask_cors import CORS 
from supabase import create_client, Client

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



@app.route('/')
def home():
    return {"status": "conectado", "mensaje": "Servicio activo"}



# ==========================================
# USUARIOS / AUTENTICACIÓN
# ==========================================

@app.route('/venus/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        response = supabase.table("usuarios") \
            .select("*") \
            .match({"username": username, "password": password}) \
            .execute()

        if response.data and len(response.data) > 0:
            return jsonify({
                "status": "success",
                "message": "Login correcto",
                "data": response.data[0]
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Usuario o contraseña incorrectos"
            }), 401

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/venus/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
         return jsonify({"status": "error", "message": "Faltan datos (username o password)"}), 400

    user = {
        "username": username,
        "password": password
    }

    try:
        response = supabase.table("usuarios").insert(user).execute()
        return jsonify({"status": "success", "message": "Usuario registrado correctamente", "data": response.data}), 201

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
            return jsonify({"status": "success", "data": response.data[0]}), 200
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
            return jsonify({"status": "success", "data": response.data[0]}), 200
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





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
