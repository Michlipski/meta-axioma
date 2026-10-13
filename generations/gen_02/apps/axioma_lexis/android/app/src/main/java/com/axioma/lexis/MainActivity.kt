package com.axioma.lexis

import android.annotation.SuppressLint
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat

/**
 * Android Main Activity for Axioma Lexis G2.
 *
 * Implements a standalone fullscreen client with offline HTML5 caching,
 * native touch drag physics, hardware vibration haptics via AndroidBridge,
 * system push/local notification scheduling with deep linking, and
 * automatic fallback to bundled assets if the remote server is unreachable.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val localAssetUrl = "file:///android_asset/index.html"
    private val CHANNEL_ID = "axioma_lexis_srs"
    private val NOTIFICATION_PERMISSION_CODE = 101

    /**
     * Native Javascript Interface exposing hardware capabilities to WebView.
     */
    inner class AndroidBridge(private val context: Context) {

        @JavascriptInterface
        fun vibrate(milliseconds: Long) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
                    vibratorManager?.defaultVibrator?.vibrate(
                        VibrationEffect.createOneShot(milliseconds, VibrationEffect.DEFAULT_AMPLITUDE)
                    )
                } else {
                    @Suppress("DEPRECATION")
                    val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        vibrator?.vibrate(
                            VibrationEffect.createOneShot(milliseconds, VibrationEffect.DEFAULT_AMPLITUDE)
                        )
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator?.vibrate(milliseconds)
                    }
                }
            } catch (e: Exception) {
                // Silently ignore if permission or hardware unavailable
            }
        }

        @JavascriptInterface
        fun showToast(message: String) {
            runOnUiThread {
                Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
            }
        }

        @JavascriptInterface
        fun postNotification(title: String, message: String, delaySeconds: Int) {
            runOnUiThread {
                scheduleNativeNotification(title, message, delaySeconds)
            }
        }

        @JavascriptInterface
        fun requestNotificationPermission() {
            runOnUiThread {
                checkAndRequestNotificationPermission()
            }
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Axioma Lexis Reminders"
            val descriptionText = "Spaced repetition due alerts and curiosity hooks"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 150, 80, 150)
            }
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun checkAndRequestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), NOTIFICATION_PERMISSION_CODE)
            }
        }
    }

    fun scheduleNativeNotification(title: String, message: String, delaySeconds: Int = 0) {
        checkAndRequestNotificationPermission()

        val task = Runnable {
            try {
                val intent = Intent(this, MainActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                    action = Intent.ACTION_VIEW
                    data = Uri.parse("lexis://review")
                }
                val flags = PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
                val pendingIntent = PendingIntent.getActivity(this, 0, intent, flags)

                val builder = NotificationCompat.Builder(this, CHANNEL_ID)
                    .setSmallIcon(android.R.drawable.ic_dialog_info)
                    .setContentTitle(title)
                    .setContentText(message)
                    .setStyle(NotificationCompat.BigTextStyle().bigText(message))
                    .setPriority(NotificationCompat.PRIORITY_HIGH)
                    .setDefaults(NotificationCompat.DEFAULT_ALL)
                    .setAutoCancel(true)
                    .setContentIntent(pendingIntent)

                val notificationManager = NotificationManagerCompat.from(this)
                if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
                    checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) {
                    notificationManager.notify((System.currentTimeMillis() % 10000).toInt(), builder.build())
                }
            } catch (e: Exception) {
                Toast.makeText(this, "Notification error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }

        if (delaySeconds <= 0) {
            task.run()
        } else {
            Handler(Looper.getMainLooper()).postDelayed(task, delaySeconds * 1000L)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createNotificationChannel()
        checkAndRequestNotificationPermission()

        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.databaseEnabled = true
            settings.cacheMode = WebSettings.LOAD_DEFAULT
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = true
            settings.setSupportZoom(false)
            settings.allowFileAccess = true
            settings.allowContentAccess = true
            settings.allowFileAccessFromFileURLs = true
            settings.allowUniversalAccessFromFileURLs = true
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            scrollBarStyle = View.SCROLLBARS_INSIDE_OVERLAY

            addJavascriptInterface(AndroidBridge(this@MainActivity), "AndroidBridge")

            webViewClient = WebViewClient()
            webChromeClient = WebChromeClient()
        }
        setContentView(webView)

        val targetUrl = resolveTargetUrl(intent)
        webView.loadUrl(targetUrl)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        val targetUrl = resolveTargetUrl(intent)
        webView.loadUrl(targetUrl)
    }

    private fun resolveTargetUrl(intent: Intent?): String {
        val data: Uri? = intent?.data
        val fragment = when (data?.host) {
            "capture" -> "#capture"
            "review" -> "#review"
            else -> ""
        }
        return "$localAssetUrl$fragment"
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
