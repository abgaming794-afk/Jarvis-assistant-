package com.example.jarvis

sealed class Intent {
    data class Call(val contactName: String) : Intent()
    data class OpenApp(val appName: String) : Intent()
    data class WebSearch(val query: String) : Intent()
    data class YoutubeSearch(val query: String) : Intent()
    data class Calculate(val expression: String) : Intent()
    object TorchOn : Intent()
    object TorchOff : Intent()
    data class SetAlarm(val hour: Int, val minute: Int) : Intent()
    data class SaveNote(val note: String) : Intent()
    object ReadNotes : Intent()
    data class SendMessage(val app: String, val contact: String, val message: String) : Intent()
    data class Unknown(val raw: String) : Intent()
}

object CommandParser {

    fun parse(input: String): Intent {
        val text = input.trim().lowercase()

        Regex("(?:call|फोन करो|फोन कर|काल करो|मात लगा|फोन दे)\\s+(.+)").find(text)?.let {
            return Intent.Call(it.groupValues[1].trim())
        }

        Regex("(?:send|भेजो|पठाई दे)\\s+(whatsapp|instagram|telegram|facebook)?\\s*message\\s+to\\s+(\\w+)\\s+saying\\s+(.+)")
            .find(text)?.let {
                val app = it.groupValues[1].ifBlank { "whatsapp" }
                return Intent.SendMessage(app, it.groupValues[2].trim(), it.groupValues[3].trim())
            }

        Regex("(?:open|खोलो|खोल दे|खुला दिया)\\s+(.+)").find(text)?.let {
            return Intent.OpenApp(it.groupValues[1].trim())
        }

        Regex("(?:play|youtube par|यूट्यूब पर)\\s+(.+?)\\s*(?:on youtube|youtube par|par)?$")
            .find(text)?.let {
                if (text.contains("youtube") || text.startsWith("play")) {
                    return Intent.YoutubeSearch(it.groupValues[1].trim())
                }
            }

        Regex("(?:search|खोजो|सर्च करो)\\s+(.+)").find(text)?.let {
            return Intent.WebSearch(it.groupValues[1].trim())
        }

        Regex("(?:calculate|calculator|गणना करो|हिसाब करो)\\s+(.+)").find(text)?.let {
            return Intent.Calculate(it.groupValues[1].trim())
        }
        if (text.matches(Regex("^[0-9+\\-*/.() ]+$")) && text.any { it.isDigit() }) {
            return Intent.Calculate(text)
        }

        if (Regex("(torch|flashlight|light).*(on|jalao|चालू)").containsMatchIn(text)) return Intent.TorchOn
        if (Regex("(torch|flashlight|light).*(off|bandh|बंद)").containsMatchIn(text)) return Intent.TorchOff

        Regex("(?:alarm).*?(\\d{1,2})[:. ](\\d{2})").find(text)?.let {
            return Intent.SetAlarm(it.groupValues[1].toInt(), it.groupValues[2].toInt())
        }
        Regex("(?:alarm).*?(\\d{1,2})\\s*(?:baje|o'clock|bje)").find(text)?.let {
            return Intent.SetAlarm(it.groupValues[1].toInt(), 0)
        }

        Regex("(?:note|note kar lo|likh lo|save karo)\\s+(.+)").find(text)?.let {
            return Intent.SaveNote(it.groupValues[1].trim())
        }
        if (Regex("(read|sunao|padho).*(notes?)").containsMatchIn(text)) return Intent.ReadNotes

        return Intent.Unknown(input)
    }

    fun detectLanguage(input: String): String {
        return when {
            input.any { it.code in 0x0900..0x097F } -> "hi"
            input.any { it.code in 0x0980..0x09FF } -> "as"
            else -> "en"
        }
    }
}
