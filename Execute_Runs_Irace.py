import os
import shutil
import subprocess
import concurrent.futures

# Función para ejecutar un escenario de sintonización de hiperparámetros
def execute_scenario(path: str, seed: int, id_scenario: int, train_dir: str, parallel: int = 1):
    """
    Ejecuta un escenario de sintonización de hiperparámetros.

    Args:
        path (str): Ruta del escenario.
        seed (int): Semilla aleatoria.
        id_scenario (int): ID del escenario.
        train_dir (str): Directorio relativo donde se encuentran las instancias.
    """
    scenario_file = os.path.join(path, 'scenario.txt')
    
    with open(scenario_file, 'a') as file:
        file.write("\n## Seed\n")
        file.write(f"seed={seed}\n")
        file.write("\n## Scenario ID\n")
        file.write(f"#id_scenario={id_scenario}\n")
        file.write("\n## Number of threads\n")
        file.write(f"parallel={parallel}\n")

    command = "Rscript execute_irace.R > output.log"
    subprocess.run(command, shell=True, cwd=path)

    print(f"Escenario {id_scenario} terminado: {path}, seed={seed}")

# Directorios de escenarios de base, de destino y nombre de los escenarios
directories = [
#    ['Runs/ACOTSP-N/Base', 'Runs/ACOTSP-N/Run', 'N'],
#    ['Runs/ACOTSP-SR/Base', 'Runs/ACOTSP-SR/Run', 'SR'],
#    ['Runs/MMASQAP-N/Base', 'Runs/MMASQAP-N/Run', 'N'],
#    ['Runs/MMASQAP-SR/Base', 'Runs/MMASQAP-SR/Run', 'SR'],
    ['Runs/PSOX-Mixed-N/Base', 'Runs/PSOX-Mixed-N/Run', 'N'],
]

# Semillas para cada combinación
seeds = [7940, 9411] #, 7175, 9685, 7018, 1569, 128, 5144, 8860, 3764]"""

# Listas para almacenar los datos de cada run
runs_data = []

# Generar combinaciones de escenarios base y semillas
for base_dir, dest_dir, scenary_type in directories:
    # Verificación de existencia de directorio base
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"El directorio base '{base_dir}' no existe.")
    # ID que representa la run para cada combinación de escenario y semilla
    run_id = 1
    # Crear carpetas para cada semilla
    for seed in seeds:
        # Crear carpeta para la combinación de escenario y semilla
        path = os.path.join(dest_dir, f"{scenary_type}_seed_{seed}")
        os.makedirs(path, exist_ok=True)
        shutil.copytree(base_dir, path, dirs_exist_ok=True)
        runs_data.append((path, seed, run_id))
        run_id += 1

# Configuración de paralelismo
N = len(runs_data)  # Total de escenarios a ejecutar
K = 2           # Máximo de ejecuciones simultáneas
parallel = 8    # Número de threads por escenario

print(f"Número total de escenarios (N): {N}\n")
print(f"Número máximo de ejecuciones simultáneas (K): {K}\n")
print(f"Número de threads por escenario: {parallel}\n")

# Ejecutar en paralelo
with concurrent.futures.ThreadPoolExecutor(max_workers=K) as executor:
    futures = {executor.submit(execute_scenario, path, seed, run_id, parallel): [path, seed, run_id] for path, seed, run_id in runs_data}
    print("Ejecutando escenarios...\n")
    for future in concurrent.futures.as_completed(futures):
        path, seed, run_id, _ = futures[future]
        print(f"Escenario {path} completado: seed={seed}, run_id={run_id}\n")
    print("Ejecución de escenarios completada.")
