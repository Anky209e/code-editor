from flask import Flask, request, render_template
import docker
import uuid
import os

app = Flask(__name__)
client = docker.from_env()

@app.route("/", methods=["GET"])
def index():
    return render_template("editor.html", code="", output=None)

@app.route("/run", methods=["POST"])
def run_code():
    code = request.form["code"]
    filename = f"/tmp/{uuid.uuid4()}.py"
    with open(filename, "w") as f:
        f.write(code)

    try:
        output = client.containers.run(
            image="python:3.10-slim",
            command=f"python /code/script.py",
            volumes={os.path.dirname(filename): {"bind": "/code", "mode": "ro"}},
            working_dir="/code",
            stderr=True,
            stdout=True,
            remove=True,
            network_disabled=True,
            mem_limit="100m",
            pids_limit=64,
            timeout=5,
        )
        result = output.decode("utf-8")
    except docker.errors.ContainerError as e:
        result = e.stderr.decode("utf-8")
    except Exception as e:
        result = f"Error: {str(e)}"
    finally:
        os.remove(filename)

    return render_template("editor.html", code=code, output=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
