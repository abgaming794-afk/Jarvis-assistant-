package com.example.jarvis
import com.example.jarvis.BuildConfig
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

object GeminiClient {

    private const val API_KEY = BuildConfig.GEMINI_API_KEY

    private const val PRIMARY_MODEL = "gemini-3.8-flash"
    private const val FALLBACK_MODEL = "gemini-2.5-flash"

    private val client = OkHttpClient()
    @Suppress("DEPRECATION_ERROR")
    fun ask(userText: String, lang: String, callback: (String) -> Unit) {
        if (API_KEY.isBlank()) {
            callback("Boss, AI chat ke liye pehle Gemini API key GeminiClient.kt mein daalni hogi.")
            return
        }

        val systemPrompt = when (lang) {
            "hi" -> "Tum Jarvis ho, ek helpful Hindi-speaking voice assistant. User ko 'Boss' bol kar address karo. Reply short aur helpful rakho."
            "as" -> "Tumi Jarvis, ejon sohayok Assamese voice assistant. User ke 'Boss' buli mati kotha koba. Uttar chuti rakhiba."
            else -> "You are Jarvis, a helpful voice assistant. Always address the user as 'Boss'. Keep replies short and natural."
        }

        val bodyJson = JSONObject().apply {
            put("contents", JSONArray().put(
                JSONObject().put("parts", JSONArray().put(
                    JSONObject().put("text", "$systemPrompt\n\nUser: $userText")
                ))
            ))
        }.toString()

        callModel(PRIMARY_MODEL, bodyJson) { primaryResult, primarySuccess ->
            if (primarySuccess) {
                callback(primaryResult)
            } else {
                // Primary model failed - try fallback
                callModel(FALLBACK_MODEL, bodyJson) { fallbackResult, fallbackSuccess ->
                    callback(fallbackResult)
                }
            }
        }
    }

    private fun callModel(model: String, bodyJson: String, onDone: (String, Boolean) -> Unit) {
        val url = "https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=$API_KEY"

        val request = Request.Builder()
            .url(url)
            .post(RequestBody.create(MediaType.parse("application/json"), bodyJson))
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                onDone("Boss, internet ya AI service se connect nahi ho paya.", false)
            }

            override fun onResponse(call: Call, response: Response) {
                val bodyStr = response.body?.string() ?: "{}"
                try {
                    val json = JSONObject(bodyStr)
                    if (json.has("error")) {
                        onDone("Boss, API se ye jawab aaya: $bodyStr", false)
                        return
                    }
                    val text = json.getJSONArray("candidates")
                        .getJSONObject(0)
                        .getJSONObject("content")
                        .getJSONArray("parts")
                        .getJSONObject(0)
                        .getString("text")
                    onDone(text.trim(), true)
                } catch (e: Exception) {
                    onDone("Boss, API se ye jawab aaya: $bodyStr", false)
                }
            }
        })
    }
}
