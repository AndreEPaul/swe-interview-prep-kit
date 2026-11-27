# Technical screens: restore execution fluency

## Practice the actual format

Collect reliable information: language, environment, running/testing workflow, duration, allowed libraries/AI, and whether the round is algorithms, component building, incremental business rules, debugging, or discussion.

Do not turn every engineering interview into either a difficult algorithm grind or a frontend-only exercise. Current role instructions beat general company anecdotes.

The workflow is language-neutral; the worked mechanism explanations below lean JavaScript/TypeScript and React, with a short Python companion. Adapt to the requested language rather than importing a frontend task into every interview. Use a supplied attempt as the starting point, including pasted code, and say which version was actually reviewed.

Use permitted or original practice. An announced preparation topic can guide a new exercise, not reconstruction of confidential assessment content. Generalize employer code/designs and keep candidate files and requested records in a confirmed private location outside this repository.

For a format that explicitly permits AI-generated investigation or code, use the separate [AI-assisted interview workflow](./ai-assisted-interviews.md). It practices directing, understanding, and verifying delegated work; it is not the same mode as a candidate-first attempt with coaching hints.

## One rep, four phases

1. **Clarify:** restate input/output, ordering, identity, mutation, errors, and scope.
2. **Plan:** name the state/data structure, invariants, and smallest working path.
3. **Implement and run:** demonstrate a normal case before accumulating extensions.
4. **Review:** edge/negative tests, explanation, and one transferable correction.

Reserve testing time inside the timebox. A partial solution with a clear working core and honest omissions is better preparation than an unexecuted polished design.

## Practical families worth rotating

- Nested navigation traversal: collect visible labels in defined order, including repeated labels and independent calls.
- Async data loading: success, rejection, empty data, pending completion, cleanup.
- Function composition: prepare reusable predicates or validators, then apply them independently.
- Business-rule processing: validate before mutation; decompose decisions before they become tangled conditions.
- UI selection/favorites: stable IDs, derived counts, repeat operations, owner-scoped rendering.
- Event history: chronological order versus insertion order, grouped output, stable ties, input preservation.
- Debugging: unfamiliar code with a clear contract, independently running checks, and small root-cause fixes.

These are generic drill families, not a claimed list of questions for any employer.

## Mechanisms to understand, not just memorize

### Functions and async values

A function reference is not its invocation, and a Promise is not its fulfilled value. Mixing either up hands the wrong kind of value to the next step:

```js
setTimeout(save, 100);    // the timer calls save after 100 ms
setTimeout(save(), 100);  // calls save now; the timer gets whatever save returned

getUser().name;           // undefined: this reads the Promise
(await getUser()).name;   // reads the user
```

- Return or await the whole operation when the caller must know it finished.
- A `catch` that returns normally recovers a rejection. Rethrow when propagation is part of the contract.
- Inside `try`, `return fn()` hands back the promise before it settles, so a later rejection skips your `catch`. `return await fn()` keeps the rejection inside it.
- A return in `try` still executes `finally`; cleanup must not overwrite a newer operation or override outcomes accidentally.

### Closures and composition

A closure retains access to bindings from its lexical environment. A higher-order function accepts or returns functions. These are different concepts, even when both appear in one API:

```js
const minLength = (n) => (s) => s.length >= n;  // higher-order: returns a function; the inner one closes over n
const atLeast3 = minLength(3);
atLeast3("ab");  // false
```

Prepare data now and accept another argument later, without expecting an inner function to read scope it was not defined in. Declaring `function isAdult() {}` creates a name in scope; it does not add `isAdult` to an object such as `rules`.

### React debounce, races, and cache are different jobs

- **Debounce:** limit starts after activity pauses.
- **Request relevance:** decide which already-running work may update the current view.
- **Cache:** reuse successful results under a defined key/freshness policy.

A timer-owning debounce wrapper recreated every render does not share one timer. Preserving it (with a ref or memoization) while reading old captured state creates a different bug: a stale closure.

Think: stable function/debouncer, latest data supplied as arguments, returned effect cleanup, and an explicit current-request rule. State is a render snapshot; a ref is persistent mutable bookkeeping. Initializing a ref from state does not synchronize it automatically.

Invalidate obsolete results, errors, and loading cleanup on a new view, even before a new debounce timer fires. Give each input a generation (a counter) and apply an outcome only if its generation is still the latest:

```js
let latest = 0;
const debouncedSearch = debounce(search, 300);

function onInput(query) {
  const id = ++latest;                    // every new input starts a new generation
  debouncedSearch(query, id);
}

async function search(query, id) {
  try {
    const results = await fetchResults(query);
    if (id === latest) show(results);     // a newer input exists otherwise; drop this response
  } catch (err) {
    if (id === latest) showError(err);
  } finally {
    if (id === latest) setLoading(false);
  }
}
```

Bumping the counter on input, not when the request starts, is what makes a response that arrives during the debounce wait count as stale. A counter identifies the input, not just its text. If the user types `a`, then `ab`, then `a` again, two requests carry the same query, and only the counter says which one may still update the screen. Without the guard, a slow response to an older request can arrive last and overwrite newer results.

Unless the spec says otherwise, cache normalized successful results, including empty arrays; do not disguise failures as successes. Define expiry boundaries and cache ownership. A cache hit must still invalidate older work even though it starts no request.

### State and display

- Define idle/loading/success-empty/success-data/error behavior.
- Clear input is a transition, not merely "skip fetching."
- Each component instance owns its own state and the DOM it renders. Two instances should not share state by accident or update each other's nodes.
- For rendering, created nodes must actually be inserted. Visually identical output can still fail an overly narrow test; understand the contract before changing code.

### Sorting and ownership

Map insertion order is not chronological order. Numeric timestamps and fixed-format date strings need appropriate comparisons. Reversing arbitrary input is not sorting it.

Array sorting mutates its target. Sorting a newly built bucket differs from sorting the caller's array. Copy to satisfy the actual ownership contract, not every object indiscriminately: `[...events].sort(compare)`, or `events.toSorted(compare)` in current runtimes.

### The same ideas in Python

If your round is in Python, practice the matching traps:

```python
async def get_user(): return {"name": "Ada"}

async def main():
    # get_user()["name"] would raise TypeError: a coroutine is not the dict
    return (await get_user())["name"]   # "Ada"; await only works inside an async function

fns = [lambda: i for i in range(3)]
[f() for f in fns]            # [2, 2, 2]: each lambda looks up i when called, after the loop ended
fns = [lambda i=i: i for i in range(3)]   # bind the current value instead: [0, 1, 2]

def add(item, bucket=[]):     # the default list is created once and shared by every call that omits it
    bucket.append(item)
    return bucket

xs = [3, 1, 2]
xs.sort()                     # sorts in place and returns None
sorted(xs)                    # returns a new list
```

For Java, Go, C#, or another language, map the same four ideas: an async result is not its completion, what a closure captures, defaults and shared state that outlive a call, and operations that mutate versus copy.

## Verify the exact requirement

- For timing, use a request log or controlled clock; test the delay and final arguments, not just that results eventually appear.
- For independent state, create two instances.
- For rejected mutations, compare state before and after the rejection.
- For snapshots, mutate a returned collection and check the owner and earlier snapshots remain unchanged.
- For retries, check total attempt count, not just one happy retry.
- After existing checks pass, add a candidate-designed case for a requirement they did not cover, whether those checks came from a scaffold or the candidate.

A passing suite is useful evidence, not a completeness guarantee. Record what you verified and what remains. If the review stops at one useful hint or one failing seam, explicitly name important contract cases still untested or deferred; that is honest scoping, not a reason to run an exhaustive suite before helping.

## Hint-driven work is still learning

If stuck, ask for a trace, a value/type distinction, or the relevant lifecycle rather than the completed solution. If repeated hints become circular, switch explicitly to explanation and a separate reference. Later, try a small variation without looking.

You can request an explanation, worked example, or reference at any time; this is teaching mode, not a failed attempt at learning. Record actual help as none / hint / explanation / scaffold / reference, with a description rather than a numerical score. Do not infer personal characteristics from an observable practice difficulty.

Do not label a coached solution an unaided mock. Do not use practice tools during a real assessment where they are forbidden.

Use the [practice and debrief record](../templates/practice-record.md) when helpful. Return a brief debrief in chat; save it only when requested to a confirmed private location. After a real screen, see [Debriefing real interviews](./debriefing.md).

## Small CSS/layout pass when the round includes it

Use an existing component. Refresh box model/sizing, max-width, spacing/alignment, Flexbox versus Grid, wrapping/overflow, long text, narrow screens, and visible focus. Recheck behavior afterward.

Styling can be one component without being the whole round. Clarify fidelity requirements instead of assuming either pixel perfection or "styling does not matter."
