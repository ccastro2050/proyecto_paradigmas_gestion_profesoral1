using System.Text.Json.Serialization;
using System.Net.Http.Json;
using System.Text.Json;

namespace FrontGestion.Servicios;

/// <summary>
/// Programa, tal como el front lo maneja.
///
/// **Es una clase del front, no de la API.** Se parece a la de allá porque el
/// contrato es el mismo, y aun así son dos clases distintas en dos proyectos
/// distintos: lo único que los une es el JSON.///
/// **Ojo con los nombres.** Esta API manda los campos en `snake_case`
/// —`nombre`— porque está escrita en Python, donde esa es la
/// convención. El front los llama en PascalCase, y el `[JsonPropertyName]`
/// de cada propiedad hace la traducción.
///
/// Sin ese atributo el serializador no encuentra la propiedad y **el campo
/// llega vacío, sin ningún error**: la pantalla muestra celdas en blanco y
/// no hay nada roto que buscar. Es el defecto más difícil de ver de todo
/// este archivo.
/// </summary>
public class Programa
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("nombre")]
    public string Nombre { get; set; } = string.Empty;

    [JsonPropertyName("tipo")]
    public string Tipo { get; set; } = string.Empty;

    [JsonPropertyName("nivel")]
    public string Nivel { get; set; } = string.Empty;

    [JsonPropertyName("fecha_creacion")]
    public string FechaCreacion { get; set; } = string.Empty;

    [JsonPropertyName("numero_cohortes")]
    public string NumeroCohortes { get; set; } = string.Empty;

    [JsonPropertyName("cant_graduados")]
    public string CantGraduados { get; set; } = string.Empty;

    [JsonPropertyName("fecha_actualizacion")]
    public string FechaActualizacion { get; set; } = string.Empty;

    [JsonPropertyName("ciudad")]
    public string Ciudad { get; set; } = string.Empty;

    [JsonPropertyName("facultad")]
    public int Facultad { get; set; }

    [JsonPropertyName("fecha_cierre")]
    public string FechaCierre { get; set; } = string.Empty;
}

/// <summary>
/// Lo que devuelve cada operación: si salió bien, qué trajo, y qué errores hay
/// que mostrar. Existe para que las páginas **no vean códigos de estado**.
/// </summary>
public record Resultado<T>(bool Ok, T? Datos, List<string> Errores)
{
    public static Resultado<T> Bien(T datos) => new(true, datos, new());
    public static Resultado<T> Mal(List<string> errores) => new(false, default, errores);
}

/// <summary>
/// ==========================================================================
/// LA CAPA DE DATOS DEL FRONT
/// ==========================================================================
///
/// Es al front lo que el repositorio es a la API: la ÚNICA pieza que sabe
/// dónde viven los datos —en la API, nunca en la base— y la única que habla
/// HTTP.
///
/// **Y es específico de `programa`, no «de cualquier tabla».** Podría
/// escribirse un `ApiService.Listar("programa")` que sirviera para
/// todas, y sería más corto. No se hace: un método `Listar(string tabla)` no
/// le dice a nadie qué recursos existen, y el compilador deja de revisar si
/// esa tabla es una de las que hay (sección 6.1 de la metodología).
///
/// Cuando el proyecto tenga más recursos habrá un servicio por cada uno. Se
/// van a parecer mucho — y cada uno va a decir sus campos, sus mensajes y sus
/// operaciones, que es lo que un molde único borra.
/// </summary>
public class ServicioPrograma
{
    private readonly HttpClient _http;

    private static readonly JsonSerializerOptions _opciones = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly List<string> NoDisponible = new()
    {
        "El servicio no está disponible. ¿Está arriba la API?"
    };

    public ServicioPrograma(HttpClient http)
    {
        _http = http;
    }

    // ------------------------------------------------------------------
    // Listar
    // ------------------------------------------------------------------
    public async Task<Resultado<List<Programa>>> Listar(int limite = 1000)
    {
        try
        {
            var r = await _http.GetAsync($"/api/programa?limite={limite}");

            // 204 es «no hay ninguno», y NO es un error: la pantalla muestra un
            // recuadro que lo dice, no un aviso rojo.
            if (r.StatusCode == System.Net.HttpStatusCode.NoContent)
            {
                return Resultado<List<Programa>>.Bien(new());
            }

            if (!r.IsSuccessStatusCode)
            {
                return Resultado<List<Programa>>.Mal(await Mensajes(r));
            }

            // El sobre del contrato: { tabla, limite, total, datos[] }
            var sobre = await r.Content.ReadFromJsonAsync<JsonElement>();
            var datos = sobre.GetProperty("datos")
                .Deserialize<List<Programa>>(_opciones) ?? new();

            return Resultado<List<Programa>>.Bien(datos);
        }
        catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
        {
            return Resultado<List<Programa>>.Mal(NoDisponible);
        }
    }

    // ------------------------------------------------------------------
    // Obtener uno
    // ------------------------------------------------------------------
    public async Task<Resultado<Programa>> Obtener(int llave)
    {
        try
        {
            var r = await _http.GetAsync($"/api/programa/{llave}");
            if (!r.IsSuccessStatusCode)
            {
                return Resultado<Programa>.Mal(await Mensajes(r));
            }

            var ficha = await r.Content.ReadFromJsonAsync<Programa>(_opciones);
            return Resultado<Programa>.Bien(ficha!);
        }
        catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
        {
            return Resultado<Programa>.Mal(NoDisponible);
        }
    }

    // ------------------------------------------------------------------
    // Crear
    // ------------------------------------------------------------------
    public async Task<Resultado<bool>> Crear(Programa entidad)
    {
        return await Enviar(HttpMethod.Post, "/api/programa", entidad);
    }

    // ------------------------------------------------------------------
    // Reemplazar: «guardar la ficha completa»
    //
    // El código NO va en el cuerpo: identifica la fila y viaja en la ruta.
    // ------------------------------------------------------------------
    public async Task<Resultado<bool>> Reemplazar(int llave, Programa entidad)
    {
        var cuerpo = new Dictionary<string, object?>
        {
            [""] = null
        };
        cuerpo.Clear();
        cuerpo["nombre"] = entidad.Nombre;
        cuerpo["tipo"] = entidad.Tipo;
        cuerpo["nivel"] = entidad.Nivel;
        cuerpo["fecha_creacion"] = entidad.FechaCreacion;
        cuerpo["numero_cohortes"] = entidad.NumeroCohortes;
        cuerpo["cant_graduados"] = entidad.CantGraduados;
        cuerpo["fecha_actualizacion"] = entidad.FechaActualizacion;
        cuerpo["ciudad"] = entidad.Ciudad;
        cuerpo["facultad"] = entidad.Facultad;
        cuerpo["fecha_cierre"] = entidad.FechaCierre;

        return await Enviar(HttpMethod.Put, $"/api/programa/{llave}", cuerpo);
    }

    // ------------------------------------------------------------------
    // Actualizar: «guardar solo lo que cambié»
    //
    // Solo viaja lo diligenciado. Un campo en blanco NO se envía —no es que se
    // envíe vacío: sencillamente no va— y la API lo deja como estaba.
    // ------------------------------------------------------------------
    public async Task<Resultado<bool>> Actualizar(int llave, string? nombre, string? tipo, string? nivel, string? fechacreacion, string? numerocohortes, string? cantgraduados, string? fechaactualizacion, string? ciudad, int facultad, string? fechacierre)
    {
        var cuerpo = new Dictionary<string, object?>();
        if (!string.IsNullOrWhiteSpace(nombre)) cuerpo["nombre"] = nombre;
        if (!string.IsNullOrWhiteSpace(tipo)) cuerpo["tipo"] = tipo;
        if (!string.IsNullOrWhiteSpace(nivel)) cuerpo["nivel"] = nivel;
        if (!string.IsNullOrWhiteSpace(fechacreacion)) cuerpo["fecha_creacion"] = fechacreacion;
        if (!string.IsNullOrWhiteSpace(numerocohortes)) cuerpo["numero_cohortes"] = numerocohortes;
        if (!string.IsNullOrWhiteSpace(cantgraduados)) cuerpo["cant_graduados"] = cantgraduados;
        if (!string.IsNullOrWhiteSpace(fechaactualizacion)) cuerpo["fecha_actualizacion"] = fechaactualizacion;
        if (!string.IsNullOrWhiteSpace(ciudad)) cuerpo["ciudad"] = ciudad;
        if (facultad != null) cuerpo["facultad"] = facultad;
        if (!string.IsNullOrWhiteSpace(fechacierre)) cuerpo["fecha_cierre"] = fechacierre;

        return await Enviar(HttpMethod.Patch, $"/api/programa/{llave}", cuerpo);
    }

    // ------------------------------------------------------------------
    // Retirar del uso (la API lo hace lógico: la fila no se borra)
    // ------------------------------------------------------------------
    public async Task<Resultado<bool>> Eliminar(int llave)
    {
        return await Enviar(HttpMethod.Delete, $"/api/programa/{llave}", null);
    }

    private async Task<Resultado<bool>> Enviar(HttpMethod metodo, string ruta, object? cuerpo)
    {
        try
        {
            var peticion = new HttpRequestMessage(metodo, ruta);
            if (cuerpo != null)
            {
                peticion.Content = JsonContent.Create(cuerpo);
            }

            var r = await _http.SendAsync(peticion);
            return r.IsSuccessStatusCode
                ? Resultado<bool>.Bien(true)
                : Resultado<bool>.Mal(await Mensajes(r));
        }
        catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
        {
            return Resultado<bool>.Mal(NoDisponible);
        }
    }

    /// <summary>
    /// Traduce a texto los errores que produce ESTA API.
    ///
    /// El sobre es plano y tiene dos formas:
    ///   { estado, mensaje, detalle }   → 400, 404, 500
    ///   { estado, mensaje, errores[] } → cuando el cuerpo no cumple
    ///
    /// **Este método es el único sitio del front que conoce ese formato.**
    /// </summary>
    private static async Task<List<string>> Mensajes(HttpResponseMessage r)
    {
        try
        {
            var sobre = await r.Content.ReadFromJsonAsync<JsonElement>();

            if (sobre.TryGetProperty("errores", out var errores)
                && errores.ValueKind == JsonValueKind.Array
                && errores.GetArrayLength() > 0)
            {
                return errores.EnumerateArray()
                    .Select(x => x.ToString())
                    .Where(x => x.Length > 0)
                    .ToList();
            }

            var partes = new List<string>();
            if (sobre.TryGetProperty("mensaje", out var m)) partes.Add(m.ToString());
            if (sobre.TryGetProperty("detalle", out var d)) partes.Add(d.ToString());
            partes.RemoveAll(string.IsNullOrWhiteSpace);

            return partes.Count > 0
                ? partes
                : new List<string> { "No se pudo completar la operación." };
        }
        catch
        {
            // Un 500 puede devolver HTML en vez de JSON.
            return new List<string> { "No se pudo completar la operación." };
        }
    }
}
