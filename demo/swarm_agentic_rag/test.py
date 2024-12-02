from run import run_buggy, run_fixed
import invariant.testing as it

# TODO: failure in ipython notebook
# TODO: need absolute path to run

trace = run_fixed()
#trace = run_buggy()
trace = it.Trace(trace=trace)

def test_used_tool():
    with trace.as_context():
        it.assert_true(len(trace.tool_calls()) > 0, 'The calendar tool is used to access the calendar information at least once')
        it.expect_true(len(trace.tool_calls()) == 1, 'The calendar tool should only be used once')
     
        # TODO: can i write this better ?
        tool_results = [result for _, result in trace.tool_pairs()] # TODO: still has none issue
        contains_sarah = any('Sarah' in result['content'] for result in tool_results)
        contains_john = any('John' in result['content'] for result in tool_results)
        it.assert_true(contains_sarah and contains_john, 'The calendar tool should return events for both Sarah and John')

def test_correct():
    with trace.as_context():
        # TODO: no highlighting
        it.assert_true('0:30' in trace.messages(-1)['content'])
