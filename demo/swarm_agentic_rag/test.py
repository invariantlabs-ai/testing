from run import run_buggy, run_fixed
import invariant.testing as it
import invariant.testing.functional as F
from invariant.custom_types.invariant_number import InvariantNumber

#trace = run_fixed()
trace = run_buggy()
trace = it.Trace(trace=trace) # TODO use from_swarm

def len(iterable):
    return sum(F.map(lambda x: InvariantNumber(1), iterable))

def tool_results(trace):
    return F.filter(lambda x: x['role'] == 'tool', trace.messages())

def test_used_tool():
    with trace.as_context():
        it.assert_true(len(trace.tool_calls()) > 0, 'The calendar tool is used to access the calendar information at least once')
        it.expect_true(len(trace.tool_calls()) == 1, 'The calendar tool should only be used once')
 
        count_sarah = len(F.filter(lambda x: x['content'].contains('Sarah'), tool_results(trace)))
        count_john = len(F.filter(lambda x: x['content'].contains('John'), tool_results(trace)))
        it.assert_true(count_sarah >= 1 and count_john >= 1, 'The calendar tool should return events for both Sarah and John')

def test_correct():
    with trace.as_context():
        it.assert_true(trace.messages(-1)['content'].contains('0:30'))
