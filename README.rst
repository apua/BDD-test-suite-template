This is a template of behavior-driven style Robot Framework test suite,
test resource, and test library.

While a project is big enough, the development should be ATDD -- acceptance
test driven development. Every story is detailed by acceptance tests, every
acceptance test is described in behaviors.

For ATDD, there is three stages:

0. Create and breakdown user stories.

1. Create specific BDD-style test cases based on acceptance tests.

   #. In the beginning, test cases and acceptance tests are 1-1;
      QA can extend test cases for the same acceptance tests later.
   #. Define "behavior - keyword" mapping to describe the actual behavior
      and fix unclear logic from keyword variables.
   #. Behaviors should invoke `set test variable` to implement the context
      of test case; in the opposite, keywords should invoke `[return]` and
      avoid unnecessary side effect.
   #. Use `log to console` to check expected local variables in behaviors.
   #. Mock keywords or invoke `no operation` to bypass real actions for
      validation.

2. Create or map keywords to behaviors.

   #. In Robot Framework, it is inconvenient to control complicated
      Python types. Therefore, keep types and actions out of scope of test
      be defined in test library.
   #. Low-level keywords are considered to have strict input/output types;
      data types are considered easy to get properties by `${obj.field}`.
   #. Invoke existing keywords if possible; otherwise, adjust or define
      a new one.
   #. Create mock Python code to bypass real actions for validation.

3. Create low-level library.

   #. Implement data types and low-level keywords.
   #. Avoid unnecessary pack/unpack variables since it breaks dryrun
      validation.
   #. Follow KISS principle in order to maintain it easily.
