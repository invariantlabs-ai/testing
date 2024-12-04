from run import run_buggy, run_fixed
import invariant.testing as it
import invariant.testing.functional as F

trace = run_fixed()
#trace = run_buggy()
trace = it.Trace.from_swarm(trace)

def test_used_tool():
    with trace.as_context():
        it.assert_true(len(trace.tool_calls()) > 0, 'The calendar tool is used to access the calendar information at least once')
        it.expect_true(len(trace.tool_calls()) == 1, 'The calendar tool should only be used once')

        count_sarah = F.len(trace.messages(role='tool', content=lambda c: 'Sarah' in c))
        count_john = F.len(trace.messages(role='tool', content=lambda c: 'John' in c))
        it.assert_true((count_sarah >= 1) & (count_john >= 1), 'The calendar tool should return events for both Sarah and John')

def test_correct():
    with trace.as_context():
        it.assert_true(trace.messages(-1)['content'].contains('0:30'))
