import language.experimental.safe
import language.experimental.captureChecking
import caps.SharedCapability

abstract class Pay extends SharedCapability:
  def execute(recipient: String, amount: Int): Unit

object CastDenied:
  // An unchecked cast would fabricate authority if allowed in safe mode.
  def fabricate(obj: Object): Unit =
    obj.asInstanceOf[Pay].execute("Alice", 10)
