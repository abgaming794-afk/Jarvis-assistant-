package com.example.jarvis

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.LinearInterpolator
import kotlin.math.min

class JarvisOrbView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    enum class OrbState { IDLE, LISTENING, THINKING, SPEAKING }

    private var ringAngle1 = 0f
    private var ringAngle2 = 0f
    private var ringAngle3 = 0f
    private var pulseScale = 1f
    private var baseColor = Color.parseColor("#06b6d4")

    private val corePaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val ringPaint1 = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE; strokeWidth = 5f; strokeCap = Paint.Cap.ROUND
    }
    private val ringPaint2 = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE; strokeWidth = 3.5f; strokeCap = Paint.Cap.ROUND
    }
    private val ringPaint3 = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE; strokeWidth = 2.5f; strokeCap = Paint.Cap.ROUND
    }

    private val rotateAnimator1 = ValueAnimator.ofFloat(0f, 360f).apply {
        duration = 6000; repeatCount = ValueAnimator.INFINITE; interpolator = LinearInterpolator()
    }
    private val rotateAnimator2 = ValueAnimator.ofFloat(360f, 0f).apply {
        duration = 9000; repeatCount = ValueAnimator.INFINITE; interpolator = LinearInterpolator()
    }
    private val rotateAnimator3 = ValueAnimator.ofFloat(0f, 360f).apply {
        duration = 14000; repeatCount = ValueAnimator.INFINITE; interpolator = LinearInterpolator()
    }
    private val pulseAnimator = ValueAnimator.ofFloat(0.85f, 1.15f).apply {
        duration = 1200
        repeatMode = ValueAnimator.REVERSE
        repeatCount = ValueAnimator.INFINITE
        interpolator = AccelerateDecelerateInterpolator()
    }

    init {
        rotateAnimator1.addUpdateListener { ringAngle1 = it.animatedValue as Float; invalidate() }
        rotateAnimator2.addUpdateListener { ringAngle2 = it.animatedValue as Float; invalidate() }
        rotateAnimator3.addUpdateListener { ringAngle3 = it.animatedValue as Float; invalidate() }
        pulseAnimator.addUpdateListener { pulseScale = it.animatedValue as Float; invalidate() }
        rotateAnimator1.start(); rotateAnimator2.start(); rotateAnimator3.start(); pulseAnimator.start()
    }

    fun setState(state: OrbState) {
        val (color, speedMultiplier, pulseDuration) = when (state) {
            OrbState.IDLE -> Triple(Color.parseColor("#06b6d4"), 1f, 1200L)
            OrbState.LISTENING -> Triple(Color.parseColor("#4f46e5"), 1.8f, 500L)
            OrbState.THINKING -> Triple(Color.parseColor("#a855f7"), 2.5f, 350L)
            OrbState.SPEAKING -> Triple(Color.parseColor("#06b6d4"), 2f, 300L)
        }
        baseColor = color
        pulseAnimator.duration = pulseDuration
        rotateAnimator1.duration = (6000 / speedMultiplier).toLong()
        rotateAnimator2.duration = (9000 / speedMultiplier).toLong()
        rotateAnimator3.duration = (14000 / speedMultiplier).toLong()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val cx = width / 2f
        val cy = height / 2f
        val radius = min(width, height) / 2f * 0.85f

        val glowRadius = radius * 0.45f * pulseScale
        corePaint.shader = RadialGradient(
            cx, cy, glowRadius * 1.8f,
            intArrayOf(alphaColor(baseColor, 200), alphaColor(baseColor, 60), alphaColor(baseColor, 0)),
            floatArrayOf(0f, 0.5f, 1f),
            Shader.TileMode.CLAMP
        )
        canvas.drawCircle(cx, cy, glowRadius * 1.8f, corePaint)

        corePaint.shader = null
        corePaint.color = alphaColor(baseColor, 230)
        canvas.drawCircle(cx, cy, glowRadius * 0.55f, corePaint)

        drawRing(canvas, cx, cy, radius * 0.65f, ringAngle1, ringPaint1, 90f, alphaColor(baseColor, 220))
        drawRing(canvas, cx, cy, radius * 0.8f, ringAngle2, ringPaint2, 140f, alphaColor(baseColor, 160))
        drawRing(canvas, cx, cy, radius * 0.95f, ringAngle3, ringPaint3, 60f, alphaColor(baseColor, 110))
    }

    private fun drawRing(
        canvas: Canvas, cx: Float, cy: Float, radius: Float,
        angle: Float, paint: Paint, sweepAngle: Float, color: Int
    ) {
        paint.color = color
        val rect = RectF(cx - radius, cy - radius, cx + radius, cy + radius)
        canvas.drawArc(rect, angle, sweepAngle, false, paint)
        canvas.drawArc(rect, angle + 180f, sweepAngle, false, paint)
    }

    private fun alphaColor(color: Int, alpha: Int): Int =
        Color.argb(alpha, Color.red(color), Color.green(color), Color.blue(color))

    override fun onDetachedFromWindow() {
        rotateAnimator1.cancel(); rotateAnimator2.cancel(); rotateAnimator3.cancel(); pulseAnimator.cancel()
        super.onDetachedFromWindow()
    }
}
