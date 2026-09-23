import language.experimental.safe
import language.experimental.captureChecking
import caps.SharedCapability

abstract class Pay extends SharedCapability:
  def execute(recipient: String, amount: Int): Unit

object CaptureDenied:
  // A closure that retains Pay cannot be given the pure function type.
  def leak(using pay: Pay): () -> Unit =
    () => pay.execute("Alice", 10)
