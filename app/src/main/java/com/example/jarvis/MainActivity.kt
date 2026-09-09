package com.example.jarvis

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.speech.RecognizerIntent
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var tvTranscript: TextView
    private lateinit var etCommand: EditText
    private lateinit var btnMic: Button
    private lateinit var btnSend: Button
    private lateinit var toggleWakeWord: ToggleButton

    private lateinit var ttsManager: TTSManager
    private lateinit var actionExecutor: ActionExecutor

    private val requiredPermissions = arrayOf(
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.CALL_PHONE,
        Manifest.permission.READ_CONTACTS,
        Manifest.permission.CAMERA
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvStatus = findViewById(R.id.tvStatus)
        tvTranscript = findViewById(R.id.tvTranscript)
        etCommand = findViewById(R.id.etCommand)
        btnMic = findViewById(R.id.btnMic)
        btnSend = findViewById(R.id.btnSend)
        toggleWakeWord = findViewById(R.id.toggleWakeWord)

        actionExecutor = ActionExecutor(this)
        ttsManager = TTSManager(this) {
            runOnUiThread { tvStatus.text = "Boss, main ready hoon." }
        }

        requestNeededPermissions()

        btnSend.setOnClickListener {
            val text = etCommand.text.toString()
            if (text.isNotBlank()) handleUserInput(text)
        }

        btnMic.setOnClickListener { startVoiceInput() }

        toggleWakeWord.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                    == PackageManager.PERMISSION_GRANTED) {
                    ContextCompat.startForegroundService(this, Intent(this, WakeWordService::class.java))
                    tvStatus.text = "Wake-word ON — 'Hey Sia' bolo."
                } else {
                    toggleWakeWord.isChecked = false
                    Toast.makeText(this, "Mic permission chahiye", Toast.LENGTH_SHORT).show()
                }
            } else {
                stopService(Intent(this, WakeWordService::class.java))
                tvStatus.text = "Boss, main ready hoon."
            }
        }
    }

    private fun requestNeededPermissions() {
        val missing = requiredPermissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 100)
        }
    }

    private fun startVoiceInput() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN")
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Bolo Boss...")
        }
        try {
            startActivityForResult(intent, 200)
        } catch (e: Exception) {
            Toast.makeText(this, "Voice recognition available nahi hai", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 200 && data != null) {
            val results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            val spokenText = results?.firstOrNull()
            if (!spokenText.isNullOrBlank()) {
                etCommand.setText(spokenText)
                handleUserInput(spokenText)
            }
        }
    }

    private fun handleUserInput(text: String) {
        tvTranscript.append("\nBoss: $text")
        val lang = CommandParser.detectLanguage(text)
        val intent = CommandParser.parse(text)

        if (intent is Intent.Unknown) {
            tvTranscript.append("\nJarvis: (sochte hue...)")
            GeminiClient.ask(text, lang) { reply ->
                runOnUiThread {
                    tvTranscript.append("\nJarvis: $reply")
                    ttsManager.speak(reply, lang)
                }
            }
        } else {
            val reply = actionExecutor.execute(intent)
            tvTranscript.append("\nJarvis: $reply")
            ttsManager.speak(reply, lang)
        }
        etCommand.text.clear()
    }

    override fun onDestroy() {
        ttsManager.shutdown()
        super.onDestroy()
    }
}
