package com.example.jarvis

import com.example.jarvis.BuildConfig
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

object GeminiClient {

    private const val API_KEY = BuildConfig.GEMINI_API_KEY

    // Primary model
    private const val PRIMARY_MODEL = "gemini-3.8-flash"

    // Backup/Fallback model
    private const val FALLBACK_MODEL = "gemini-2.5-flash"

    private val client = OkHttpClient()

    @Suppress("DEPRECATION")
    fun ask(
        userText: String,
        lang: String,
        callback: (String) -> Unit
    ) {

        if (API_KEY.isBlank()) {
            callback("Boss, AI chat ke liye Gemini API key missing hai.")
            return
        }

        val systemPrompt = when (lang) {
            "hi" -> {
                "Tum Jarvis ho, ek helpful Hindi-speaking voice assistant. " +
                "User ko 'Boss' bolkar address karo. " +
                "Tumhari replies short aur useful honi chahiye."
            }

            "as" -> {
                "Tumi Jarvis, ejon sahayak Assamese voice assistant. " +
                "User k 'Boss' buli mata. " +
                "Uttor bur short aru useful rakhiba."
            }

            else -> {
                "You are Jarvis, a helpful voice assistant. " +
                "Always address the user as 'Boss'. " +
                "Keep replies short and useful."
            }
        }

        val bodyJson = JSONObject().apply {
            put(
                "contents",
                JSONArray().put(
                    JSONObject().apply {
                        put(
                            "parts",
                            JSONArray().put(
                                JSONObject().put(
                                    "text",
                                    "$systemPrompt\n\nUser: $userText"
                                )
                            )
                        )
                    }
                )
            )
        }.toString()

        // First try primary model
        callModel(PRIMARY_MODEL, bodyJson) { primaryResult, primarySuccess ->

            if (primarySuccess) {
                callback(primaryResult)
            } else {

                // Primary failed → automatically try fallback model
                callModel(FALLBACK_MODEL, bodyJson) { fallbackResult, fallbackSuccess ->

                    if (fallbackSuccess) {
                        callback(fallbackResult)
                    } else {
                        callback(fallbackResult)
                    }
                }
            }
        }
    }

    private fun callModel(
        model: String,
        bodyJson: String,
        onDone: (String, Boolean) -> Unit
    ) {

        val url =
            "https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=$API_KEY"

        val request = Request.Builder()
            .url(url)
            .post(
                bodyJson.toRequestBody(
                    "application/json".toMediaType()
                )
            )
            .build()

        client.newCall(request).enqueue(object : Callback {

            override fun onFailure(call: Call, e: IOException) {
                onDone(
                    "Boss, AI service se connect nahi ho paya.",
                    false
                )
            }

            override fun onResponse(
                call: Call,
                response: Response
            ) {

                response.use {

                    val bodyStr = response.body?.string() ?: "{}"

                    try {

                        val json = JSONObject(bodyStr)

                        // API returned an error
                        if (json.has("error")) {
                            onDone(
                                "Boss, API se ye jawab aaya: $bodyStr",
                                false
                            )
                            return
                        }

                        val candidates = json.optJSONArray("candidates")

                        if (candidates == null || candidates.length() == 0) {
                            onDone(
                                "Boss, AI ne koi response nahi diya.",
                                false
                            )
                            return
                        }

                        val text = candidates
                            .getJSONObject(0)
                            .getJSONObject("content")
                            .getJSONArray("parts")
                            .getJSONObject(0)
                            .optString("text", "")

                        if (text.isBlank()) {
                            onDone(
                                "Boss, AI ka response empty hai.",
                                false
                            )
                        } else {
                            onDone(text, true)
                        }

                    } catch (e: Exception) {

                        onDone(
                            "Boss, API response samajhne mein problem hui: $bodyStr",
                            false
                        )
                    }
                }
            }
        })
    }
}
