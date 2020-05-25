import dockerfile_api, filecmp, os, pprint, shutil, sys

from yamlreader import yaml_load

def package_data(filename):
  return os.path.join(os.path.split(__file__)[0], os.path.join("data", filename))

def copy_package_data(filename):
  if not os.path.exists(".buildpacks"):
    os.makedirs(".buildpacks")
  source = package_data(filename)
  if not os.path.exists(os.path.join(".buildpacks", filename)) or not filecmp.cmp(source, os.path.join(".buildpacks", filename)):
    shutil.copy2(package_data(filename), ".buildpacks")

def base_image(language):
  if language == "scala":
    return dockerfile_api.command_from("adoptopenjdk/openjdk11:jre-11.0.7_10-alpine")
  else:
    print("Unsupported language")
    sys.exit(-1)

def install_system_components(components):
  return dockerfile_api.command_run(f'apk update && apk upgrade && apk add --no-cache {" ".join(components)}')

def create_unprivileged_user():
  commands = []
  commands.append(dockerfile_api.command_run("""addgroup -g 1000 buildpacks &&
    adduser -D -u 1000 -G buildpacks buildpacks"""))
  commands.append(dockerfile_api.command_user("buildpacks"))
  commands.append(dockerfile_api.command_workdir("/home/buildpacks"))
  return commands

def jvm_agents(agents):
  commands = []  
  entrypoint_args = ""
  for agent in agents:
    commands.append(dockerfile_api.command_run(f'curl -sLo {agent}.jar "{agents[agent]["url"]}"'))
    entrypoint_arg = f'-javaagent:{agent}.jar'
    if "parameters" in agents[agent] and agents[agent]["parameters"] != None:
      entrypoint_arg = f'{entrypoint_arg}={agents[agent]["parameters"]} '
    entrypoint_args = f"{entrypoint_args} {entrypoint_arg}"
  commands.append(dockerfile_api.command_env("ENTRYPOINT_ARGS", entrypoint_args))

  return commands

def is_jvm(language):
  return language == "java" or language == "scala"

def add_entrypoint(language):
  commands = []
  if language == "scala":
    copy_package_data("scala-entrypoint.sh")
    commands.append(dockerfile_api.command_copy(os.path.join(".buildpacks", "scala-entrypoint.sh"), "entrypoint.sh"))
    commands.append(dockerfile_api.command_entrypoint("/home/buildpacks/entrypoint.sh"))
    return commands
  else:
    print(f"Unsupported language: {language}")
    sys.exit(-1)

def usage():
  print("Usage:")
  print("  buildpacks my-service.yaml")

def main():
  if len(sys.argv) < 2:
    usage()
    sys.exit(-1)

  commands = []

  print(f"Loading {sys.argv[1]}")
  service = yaml_load(sys.argv[1])
  language = service["language"]

  print(f"Merging {language}.yaml")
  base_yaml = yaml_load(f'{package_data(language)}.yaml')
  service = yaml_load(sys.argv[1], base_yaml)

  print("Result:")
  pprint.PrettyPrinter(indent=2).pprint(service)

  components = service["components"]

  commands.append(base_image(language))
  commands.append(install_system_components(components))

  commands.extend(create_unprivileged_user())

  if is_jvm(language):
    agents = service["agents"]
    commands.extend(jvm_agents(agents))

  commands.extend(add_entrypoint(language))

  dockerfile_api.write("Dockerfile", commands)
  print("Dockerfile written!")
