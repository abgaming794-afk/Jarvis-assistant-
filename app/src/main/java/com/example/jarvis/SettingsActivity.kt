package com.example.jarvis

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class SettingsActivity : AppCompatActivity() {

    private lateinit var toggleWakeWord: ToggleButton
    private lateinit var spinnerAiModel: Spinner
    private lateinit var spinnerVoiceEngine: Spinner
    private lateinit var etElevenLabsKey: EditText
    private lateinit var seekTone: SeekBar
    private lateinit var seekSpeed: SeekBar
    private lateinit var seekPitch: SeekBar
    private lateinit var spinnerTheme: Spinner
    private lateinit var btnSave: Button

    private val aiModels = listOf(
        PreferencesManager.MODEL_GEMINI_3_8,
        PreferencesManager.MODEL_GEMINI_3_7
    )

    private val voiceEngines = listOf(
        PreferencesManager.VOICE_DEVICE_TTS,
        PreferencesManager.VOICE_ELEVENLABS
    )

    private val themes = listOf(
        PreferencesManager.THEME_DARK,
        PreferencesManager.THEME_LIGHT,
        PreferencesManager.THEME_SYSTEM
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)
        title = "Settings"

        toggleWakeWord = findViewById(R.id.toggleWakeWordSetting)
        spinnerAiModel = findViewById(R.id.spinnerAiModel)
        spinnerVoiceEngine = findViewById(R.id.spinnerVoiceEngine)
        etElevenLabsKey = findViewById(R.id.etElevenLabsKey)
        seekTone = findViewById(R.id.seekTone)
        seekSpeed = findViewById(R.id.seekSpeed)
        seekPitch = findViewById(R.id.seekPitch)
        spinnerTheme = findViewById(R.id.spinnerTheme)
        btnSave = findViewById(R.id.btnSaveSettings)

        setupSpinners()
        loadCurrentSettings()

        btnSave.setOnClickListener { saveSettings() }
    }

    private fun setupSpinners() {
        spinnerAiModel.adapter = ArrayAdapter(
            this, android.R.layout.simple_spinner_dropdown_item, aiModels
        )
        spinnerVoiceEngine.adapter = ArrayAdapter(
            this, android.R.layout.simple_spinner_dropdown_item, voiceEngines
        )
        spinnerTheme.adapter = ArrayAdapter(
            this, android.R.layout.simple_spinner_dropdown_item, themes
        )
    }

    private fun loadCurrentSettings() {
        toggleWakeWord.isChecked = PreferencesManager.isWakeWordEnabled(this)

        spinnerAiModel.setSelection(
            aiModels.indexOf(PreferencesManager.getAiModel(this)).coerceAtLeast(0)
        )
        spinnerVoiceEngine.setSelection(
            voiceEngines.indexOf(PreferencesManager.getVoiceEngine(this)).coerceAtLeast(0)
        )
        spinnerTheme.setSelection(
            themes.indexOf(PreferencesManager.getTheme(this)).coerceAtLeast(0)
        )

        etElevenLabsKey.setText(PreferencesManager.getElevenLabsKey(this))
        seekTone.progress = PreferencesManager.getTone(this)
        seekSpeed.progress = PreferencesManager.getSpeed(this)
        seekPitch.progress = PreferencesManager.getPitch(this)
    }

    private fun saveSettings() {
        PreferencesManager.setWakeWordEnabled(this, toggleWakeWord.isChecked)
        PreferencesManager.setAiModel(this, aiModels[spinnerAiModel.selectedItemPosition])
        PreferencesManager.setVoiceEngine(this, voiceEngines[spinnerVoiceEngine.selectedItemPosition])
        PreferencesManager.setElevenLabsKey(this, etElevenLabsKey.text.toString().trim())
        PreferencesManager.setTone(this, seekTone.progress)
        PreferencesManager.setSpeed(this, seekSpeed.progress)
        PreferencesManager.setPitch(this, seekPitch.progress)
        PreferencesManager.setTheme(this, themes[spinnerTheme.selectedItemPosition])

        Toast.makeText(this, "Settings save ho gayi, Boss!", Toast.LENGTH_SHORT).show()
        finish()
    }
}
