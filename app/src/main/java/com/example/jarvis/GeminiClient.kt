package com.example.jarvis
import com.example.jarvis.BuildConfig
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

object GeminiClient {

    // TODO: apni free Gemini API key yaha daalo -> https://aistudio.google.com/app/apikey
    private const val API_KEY = BuildConfig.GEMINI_API_KEY

    private const val URL =
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=$API_KEY"

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

        val body = JSONObject().apply {
            put("contents", JSONArray().put(
                JSONObject().put("parts", JSONArray().put(
                    JSONObject().put("text", "$systemPrompt\n\nUser: $userText")
                ))
            ))
        }

        val request = Request.Builder()
            .url(URL)
            .post(RequestBody.create(MediaType.parse("application/json"), body.toString()))
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback("Boss, internet ya AI service se connect nahi ho paya.")
            }

            override fun onResponse(call: Call, response: Response) {
                val bodyStr = response.body?.string() ?: "{}"
                try {
                    val json = JSONObject(bodyStr)
                    val text = json.getJSONArray("candidates")
                        .getJSONObject(0)
                        .getJSONObject("content")
                        .getJSONArray("parts")
                        .getJSONObject(0)
                        .getString("text")
                    callback(text.trim())
                } catch (e: Exception) {
                    callback("Boss, API se ye jawab aaya: $bodyStr")
                }
            }
        })
    }
}
