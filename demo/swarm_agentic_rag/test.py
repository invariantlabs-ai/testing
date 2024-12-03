from run import run_buggy, run_fixed
import invariant.testing as it
import invariant.testing.functional as F
from invariant.custom_types.invariant_number import InvariantNumber

trace = run_fixed()
#trace = run_buggy()
trace = it.Trace(trace=trace) # TODO use from_swarm

def len(iterable):
    #return F.count(lambda x: InvariantNumber(1, x.addresses), iterable) # TODO does not work
    return F.count(lambda x: InvariantNumber(1), iterable)

def tool_results(trace):
    return F.filter(lambda x: x['role'] == 'tool', trace.messages())
    #return [result for _, result in trace.tool_pairs()]

def test_used_tool():
    with trace.as_context():
        it.assert_true(len(trace.tool_calls()) > 0, 'The calendar tool is used to access the calendar information at least once')
        it.expect_true(len(trace.tool_calls()) == 1, 'The calendar tool should only be used once')
 
 
 
        #tool_results = F.filter(lambda x: x['role'] == 'tool', trace.trace) 
        #print(tool_results[0]['content'], type(tool_results[0]['content']))
        count_sarah = F.count(lambda x: 'Sarah' in x['content'], tool_results(trace))
        count_john = F.count(lambda x: 'John' in x['content'], tool_results(trace))

        it.assert_true(len(count_sarah) >= 1 and len(count_john) >= 1, 'The calendar tool should return events for both Sarah and John')

def test_correct():
    with trace.as_context():
        it.assert_true(trace.messages(-1)['content'].contains('0:30'))
