"""Policy related tests."""

import pytest
import mock
import balrog


def test_create(policy, policy_roles):
    """Test policy creation."""
    assert policy.roles == dict((role.name, role) for role in policy_roles)


def test_role_name_is_unique(role, get_role, get_identity):
    """Test that roles are registered with unique name."""
    with pytest.raises(AssertionError):
        balrog.Policy(
            roles=(
                role,
                role,
            ),
            get_role=get_role,
            get_identity=get_identity,
        )


def test_check(policy, permission_name, identity):
    """Test Policy.check."""
    with mock.patch.object(balrog.Role, 'check') as mock_check:
        mock_check.return_value = True
        assert policy.check(permission_name, 1, 2, 3, a=1, b=2, c=3)
        mock_check.assert_called_once_with(identity, permission_name, 1, 2, 3, a=1, b=2, c=3)


@pytest.mark.parametrize(
    'name',
    (
        'unknown',
        None,
        -1,
    ),
)
def test_check_role_not_found(policy, identity, permission_name, name):
    """Test Policy.check is False when permission is not found."""
    assert name != permission_name
    assert not policy.check(identity, name)


def test_filter(policy, identity, permission_name, objects):
    """Test Policy.filter bypasses the objects by default."""
    with mock.patch.object(balrog.Role, 'filter') as mock_filter:
        mock_filter.return_value = objects
        # None is passed here for default explicitly in order the call args to match
        assert policy.filter(permission_name, objects, 1, 2, 3, a=1, b=2, c=3) == objects
        mock_filter.assert_called_once_with(identity, permission_name, objects, 1, 2, 3, a=1, b=2, c=3)


def test_filter_without_permission(policy, identity, permission_name, objects):
    """Test Policy.filter raises an exception when not allowed."""
    with pytest.raises(balrog.PermissionNotFound):
        policy.filter('unknown', objects)


def test_get_role(policy, identity):
    """Test get_role raises an exception for unknown role name."""
    with pytest.raises(balrog.RoleNotFound):
        with mock.patch.object(policy, '_get_role') as mock_get_role:
            mock_get_role.return_value = 'unknown'
            policy.get_role(identity)
