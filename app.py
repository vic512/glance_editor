from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape
import yaml
import docker
import os

app = Flask(__name__)

# Get the path to the YAML file and Docker container name from environment variables
YAML_FILE = os.getenv('YAML_FILE', '/default/path/to/glance.yml')
DOCKER_CONTAINER_NAME = os.getenv('DOCKER_CONTAINER_NAME')

# Initialize Docker client
client = docker.from_env()

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def write_yaml(file_path, data):
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        yaml_content = request.form['yaml_content']
        try:
            parsed_yaml = yaml.safe_load(yaml_content)
            write_yaml(YAML_FILE, parsed_yaml)
            
            if DOCKER_CONTAINER_NAME:
                container = client.containers.get(DOCKER_CONTAINER_NAME)
                container.restart()

            return redirect(url_for('index'))
        except yaml.YAMLError as e:
            return f"Error parsing YAML: {e}"
    
    yaml_content = read_yaml(YAML_FILE)
    escaped_yaml_content = escape(yaml.dump(yaml_content, default_flow_style=False, sort_keys=False))
    return render_template('index.html', yaml_content=escaped_yaml_content, restart_container=bool(DOCKER_CONTAINER_NAME))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
