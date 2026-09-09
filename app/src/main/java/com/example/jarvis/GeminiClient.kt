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
    private const val FALLBACK_MODEL = "gemini-3.7-flash"

    // Retry settings
    private const val MAX_RETRIES = 3
    private const val INITIAL_BACKOFF_MS = 1000L

    // Errors jinpar retry karna sahi hai (temporary/server-side issues)
    private val RETRYABLE_CODES = setOf(429, 500, 502, 503, 504)

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

        // Pehle primary model try karo (retries ke saath)
        callModelWithRetry(PRIMARY_MODEL, bodyJson, attempt = 1) { primaryResult, primarySuccess ->

            if (primarySuccess) {
                callback(primaryResult)
            } else {
                // Primary ke sab retries fail → fallback model try karo (retries ke saath)
                callModelWithRetry(FALLBACK_MODEL, bodyJson, attempt = 1) { fallbackResult, fallbackSuccess ->
                    callback(fallbackResult)
                }
            }
        }
    }

    /**
     * Model ko call karta hai, aur agar retryable error (503, 429, etc.) aaye
     * toh exponential backoff ke saath dobara try karta hai (max MAX_RETRIES baar).
     */
    private fun callModelWithRetry(
        model: String,
        bodyJson: String,
        attempt: Int,
        onDone: (String, Boolean) -> Unit
    ) {
        callModel(model, bodyJson) { result, success, errorCode ->

            if (success) {
                onDone(result, true)
                return@callModel
            }

            val isRetryable = errorCode != null && RETRYABLE_CODES.contains(errorCode)

            if (isRetryable && attempt < MAX_RETRIES) {
                val backoffMs = INITIAL_BACKOFF_MS * (1L shl (attempt - 1)) // 1s, 2s, 4s...
                Thread.sleep(backoffMs) // OkHttp callback thread pool par safe hai, UI thread block nahi hota
                callModelWithRetry(model, bodyJson, attempt + 1, onDone)
            } else {
                onDone(result, false)
            }
        }
    }

    /**
     * Ek single API call karta hai. Result ke saath error ka HTTP-jaisa code
     * (agar mila) bhi wapas karta hai, taaki retry logic decide kar sake.
     */
    private fun callModel(
        model: String,
        bodyJson: String,
        onDone: (String, Boolean, Int?) -> Unit
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
                // Network-level failure — retryable maan lo
                onDone(
                    "Boss, AI service se connect nahi ho paya.",
                    false,
                    503
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

                        // API ne error return kiya
                        if (json.has("error")) {
                            val errorObj = json.getJSONObject("error")
                            val code = errorObj.optInt("code", response.code)
                            val message = errorObj.optString(
                                "message",
                                "Kuch gadbad ho gayi."
                            )

                            val friendlyMsg = when (code) {
                                503 -> "Boss, AI system abhi busy hai (high demand). Thodi der mein try karta hoon."
                                429 -> "Boss, thodi jaldi-jaldi requests ja rahi hain. Ek second rukiye."
                                in 500..599 -> "Boss, AI server mein temporary problem hai."
                                else -> "Boss, AI se error aaya: $message"
                            }

                            onDone(friendlyMsg, false, code)
                            return@use
                        }

                        val candidates = json.optJSONArray("candidates")

                        if (candidates == null || candidates.length() == 0) {
                            onDone(
                                "Boss, AI ne koi response nahi diya.",
                                false,
                                null
                            )
                            return@use
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
                                false,
                                null
                            )
                        } else {
                            onDone(text, true, null)
                        }

                    } catch (e: Exception) {
                        onDone(
                            "Boss, API response samajhne mein problem hui.",
                            false,
                            null
                        )
                    }
                }
            }
        })
    }
}
