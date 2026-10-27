# LAB-05: Terraform en Google Cloud

## Evidencia
| Lab | Puntaje | Captura | Carpeta |
|-----|---------|---------|---------|
| GSP233 | 100/100 | evidencia/gsp233.png | 01-gsp233/ |
| GSP497 | 100/100 | evidencia/gsp497.png | 02-gsp497/ |
| GSP345 | 100/100 | evidencia/gsp345.png | 03-gsp345/ |
## Bitácora
### GSP233
IP externa del Service y el curl: [http://35.232.190.93/](http://35.232.190.93/)
 
**Qué hice.** Seguí las instrucciones del lab paso a paso hasta desplegar el Service y comprobar con `curl` que respondía en su IP externa.
 
**Qué me costó.** Nada en particular; al ser un lab guiado, los pasos funcionaron tal como estaban descritos.
 
**Qué cambiaría.** Nada en el procedimiento. Lo aprovecharía más leyendo cada archivo `.tf` antes de aplicarlo, en lugar de solo ejecutar los comandos.
### GSP497
**Qué hice.** Seguí las instrucciones del lab paso a paso hasta completar todas las tareas.
 
**Qué me costó.** Nada en particular; al ser un lab guiado, los pasos funcionaron tal como estaban descritos.
 
**Qué cambiaría.** Nada en el procedimiento. Lo aprovecharía más leyendo cada archivo `.tf` antes de aplicarlo, en lugar de solo ejecutar los comandos.
### GSP345
**Qué hice.** Armé la estructura raíz con dos módulos propios (`instances` y `storage`), en la región `us-west4` y zona `us-west4-c`. Luego hice estos pasos:
 
- Importé `tf-instance-1` y `tf-instance-2`, que habían sido creadas a mano. `plan-2.txt` quedó en `0 to add, 2 to change, 0 to destroy`, sin `forces replacement`.
- Creé el bucket `tf-bucket-471675` y migré el estado a un backend `gcs` con prefijo `terraform/state`.
- Subí las instancias a `e2-standard-2`, creé y luego destruí `tf-instance-481965`.
- Desplegué la VPC `tf-vpc-283221` con el módulo `terraform-google-modules/network/google` 10.0.0, con dos subredes, y conecté cada instancia a la suya.
- Creé el firewall `tf-firewall` (TCP 80 desde `0.0.0.0/0`).
Guardé un `plan-<n>.txt` por tarea. Al final, `plan-final.txt` da `No changes` y `state-list.txt` lista los 7 recursos.
 
**Qué me costó.**
 
- **Los valores del lab:** cada instancia del lab trae su propia zona, bucket, VPC y nombre de tercera instancia. Al principio usé los de otra instancia, así que el import fallaba (`Cannot import non-existent remote object`) y los checks de las tareas 3 a 6 no se marcaban.
- **Renombrar el bucket:** el estado vivía dentro del bucket que había que reemplazar. Tuve que devolverlo a local con `terraform init -migrate-state`, cambiar el bucket y volver a migrarlo.
- **Cambiar de VPC:** la VPC vieja no se podía borrar mientras las instancias la usaban. Primero las moví a `default`, y descubrí que también había que poner `subnetwork = "default"`, porque si no el provider mantenía la subred vieja. Las instancias quedaron en `TERMINATED` y tuve que arrancarlas.
- **El firewall:** en una de las correcciones reescribí `main.tf` sin el firewall y el `apply` lo destruyó. Lo noté porque no estaba en `terraform state list` y lo volví a crear.
**Qué cambiaría.**
 
- Copiar todos los valores del panel del lab a un archivo antes de escribir una sola línea, y comprobar la zona real con `gcloud compute instances list`.
- Leer siempre el plan antes de aplicar, buscando `destroy` y `forces replacement`, en lugar de usar `-auto-approve` directamente.
- Editar los `.tf` en lugar de reescribirlos completos.
- Hacer un `git commit` al terminar cada tarea, para que cada `plan-<n>.txt` quede ligado a la versión exacta de los `.tf` que lo produjo.
- Usar referencias (`module.vpc.network_self_link`) en vez de nombres escritos a mano, para que Terraform conozca las dependencias entre recursos.
- 
## Uso de IA

Usé Claude como asistente durante el GSP345.

- **Qué le pedí:** una guía de pasos para el challenge lab, y ayuda para interpretar cada error que me salía en Cloud Shell (pegando la salida completa).
- **Qué me dio:** los comandos y archivos `.tf` para cada tarea, la forma de generar los `plan-<n>.txt` y verificarlos con `grep`, y explicaciones sobre el import y la migración del backend.
- **Qué corregí:**
  - La primera guía usaba valores de otra instancia del lab (zona `us-west4-b`, bucket, VPC y tercera instancia con otros nombres). Tuve que comprobar los valores reales en mi panel y en `gcloud` y adaptarlos.
  - Un `main.tf` que me propuso para corregir el backend omitía el módulo `vpc` y el firewall. El `apply` destruyó el firewall. Lo detecté revisando la salida del plan y el `state list`, y lo recuperé.
  - Pegué literalmente un placeholder (`<TU_PROJECT_ID>`) que había que reemplazar.
- **Lo que aprendí de esto:** leer siempre el plan antes de aplicar (buscar `destroy` y `forces replacement`), y no confiar en que una configuración generada coincide con mi entorno sin verificarla.
