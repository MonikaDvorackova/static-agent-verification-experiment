// Comparison candidate in an existing language. NOT COMPILED in this run.
// The trusted host must be the only holder of the model client and must issue
// recipient-bound grants. Merely placing these types in a Scala file does not
// seal package access or attest host-side authorization.
import language.experimental.safe
import language.experimental.captureChecking
import caps.SharedCapability

abstract class ModelSend extends SharedCapability:
  def send(recipient: String, content: String): Unit

final class Sensitive private (val content: String)
final class RecipientGrant private (val recipient: String)

object RecipientFlow:
  def publish(secret: Sensitive, grant: RecipientGrant)(using send: ModelSend): Unit =
    send.send(grant.recipient, secret.content)

// Deliberately incomplete: grant recipient and destination agree by construction,
// but grant issuance, scope to a specific secret, effect confinement and runtime
// service access need an audited host implementation; no end-to-end proof follows.
