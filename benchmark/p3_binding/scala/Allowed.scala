import language.experimental.safe
import language.experimental.captureChecking
import caps.SharedCapability

// The only privileged entry point in this toy closed-world module is Pay.execute.
// The host is trusted to construct and hand out Pay; agent code receives it as a parameter.
abstract class Pay extends SharedCapability:
  def execute(recipient: String, amount: Int): Unit

object Allowed:
  def agent(recipient: String, amount: Int)(using pay: Pay): Unit =
    pay.execute(recipient, amount)
