# AGENTS.md

Este repositorio sigue GitHub Flow. Las reglas aplican a todos los laboratorios y al proyecto final, con o sin agentes de IA.

## Flujo de trabajo

1. **main está protegida.** Nadie hace push directo a `main`: ni estudiantes ni un agente. Todo lo que llega a `main` pasa por un pull request. `git push origin main` se rechaza.
2. **Una rama por tarea.** Un laboratorio, una funcionalidad o una corrección: una rama. Nombres cortos y descriptivos (`lab1/ana-perez`, `fix/fecha-vacia`, `docs/agente`).
3. **Todo entra por pull request.** En los labs en parejas, el compañero revisa antes del merge. En el proyecto final, revisa el mantenedor. Abrir el PR con `gh pr create --fill`.
4. **Ramas cortas, y se borran.** Se integran en días, no en semanas. Una rama con más de una semana de vida es una señal de alerta: dividirla. Después del merge: `git branch -d feature/login`.
5. **Mensajes según las reglas del curso.** Imperativo, ≤ 50 caracteres en el subject, cuerpo con el qué y el porqué. Prefijo Conventional Commits.
6. **El pipeline decide.** Si las pruebas fallan, el PR no se puede mezclar. La revisión humana mira el diseño; la máquina mira que no se rompa nada.

## Commits

Formato:

```
tipo: descripción en imperativo

Cuerpo con el qué y el porqué.
```

- Subject ≤ 50 caracteres, sin punto final
- Imperativo: "agregar", no "agregado" ni "agrega"
- Prefijo Conventional Commits: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

Ejemplo:

```
feat: agregar validación de fecha

Validar el campo vacío para evitar envíos incompletos.
```

## Qué no hacer

- No hacer push a `main`
- No mezclar varias tareas en una misma rama
- No dejar ramas vivas más de una semana
- No fusionar un PR si el pipeline falla (desde Semana 6)
