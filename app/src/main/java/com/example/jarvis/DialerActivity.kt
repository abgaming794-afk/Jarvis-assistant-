package com.example.jarvis

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class DialerActivity : AppCompatActivity() {

    private lateinit var numberInput: EditText
    private lateinit var callButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dialer)

        numberInput = findViewById(R.id.numberInput)
        callButton = findViewById(R.id.callButton)

        callButton.setOnClickListener {
            val number = numberInput.text.toString().trim()

            if (number.isBlank()) {
                Toast.makeText(this, "Boss, number daaliye pehle.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            makeCall(number)
        }
    }

    private fun makeCall(number: String) {
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.CALL_PHONE
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.CALL_PHONE),
                301
            )
            return
        }

        val intent = Intent(Intent.ACTION_CALL)
        intent.data = Uri.parse("tel:$number")
        startActivity(intent)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 301 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == PackageManager.PERMISSION_GRANTED
        ) {
            val number = numberInput.text.toString().trim()
            if (number.isNotBlank()) {
                makeCall(number)
            }
        } else {
            Toast.makeText(this, "Boss, call permission nahi mili.", Toast.LENGTH_SHORT).show()
        }
    }
}
