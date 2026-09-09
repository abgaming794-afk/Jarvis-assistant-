package com.example.jarvis

import android.content.Context
import android.content.SharedPreferences

object PreferencesManager {

    private const val PREFS_NAME = "jarvis_settings"

    private const val KEY_WAKE_WORD = "wake_word_enabled"
    private const val KEY_AI_MODEL = "ai_model"
    private const val KEY_VOICE_ENGINE = "voice_engine"
    private const val KEY_TONE = "voice_tone"
    private const val KEY_SPEED = "voice_speed"
    private const val KEY_PITCH = "voice_pitch"
    private const val KEY_ELEVENLABS_KEY = "elevenlabs_api_key"
    private const val KEY_THEME = "app_theme"

    // AI model options
    const val MODEL_GEMINI_3_8 = "gemini-3.8-flash"
    const val MODEL_GEMINI_3_7 = "gemini-3.7-flash"

    // Voice engine options
    const val VOICE_DEVICE_TTS = "device_tts"
    const val VOICE_ELEVENLABS = "elevenlabs"

    // Theme options
    const val THEME_LIGHT = "light"
    const val THEME_DARK = "dark"
    const val THEME_SYSTEM = "system"

    private fun prefs(context: Context): SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    // ---- Wake word ----
    fun isWakeWordEnabled(context: Context): Boolean =
        prefs(context).getBoolean(KEY_WAKE_WORD, false)

    fun setWakeWordEnabled(context: Context, enabled: Boolean) {
        prefs(context).edit().putBoolean(KEY_WAKE_WORD, enabled).apply()
    }

    // ---- AI model (primary) ----
    fun getAiModel(context: Context): String =
        prefs(context).getString(KEY_AI_MODEL, MODEL_GEMINI_3_8) ?: MODEL_GEMINI_3_8

    fun setAiModel(context: Context, model: String) {
        prefs(context).edit().putString(KEY_AI_MODEL, model).apply()
    }

    // ---- Voice engine ----
    fun getVoiceEngine(context: Context): String =
        prefs(context).getString(KEY_VOICE_ENGINE, VOICE_DEVICE_TTS) ?: VOICE_DEVICE_TTS

    fun setVoiceEngine(context: Context, engine: String) {
        prefs(context).edit().putString(KEY_VOICE_ENGINE, engine).apply()
    }

    // ---- Tone / Speed / Pitch (0-100 scale, UI slider friendly) ----
    fun getTone(context: Context): Int = prefs(context).getInt(KEY_TONE, 50)
    fun setTone(context: Context, value: Int) {
        prefs(context).edit().putInt(KEY_TONE, value).apply()
    }

    fun getSpeed(context: Context): Int = prefs(context).getInt(KEY_SPEED, 50)
    fun setSpeed(context: Context, value: Int) {
        prefs(context).edit().putInt(KEY_SPEED, value).apply()
    }

    fun getPitch(context: Context): Int = prefs(context).getInt(KEY_PITCH, 50)
    fun setPitch(context: Context, value: Int) {
        prefs(context).edit().putInt(KEY_PITCH, value).apply()
    }

    // ---- ElevenLabs API key ----
    fun getElevenLabsKey(context: Context): String =
        prefs(context).getString(KEY_ELEVENLABS_KEY, "") ?: ""

    fun setElevenLabsKey(context: Context, key: String) {
        prefs(context).edit().putString(KEY_ELEVENLABS_KEY, key).apply()
    }

    // ---- Theme ----
    fun getTheme(context: Context): String =
        prefs(context).getString(KEY_THEME, THEME_DARK) ?: THEME_DARK

    fun setTheme(context: Context, theme: String) {
        prefs(context).edit().putString(KEY_THEME, theme).apply()
    }
}
