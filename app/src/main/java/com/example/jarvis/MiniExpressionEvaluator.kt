package com.example.jarvis

object MiniExpressionEvaluator {

    fun eval(expression: String): Double {
        val tokens = tokenize(expression.replace(" ", ""))
        val parser = Parser(tokens)
        return parser.parseExpression()
    }

    private fun tokenize(expr: String): List<String> {
        val tokens = mutableListOf<String>()
        var i = 0
        while (i < expr.length) {
            val c = expr[i]
            when {
                c.isDigit() || c == '.' -> {
                    val start = i
                    while (i < expr.length && (expr[i].isDigit() || expr[i] == '.')) i++
                    tokens.add(expr.substring(start, i))
                    continue
                }
                c in "+-*/()" -> {
                    tokens.add(c.toString())
                    i++
                }
                else -> i++
            }
        }
        return tokens
    }

    private class Parser(private val tokens: List<String>) {
        private var pos = 0

        fun parseExpression(): Double {
            var value = parseTerm()
            while (pos < tokens.size && (tokens[pos] == "+" || tokens[pos] == "-")) {
                val op = tokens[pos++]
                val rhs = parseTerm()
                value = if (op == "+") value + rhs else value - rhs
            }
            return value
        }

        private fun parseTerm(): Double {
            var value = parseFactor()
            while (pos < tokens.size && (tokens[pos] == "*" || tokens[pos] == "/")) {
                val op = tokens[pos++]
                val rhs = parseFactor()
                value = if (op == "*") value * rhs else value / rhs
            }
            return value
        }

        private fun parseFactor(): Double {
            if (pos < tokens.size && tokens[pos] == "(") {
                pos++
                val value = parseExpression()
                if (pos < tokens.size && tokens[pos] == ")") pos++
                return value
            }
            if (pos < tokens.size && tokens[pos] == "-") {
                pos++
                return -parseFactor()
            }
            val value = tokens[pos].toDouble()
            pos++
            return value
        }
    }
}
