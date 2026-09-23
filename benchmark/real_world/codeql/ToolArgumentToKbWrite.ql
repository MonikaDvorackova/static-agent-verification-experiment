/**
 * @name OpenKB tool argument reaches knowledge-base file-write wrapper
 * @description Narrow research query for the pinned OpenKB example; reports possible taint flow, not a vulnerability.
 * @kind problem
 * @problem.severity warning
 * @id research/openkb-tool-argument-to-write
 * @tags security
 */
import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

module ToolContentToWrite implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    exists(Function tool, Parameter parameter |
      tool.getName() = "write_file" and
      tool.getLocation().getFile().getRelativePath() = "openkb/agent/query.py" and
      parameter = tool.getAnArg() and
      parameter.getName() = "content" and
      source = DataFlow::parameterNode(parameter)
    )
  }

  predicate isSink(DataFlow::Node sink) {
    exists(Call call, Name functionName |
      functionName = call.getFunc() and
      functionName.getId() = "write_kb_file" and
      call.getLocation().getFile().getRelativePath() = "openkb/agent/query.py" and
      sink.asExpr() = call.getArg(1)
    )
  }
}

module Flow = TaintTracking::Global<ToolContentToWrite>;

from DataFlow::Node source, DataFlow::Node sink
where Flow::flow(source, sink)
select sink, "The SDK tool content parameter can reach this write helper call from $@.",
  source, "tool-supplied content"
