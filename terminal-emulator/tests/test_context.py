import pytest
from src.context import Context

@pytest.fixture()
def ctx():
    yield Context()

def test_add_unscoped(ctx):
    ctx.add_unscoped_param('a', '1')
    assert ctx.get_value('a') == '1'

    ctx.add_unscoped_param('a', '2')
    assert ctx.get_value('a') == '2'

def test_add_unscoped_scoped_same_name(ctx):
    ctx.add_scoped_param('a', '100')
    assert ctx.get_value('a') == '100'

    ctx.add_unscoped_param('a', '200')
    assert ctx.get_value('a') == '100'

def test_add_unscoped_scoped_diff_name(ctx):
    ctx.add_scoped_param('a', '100')
    assert ctx.get_value('a') == '100'

    ctx.add_unscoped_param('b', '200')
    assert ctx.get_value('b') == '200'

    assert ctx.get_env() == {'a': '100', 'b': '200'}

def test_exit_scope(ctx):
    ctx.add_scoped_param('a', '100')
    ctx.add_unscoped_param('b', '200')

    assert ctx.get_env() == {'a': '100', 'b': '200'}

    ctx.exit_scope()

    assert ctx.get_env() == {'b': '200'}

@pytest.mark.parametrize(
    'template,expected',
    [
        ("$x$y", "12"),
        ("cat $x", "cat 1"),
    ]
)
def test_template(ctx, template, expected):
    ctx.add_unscoped_param('x', '1')
    ctx.add_unscoped_param('y', '2')

    assert ctx.populate_values(template) == expected
