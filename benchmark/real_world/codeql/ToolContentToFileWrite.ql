/**
 * @name Selected SDK tool content reaches a file-write call
 * @description Research-only flow query on three pinned projects; names are a manual model and do not prove a vulnerability.
 * @kind problem
 * @problem.severity warning
 * @id research/selected-sdk-tool-content-to-write
 * @tags security
 */
import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

module ToolContentToWrite implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    exists(Function tool, Parameter parameter, string file |
      tool.getName() = "write_file" and
      file = tool.getLocation().getFile().getRelativePath() and
      file in ["openkb/agent/query.py", "python/src/copane/tools/write_file.py", "src/tools/write_file_tool.py"] and
      parameter = tool.getAnArg() and parameter.getName() = "content" and
      source = DataFlow::parameterNode(parameter)
    )
  }

  predicate isSink(DataFlow::Node sink) {
    exists(Call call |
      (
        call.getFunc().(Name).getId() = "write_kb_file" and sink.asExpr() = call.getArg(1)
        or
        call.getFunc().(Attribute).getName() = "write" and sink.asExpr() = call.getArg(0)
      )
    )
  }
}

module Flow = TaintTracking::Global<ToolContentToWrite>;

from DataFlow::Node source, DataFlow::Node sink
where Flow::flow(source, sink)
select sink, "Selected tool parameter can reach a named file-write call from $@; review the receiver and path restrictions.",
  source, "tool-supplied content"
