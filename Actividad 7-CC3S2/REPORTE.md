# Actividad 6

## Ejercicios guiados

### Parte 1

#### Evitar o no `-ff`

- Evitaría `-ff` cuando necesito una clara trazabilidad en mi historial de commits. Sin esto, no habría un commit específico y no se podrían seguir claramente las fusiones en el historial.

#### Trabajo en equipo con `--no-ff`

- Se ve una mejor agrupación, en especial en la salida de `git log --graph`, por ejemplo, en donde se muestran los commit explícitos de fusión. Este commit, además, puede incluir más información de contexto que un merge fast foward.
- Sin embargo, un problema fácil de encontrar viene con el exceso de commits de fusión, en especial cuando se trabajan con múltiples ramas con un equipo ampliado.

#### Squash con muchos commits

- Es conviente usar `--squash` cuando se tienen múltiples commits WIP o innecesarios. De igual modo, antes de integrar una rama con la rama principal, es preferente limpiar commits intermedios sin mucho sentido ni contexto.
- Sin embargo, también se podría perder información importante si no es manejada con cuidado. Algunos datos que se pierden también pueden ser los autores de los commits

### Conflictos

#### ¿Qué pasos adicionales hiciste para resolverlo?

- No eran necesarios pasos adicionales, con solo eliminar los indicadores de conflicto ya se pudo fusionar.

#### ¿Qué prácticas (convenciones, PRs pequeñas, tests) lo evitarían?

- Principalmente, hacer PRs pequeños y en varios puntos del desarrollo en lugar de hacer un PR grande al final del desarrollo. De esta forma, los conflictos son mucho más pequeños o directamente no hay conflictos.

### Historiales

#### ¿Cómo se ve el DAG en cada caso?

- En el primer caso, solo se ve la primera línea de cada commit y el recorrido siguiendo el primer padre de cada commits. En el segundo caso, solo se muestran los commits de tipo merge. En el último, se muestra toda la historia con todas las referencias. Es decir, todas las ramas, todos los commits y todos los merges.
- Para equipos pequeños, puede resultar más conveniente hacer merges fast forward junto a squashes constantes. Para ver el grafo, puede convenir el primer método, ya que muestra la información necesaria siguiendo solo al primer padre.
- Para equipos grandes, se pueden requerer merges no fast forward para características importantes y squashes muy selectivos. En estos casos, solo puede requerirse ver los merges en la rama principal para entender el progreso del código.
- Para equipos con auditoría estricta, se tiene que tener un registro de todos los cambios, por lo que nunca se usan merges con fast forward y tampoco squashes. En este caso, se tiene que analizar todo el grafo completo.

### `git revert`

#### ¿Cuándo usar `git revert` en vez de `git reset`?

- Uso `git revert` cuando necesite rehacer cambios sin modificar el historial, la alternativa `reset` es útil cuando no importa modificar el historial.
- En un historial público es preferible hacer `revert` para mantener un historial limpio. Si es que se hace `reset` y se intenta empujar el progreso a remoto, se encontrarán conflictos de contenido diferente.

