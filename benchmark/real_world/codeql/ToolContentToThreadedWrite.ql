/**
 * @name Selected tool content reaches scheduled write helper
 * @description Narrow scheduling-edge query; this does not follow the asynchronous call into the actual file write.
 * @kind problem
 * @problem.severity warning
 * @id research/selected-tool-content-to-threaded-helper
 * @tags security
 */
import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

module ToolToThread implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    exists(Function tool, Parameter parameter |
      tool.getName() = "write_file" and
      tool.getLocation().getFile().getRelativePath() = "src/tools/write_file_tool.py" and
      parameter = tool.getAnArg() and parameter.getName() = "content" and
      source = DataFlow::parameterNode(parameter)
    )
  }

  predicate isSink(DataFlow::Node sink) {
    exists(Call call |
      call.getFunc().(Attribute).getName() = "to_thread" and
      call.getLocation().getFile().getRelativePath() = "src/tools/write_file_tool.py" and
      sink.asExpr() = call.getArg(2)
    )
  }
}

module Flow = TaintTracking::Global<ToolToThread>;

from DataFlow::Node source, DataFlow::Node sink
where Flow::flow(source, sink)
select sink, "Tool content reaches the scheduled helper argument from $@; helper body requires separate review.",
  source, "tool-supplied content"
