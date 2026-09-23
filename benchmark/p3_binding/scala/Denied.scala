import language.experimental.safe
import language.experimental.captureChecking
import caps.SharedCapability

abstract class Pay extends SharedCapability:
  def execute(recipient: String, amount: Int): Unit

object Denied:
  // Intentionally invalid: there is no payment capability in scope.
  def agent(recipient: String, amount: Int): Unit =
    summon[Pay].execute(recipient, amount)
