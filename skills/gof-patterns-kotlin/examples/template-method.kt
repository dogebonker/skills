// Template Method: the base class fixes the order of steps, and subclasses fill in the open ones.
// Android's Activity and Fragment lifecycles work this way (onCreate, onStart, ...).

abstract class DataImporter {
    fun importFrom(source: String): Int {
        val raw = read(source)
        val records = parse(raw)
        val valid = records.filter { isValid(it) }
        store(valid)
        return valid.size
    }

    protected abstract fun read(source: String): String
    protected abstract fun parse(raw: String): List<String>

    protected open fun isValid(record: String): Boolean = record.isNotBlank()   // hook with a default

    protected open fun store(records: List<String>) {
        println("stored ${records.size}: $records")
    }
}

class CsvImporter : DataImporter() {
    override fun read(source: String) = source.trim()
    override fun parse(raw: String) = raw.split(",")
}

class JsonImporter : DataImporter() {
    override fun read(source: String) = source.trim()
    override fun parse(raw: String) =
        raw.removeSurrounding("[", "]").split(",").map { it.trim().removeSurrounding("\"") }
    override fun isValid(record: String) = record.length > 1
}

fun main() {
    println(CsvImporter().importFrom("a,,b,c"))
    println(JsonImporter().importFrom("""["x", "yy", "zzz"]"""))
}
