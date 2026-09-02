"""
Servicio de programa — la capa de NEGOCIO.

Depende solo de la interfaz del repositorio, así que no sabe qué motor hay
detrás: por eso se puede probar sin base de datos.

Comunica los problemas con excepciones, que el controlador traduce a códigos
HTTP. El servicio no sabe qué es un 404, y así debe ser: si lo supiera,
quedaría atado a la web y no podría usarse desde otro sitio.
"""

from repositorios.abstracciones.i_repositorio_programa import IRepositorioPrograma


class ServicioPrograma:
    """Reglas de negocio del CRUD de programa."""

    def __init__(self, repositorio: IRepositorioPrograma):
        self._repositorio = repositorio

    @staticmethod
    def _validar_llave(llave):
        if llave is None or str(llave).strip() == "":
            raise ValueError("La llave de el programa no puede estar vacía.")
        return llave

    async def listar(self, limite: int) -> list[dict]:
        # La FORMA del dato es correcta (sí es un entero), así que esto es
        # 400 y no 422.
        if limite <= 0:
            raise ValueError("El límite debe ser un entero mayor que cero.")
        return await self._repositorio.obtener_todos(limite)

    async def obtener(self, llave) -> dict:
        llave = self._validar_llave(llave)
        fila = await self._repositorio.obtener_por_llave(llave)
        if fila is None:
            raise LookupError(f"No existe el programa con id = {llave}")
        return fila

    async def crear(self, datos: dict) -> None:
        await self._repositorio.crear(datos)

    async def actualizar(self, llave, datos: dict) -> int:
        llave = self._validar_llave(llave)
        # Sin esta comprobación el repositorio devolvería 0 filas, que en toda
        # la demás lógica significa "no existe" — y responderíamos 404 en vez
        # del 400 que exige el contrato para un cuerpo vacío.
        if not datos:
            raise ValueError("No se envió ningún campo para actualizar.")
        filas = await self._repositorio.actualizar(llave, datos)
        if filas == 0:
            raise LookupError(f"No existe el programa con id = {llave}")
        return filas

    async def eliminar(self, llave) -> int:
        llave = self._validar_llave(llave)
        filas = await self._repositorio.eliminar_logico(llave)
        if filas == 0:
            raise LookupError(f"No existe el programa con id = {llave}")
        return filas
