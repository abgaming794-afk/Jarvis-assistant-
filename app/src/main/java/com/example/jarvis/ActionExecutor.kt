package com.example.jarvis

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.AlarmClock
import android.provider.ContactsContract
import android.hardware.camera2.CameraManager
import android.content.SharedPreferences

class ActionExecutor(private val context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("jarvis_notes", Context.MODE_PRIVATE)

    fun execute(intent: com.example.jarvis.Intent): String {
        return when (intent) {
            is com.example.jarvis.Intent.Call -> makeCall(intent.contactName)
            is com.example.jarvis.Intent.OpenApp -> openApp(intent.appName)
            is com.example.jarvis.Intent.WebSearch -> webSearch(intent.query)
            is com.example.jarvis.Intent.YoutubeSearch -> youtubeSearch(intent.query)
            is com.example.jarvis.Intent.Calculate -> calculate(intent.expression)
            is com.example.jarvis.Intent.TorchOn -> toggleTorch(true)
            is com.example.jarvis.Intent.TorchOff -> toggleTorch(false)
            is com.example.jarvis.Intent.SetAlarm -> setAlarm(intent.hour, intent.minute)
            is com.example.jarvis.Intent.SaveNote -> saveNote(intent.note)
            is com.example.jarvis.Intent.ReadNotes -> readNotes()
            is com.example.jarvis.Intent.SendMessage -> sendMessage(intent.app, intent.contact, intent.message)
            is com.example.jarvis.Intent.Unknown -> ""
        }
    }

    private fun makeCall(name: String): String {
        val uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        val cursor = context.contentResolver.query(
            uri, null,
            "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} LIKE ?",
            arrayOf("%$name%"), null
        )
        cursor?.use {
            if (it.moveToFirst()) {
                val numberIdx = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                val number = it.getString(numberIdx)
                val callIntent = Intent(Intent.ACTION_CALL, Uri.parse("tel:$number"))
                callIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                context.startActivity(callIntent)
                return "Boss, $name ko call kar raha hoon."
            }
        }
        return "Boss, mujhe $name naam ka contact nahi mila."
    }

    private fun openApp(appName: String): String {
        val pm = context.packageManager
        val apps = pm.getInstalledApplications(PackageManager.GET_META_DATA)
        val match = apps.firstOrNull {
            pm.getApplicationLabel(it).toString().contains(appName, ignoreCase = true)
        }
        if (match != null) {
            val launchIntent = pm.getLaunchIntentForPackage(match.packageName)
            if (launchIntent != null) {
                launchIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                context.startActivity(launchIntent)
                return "Boss, $appName khol raha hoon."
            }
        }
        return "Boss, mujhe $appName naam ka app nahi mila."
    }

    private fun webSearch(query: String): String {
        val intent = Intent(Intent.ACTION_WEB_SEARCH)
        intent.putExtra("query", query)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        try {
            context.startActivity(intent)
        } catch (e: Exception) {
            val fallback = Intent(Intent.ACTION_VIEW, Uri.parse("https://www.google.com/search?q=${Uri.encode(query)}"))
            fallback.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            context.startActivity(fallback)
        }
        return "Boss, $query search kar raha hoon."
    }

    private fun youtubeSearch(query: String): String {
        val intent = Intent(Intent.ACTION_VIEW,
            Uri.parse("https://www.youtube.com/results?search_query=${Uri.encode(query)}"))
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        context.startActivity(intent)
        return "Boss, YouTube par $query play kar raha hoon."
    }

    private fun calculate(expr: String): String {
        return try {
            val result = MiniExpressionEvaluator.eval(expr)
            "Boss, answer hai $result"
        } catch (e: Exception) {
            "Boss, ye expression samajh nahi aaya."
        }
    }

    private fun toggleTorch(on: Boolean): String {
        return try {
            val cm = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val camId = cm.cameraIdList[0]
            cm.setTorchMode(camId, on)
            if (on) "Boss, torch on kar diya." else "Boss, torch off kar diya."
        } catch (e: Exception) {
            "Boss, torch control nahi ho paya."
        }
    }

    private fun setAlarm(hour: Int, minute: Int): String {
        val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
            putExtra(AlarmClock.EXTRA_HOUR, hour)
            putExtra(AlarmClock.EXTRA_MINUTES, minute)
            putExtra(AlarmClock.EXTRA_SKIP_UI, true)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        context.startActivity(intent)
        return "Boss, alarm $hour baj kar $minute minute ke liye laga diya."
    }

    private fun saveNote(note: String): String {
        val existing = prefs.getStringSet("notes", mutableSetOf())?.toMutableSet() ?: mutableSetOf()
        existing.add("${System.currentTimeMillis()}::$note")
        prefs.edit().putStringSet("notes", existing).apply()
        return "Boss, note save kar diya."
    }

    private fun readNotes(): String {
        val notes = prefs.getStringSet("notes", mutableSetOf()) ?: mutableSetOf()
        if (notes.isEmpty()) return "Boss, koi notes save nahi hain."
        val texts = notes.map { it.substringAfter("::") }
        return "Boss, aapke notes hain: ${texts.joinToString(". ")}"
    }

    private fun sendMessage(app: String, contact: String, message: String): String {
        val phone = resolveContactPhone(contact)
        if (phone == null) return "Boss, $contact naam ka contact nahi mila."

        val uri = Uri.parse("https://wa.me/$phone?text=${Uri.encode(message)}")
        val intent = Intent(Intent.ACTION_VIEW, uri)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        context.startActivity(intent)
        JarvisAccessibilityService.pendingAutoSend = true
        return "Boss, $contact ko $app par message bhej raha hoon."
    }

    private fun resolveContactPhone(name: String): String? {
        val uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        val cursor = context.contentResolver.query(
            uri, null,
            "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} LIKE ?",
            arrayOf("%$name%"), null
        )
        cursor?.use {
            if (it.moveToFirst()) {
                val idx = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                return it.getString(idx).replace(" ", "").replace("-", "")
            }
        }
        return null
    }
}
