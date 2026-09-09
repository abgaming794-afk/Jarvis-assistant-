package com.example.jarvis

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class JarvisAccessibilityService : AccessibilityService() {

    companion object {
        var pendingAutoSend = false
        private const val SEND_BUTTON_ID = "com.whatsapp:id/send"
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (!pendingAutoSend) return
        if (event?.packageName != "com.whatsapp") return

        val root: AccessibilityNodeInfo = rootInActiveWindow ?: return
        val sendButton = root.findAccessibilityNodeInfosByViewId(SEND_BUTTON_ID)
        if (sendButton.isNotEmpty()) {
            sendButton[0].performAction(AccessibilityNodeInfo.ACTION_CLICK)
            pendingAutoSend = false
        }
    }

    override fun onInterrupt() {}
}
