"""Given tests."""

import textwrap


def test_given_injection(pytester):
    pytester.makefile(
        ".feature",
        given=textwrap.dedent(
            """\
            Feature: Given
                Scenario: Test given fixture injection
                    Given I have injecting given
                    Then foo should be "injected foo"
            """
        ),
    )
    pytester.makepyfile(
        textwrap.dedent(
            """\
        import pytest
        from pytest_bdd import given, then, scenario

        @scenario("given.feature", "Test given fixture injection")
        def test_given():
            pass

        @given("I have injecting given", target_fixture="foo")
        def _():
            return "injected foo"


        @then('foo should be "injected foo"')
        def _(foo):
            assert foo == "injected foo"

        """
        )
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_parsing_sub_string_steps(pytester):
    # This package has changed behaviour, so that now _all_ step defs that match will run for a step.
    # This means we'll need to

    pytester.makefile(
        ".feature",
        example=textwrap.dedent(
            """\
            Feature: An example feature
                Scenario: An example scenario
                    Given the foo is bar
                    Given the foo is very bar
            """
        ),
    )
    pytester.makepyfile(
        textwrap.dedent(
            """\
        import pytest
        from pytest_bdd import given, parsers, then, scenario

        @scenario("example.feature", "An example scenario")
        def test_example():
            pass

        @given(parsers.parse("the {first} is {second}"))
        def _(first, second):
            assert first == "foo"
            assert second == "bar"

        @given(parsers.parse("the {first} is very {second}"))
        def _(first, second):
            assert first == "foo"
            assert second == "bar"

        """
        )
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_parsing_missing_example(pytester):
    # This package has changed behaviour, keep existing behaviour

    pytester.makefile(
        ".feature",
        example=textwrap.dedent(
            """\
            Feature: An example feature
                Scenario Outline: An example scenario with example
                    Given the <foo>
                Examples:
                    | foo |
                    |     |
            """
        ),
    )
    pytester.makepyfile(
        textwrap.dedent(
            """\
        import pytest
        from pytest_bdd import given, parsers, then, scenario

        def parameterized_or_literal(request, argument):
            if not argument:
                return None

            if argument[0] == "<" and argument[-1] == ">":
                return request.getfixturevalue(argument[1:-1])
            return argument

        @scenario("example.feature", "An example scenario with example")
        def test_example():
            pass

        @given(parsers.parse("the {foo}"))
        def _(request, foo):
            assert parameterized_or_literal(request, foo) == None
        """
        )
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
